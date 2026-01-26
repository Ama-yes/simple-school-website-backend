from app.models.schemas import GradeForStd
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