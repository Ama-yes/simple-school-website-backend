from app.core.security import password_hashing, check_password, create_access_token, create_refresh_token, check_refresh_token, check_access_token
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.schemas import AdminLoggingIn, AdminSigningIn, StudentLoggingIn, StudentSigningIn, TeacherLoggingIn, TeacherSigningIn, ConfirmPassword
from app.models.models import Admin, Teacher, Student
from app.core.config import settings
from app.worker.tasks import send_email
from datetime import datetime, timedelta
import uuid




class AuthRepository:
    def __init__(self, session: Session, role: str):
        self._db = session
        self._role = role
    
    
    def signin(self, data: AdminSigningIn | StudentSigningIn | TeacherSigningIn):
        db = self._db
        role = self._role
        
        match role:
            case "Teacher":
                user = Teacher(name=data.name, email=data.email, hashed_password=password_hashing(data.password), token_version=1)
            case "Student":
                user = Student(name=data.name, email=data.email, hashed_password=password_hashing(data.password), school_year=data.school_year, token_version=1)
            case "Admin":
                user = Admin(username=data.username, email=data.email, hashed_password=password_hashing(data.password), token_version=1)
        
        try:
            db.add(user)
            db.commit()
        except IntegrityError:
            db.rollback()
            raise ValueError(f"{role} already exists!")
        
        return {"status": "Completed", "detail": "Sign in successful!"}
    
    
    def login(self, user: AdminLoggingIn | StudentLoggingIn | TeacherLoggingIn):
        db = self._db
        role = self._role
        
        match role:
            case "Teacher":
                query = db.query(Teacher).filter(Teacher.email == user.email)
            case "Student":
                query = db.query(Student).filter(Student.email == user.email)
            case "Admin":
                query = db.query(Admin).filter(Admin.username == user.username)
        
        
        db_user = query.first()
        
        if not db_user or not check_password(plain_password=user.password, hashed_password=db_user.hashed_password):
            raise ValueError("Email or password incorrect!")
        
        if role != "Admin" and not db_user.approved:
            raise ValueError("Account locked or not yet approved by an admin!")
        
        access_token = create_access_token({"sub": db_user.email, "role": role})
        refresh_token = create_refresh_token({"sub": db_user.email, "version": db_user.token_version, "role": role})
        
        return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}


    def verify_refresh_token(self, token) -> Student | Admin | Teacher:
        role = self._role
        
        result = check_refresh_token(token)
        
        if not result:
            raise ValueError("Invalid credentials!")
        
        if not result.get("version"):
            raise ValueError("Invalid token type!")
        
        if result.get("role") != role:
            raise ValueError("Unexpected role!")
        
        email = result["sub"]
        token_v = result["version"]
        
        db = self._db
        
        match role:
            case "Teacher":
                query = db.query(Teacher).filter(Teacher.email == email)
            case "Student":
                query = db.query(Student).filter(Student.email == email)
            case "Admin":
                query = db.query(Admin).filter(Admin.email == email)
        
        db_user = query.first()
        
        if not db_user:
            raise ValueError("Invalid credentials!")
        
        if db_user.token_version != token_v:
            raise ValueError("Invalid token version!")
        
        return db_user
        
        
    def change_password(self, new_psswrd: ConfirmPassword, token: str):
        db = self._db
        db_user = self.verify_refresh_token(token)
        
        db_user.token_version += 1
        db_user.hashed_password = password_hashing(password=new_psswrd.password) 
        db.add(db_user)
        db.commit()
        
        return {"status": "Completed", "detail": "Log back in necessary!"}
    
    
    def token_refresh(self, token: str):
        role = self._role
        
        db_user = self.verify_refresh_token(token)
        
        access_token = create_access_token({"sub": db_user.email, "role": role})
        
        return {"access_token": access_token, "token_type": "bearer", "refresh_token": token}
    
    
    def reset_password(self, email: str):
        db = self._db
        role = self._role
        
        match role:
            case "Teacher":
                query = db.query(Teacher).filter(Teacher.email == email)
            case "Student":
                query = db.query(Student).filter(Student.email == email)
            case "Admin":
                query = db.query(Admin).filter(Admin.email == email)
        
        db_user = query.first()
        
        if not db_user:
            raise ValueError(f"{email} is not linked to any account!")
        
        reset_token = str(uuid.uuid4())
        
        db_user.reset_token = reset_token
        db_user.reset_token_expire = datetime.now() + timedelta(minutes=15)
        
        db.commit()
        
        link = f"{settings.hostname}/{role.lower()}/password-resetting/{reset_token}"
        
        send_email.apply_async(args=(email, f"Hey {db_user.username if role == 'Admin' else db_user.name},\nClick below to reset your password:\n{link}\nNOTE: THIS ISN'T A CLICKABLE LINK, YOU SHOULD SEND A 'POST' REQUEST TO IT INCLUDING THE NEW PASSWORD!", "Password Reset Request"), expires=600, countdown=5)
        
        return {"status": "Completed", "detail": "Email sent in the backgroud!"}
    
    
    def verify_token_reset_psswrd(self, token: str, psswrd: ConfirmPassword):
        db = self._db
        role = self._role
        
        match role:
            case "Teacher":
                query = db.query(Teacher).filter(Teacher.reset_token == token)
            case "Student":
                query = db.query(Student).filter(Student.reset_token == token)
            case "Admin":
                query = db.query(Admin).filter(Admin.reset_token == token)
        
        db_user = query.first()
        
        if not db_user or db_user.reset_token_expire < datetime.now():
            raise ValueError("Invalid link!")
        
        db_user.token_version += 1
        db_user.hashed_password = password_hashing(psswrd.password) 
        db_user.reset_token = None
        db_user.reset_token_expire = None
        db.add(db_user)
        db.commit()
        
        return {"status": "Completed", "detail": "Log back in necessary!"}
    
    
    def delete_user(self, token: str, todelete_id = None, user_type = None):
        role = self._role
        
        result = check_access_token(token)
        
        if not result:
            raise ValueError("Invalid credentials!")
        
        if result.get("role") != role:
            raise ValueError("Unexpected role!")
        
        if role != "Admin" and todelete_id:
            raise ValueError("Insufficient permissions!")
        
        email = result["sub"]
        
        db = self._db
        
        match role:
            case "Teacher":
                query = db.query(Teacher).filter(Teacher.email == email)
            case "Student":
                query = db.query(Student).filter(Student.email == email)
            case "Admin":
                if not todelete_id:
                    query = db.query(Admin).filter(Admin.email == email)
                
                elif user_type == "Teacher":
                    query = db.query(Teacher).filter(Teacher.id == todelete_id)
                
                elif user_type == "Student":
                    query = db.query(Student).filter(Student.id == todelete_id)
        
        
        db_user = query.first()
        
        if not db_user:
            raise ValueError(f"{user_type if user_type else role} doesn't exist!")
        
        
        db.delete(db_user)
        db.commit()
        
        return {"status": "Completed", "detail": "Deletion successful!"}
