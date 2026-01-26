from app.models.schemas import GradeForStd, StudentEdit
from app.models.models import Student, Grade, Subject
from app.core.security import password_hashing, check_access_token, create_access_token, create_refresh_token, check_refresh_token
from sqlalchemy.orm import Session, joinedload, selectinload


class StudentRepository:
    def __init__(self, session: Session):
        self._db = session

    def student_grades_check(self, token: str) -> list[GradeForStd]:
        db = self._db
        
        result = check_access_token(token)
        
        if not result:
            raise ValueError("Invalid credentials!")
        
        if result.get("role") != "Student":
            raise ValueError("Unexpected role!")
        
        query = db.query(Student).filter(Student.email == result.get("sub")).options(selectinload(Student.grades).joinedload(Grade.subject).joinedload(Subject.teacher))
        db_student = query.first()
        
        if not db_student:
            raise ValueError("Student doesn't exist!")
        
        return db_student.grades


    def student_modify_profile(self, token: str, data: StudentEdit) -> Student:
        db = self._db
        
        result = check_access_token(token)
        
        if not result:
            raise ValueError("Invalid credentials!")
        
        if result.get("role") != "Student":
            raise ValueError("Unexpected role!")
        
        query = db.query(Student).filter(Student.email == result.get("sub"))
        db_student = query.first()
        
        if not db_student:
            raise ValueError("Student doesn't exist!")
        
        
        if data.name:
            db_student.name = data.name
        
        if data.email:
            db_student.email = data.email
        
        if data.school_year:
            db_student.school_year = data.school_year
        
        db.add(db_student)
        db.commit()
        db.refresh(db_student)
        
        return db_student