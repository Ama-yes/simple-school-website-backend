from app.models.schemas import StudentLoggedIn, StudentLoggingIn, StudentSigningIn
from app.models.models import Student
from app.core.security import password_hashing, check_password, create_access_token, create_refresh_token
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.exc import IntegrityError


class StudentRepository:
    def __init__(self, session: Session):
        self._db = session
    
    def student_signin(self, student: StudentSigningIn):
        db = self._db
        student = Student(name=student.name, email=student.email, hashed_password=password_hashing(student.password), token_version=1, grades=[])
        
        try:
            db.add(student)
            db.commit()
        except IntegrityError:
            db.rollback()
            raise ValueError("Student already exists!")
        
        db.refresh(student)
        
        return student
    
    
    def student_login(self, student: StudentLoggingIn):
        db = self._db
        query = db.query(Student).filter(Student.email == student.email)
        
        db_student = query.first()
        
        if not db_student or not check_password(plain_password=student.password, hashed_password=db_student.hashed_password):
            raise ValueError("Email or password incorrect!")
        
        db_student.token_version += 1
        
        access_token = create_access_token({"sub": student.email})
        refresh_token = create_refresh_token({"sub": student.email, "version": db_student.token_version})
        
        return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}