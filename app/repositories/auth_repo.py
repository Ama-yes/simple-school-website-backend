from app.core.security import password_hashing, check_password, create_access_token, create_refresh_token
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.schemas import AdminLoggingIn, AdminSigningIn, StudentLoggingIn, StudentSigningIn, TeacherLoggingIn, TeacherSigningIn
from app.models.models import Admin, Teacher, Student





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
        
        db.refresh(user)
        
        access_token = create_access_token({"sub": user.email, "role": role})
        refresh_token = create_refresh_token({"sub": user.email, "version": user.token_version, "role": role})
        
        return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}
    
    
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
        
        access_token = create_access_token({"sub": db_user.email, "role": role})
        refresh_token = create_refresh_token({"sub": db_user.email, "version": db_user.token_version, "role": role})
        
        return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}
