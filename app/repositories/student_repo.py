from app.models.schemas import StudentLoggingIn, StudentSigningIn
from app.models.models import Student
from app.core.security import password_hashing, check_password, create_access_token, create_refresh_token, check_refresh_token
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.exc import IntegrityError
from app.worker.tasks import send_email


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
            raise ValueError("Student doesn't exist!")
        
        result = send_email.apply_async(args=(db_student.name, email, "Click here to reset your password!"), expires=30, countdown=5)
        return result