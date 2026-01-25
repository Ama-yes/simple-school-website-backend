from app.models.schemas import StudentLoggingIn, StudentSigningIn
from app.models.models import Student
from app.core.config import settings
from app.core.security import password_hashing, check_password, create_access_token, create_refresh_token, check_refresh_token
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.exc import IntegrityError
from app.worker.tasks import send_email
from datetime import datetime, timedelta
import uuid


class StudentRepository:
    def __init__(self, session: Session):
        self._db = session
    
    def student_verify_refresh_token(self, token) -> Student:
        result = check_refresh_token(token)
        
        if not result:
            raise ValueError("Invalid credentials!")
        
        if not result.get("version"):
            raise ValueError("Invalid token type!")
        
        if result.get("role") != "Student":
            raise ValueError("Unexpected role!")
        
        email = result["sub"]
        token_v = result["version"]
        
        db = self._db
        query = db.query(Student).filter(Student.email == email)
        
        db_student = query.first()
        
        if not db_student:
            raise ValueError("Invalid credentials!")
        
        if db_student.token_version != token_v:
            raise ValueError("Invalid token version!")
        
        return db_student
        
        
    def student_change_password(self, new_password: str, token: str):
        db = self._db
        db_student = self.student_verify_refresh_token(token)
        
        db_student.token_version += 1
        db_student.hashed_password = password_hashing(password=new_password) 
        db.add(db_student)
        db.commit()
        db.refresh(db_student)
        
        return {"status": "Completed", "detail": "Log back in necessary!"}
    
    
    def student_token_refresh(self, token: str):
        db_student = self.student_verify_refresh_token(token)
        
        access_token = create_access_token({"sub": db_student.email, "role": "Student"})
        
        return {"access_token": access_token, "token_type": "bearer", "refresh_token": token}
    
    
    def student_reset_password(self, email: str):
        db = self._db
        
        query = db.query(Student).filter(Student.email == email)
        db_student = query.first()
        
        if not db_student:
            raise ValueError(f"{email} is not linked to any account!")
        
        reset_token = str(uuid.uuid4())
        
        db_student.reset_token = reset_token
        db_student.reset_token_expire = datetime.now() + timedelta(minutes=15)
        
        db.commit()
        
        link = f"{settings.hostname}/student/password-resetting/{reset_token}"
        
        send_email.apply_async(args=(email, f"Hey {db_student.name},\nClick below to reset your password:\n{link}\nNOTE: THIS ISN'T A CLICKABLE LINK, YOU SHOULD SENT A POST REQUEST TO IT WITH YOUR EMAIL!", "Password Reset Request"), expires=30, countdown=5)
        return "Email sent in the backgroud!"
    
    
    def student_verify_reset_token(self, token: str, password: str):
        db = self._db
        
        query = db.query(Student).filter(Student.reset_token == token)
        db_student = query.first()
        
        if not db_student or db_student.reset_token_expire < datetime.now():
            raise ValueError("Invalid link!")
        
        
        db_student.token_version += 1
        db_student.hashed_password = password_hashing(password) 
        db_student.reset_token = None
        db_student.reset_token_expire = None
        db.add(db_student)
        db.commit()
        
        return {"status": "Completed", "detail": "Log back in necessary!"}