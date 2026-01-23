from app.models.schemas import StudentLoggingIn, StudentSigningIn
from app.models.models import Student
from app.core.security import password_hashing, check_password, create_access_token, create_refresh_token, check_token
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.exc import IntegrityError


class StudentRepository:
    def __init__(self, session: Session):
        self._db = session
    
    def student_signin(self, student: StudentSigningIn):
        db = self._db
        student = Student(name=student.name, email=student.email, hashed_password=password_hashing(student.password), token_version=1)
        
        try:
            db.add(student)
            db.commit()
        except IntegrityError:
            db.rollback()
            raise ValueError("Student already exists!")
        
        db.refresh(student)
        
        access_token = create_access_token({"sub": student.email, "role": "student"})
        refresh_token = create_refresh_token({"sub": student.email, "version": student.token_version, "role": "student"})
        
        return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}
    
    
    def student_login(self, student: StudentLoggingIn):
        db = self._db
        query = db.query(Student).filter(Student.email == student.email)
        
        db_student = query.first()
        
        if not db_student or not check_password(plain_password=student.password, hashed_password=db_student.hashed_password):
            raise ValueError("Email or password incorrect!")
        
        access_token = create_access_token({"sub": student.email, "role": "student"})
        refresh_token = create_refresh_token({"sub": student.email, "version": db_student.token_version, "role": "student"})
        
        return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}
    
    
    def student_verify_refresh_token(self, token) -> Student:
        result = check_token(token)
        
        if not result:
            raise ValueError("Invalid credentials!")
        
        if not result.get("version"):
            raise ValueError("Invalid token type!")
        
        if result.get("role") != "student":
            raise ValueError("Unexpected role!")
        
        email = result["sub"]
        token_v = result["version"]
        
        db = self._db
        query = db.query(Student).filter(Student.email == email)
        
        db_student = query.first()
        
        if not db_student:
            raise ValueError("Student doesn't exist!")
        
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
        
        access_token = create_access_token({"sub": db_student.email, "role": "student"})
        
        return {"access_token": access_token, "token_type": "bearer", "refresh_token": token}