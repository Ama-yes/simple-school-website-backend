from app.models.schemas import StudentEdit
from app.models.models import Student, Grade
from sqlalchemy.orm import Session, selectinload, joinedload


class StudentRepository:
    def __init__(self, session: Session):
        self._db = session

    def student_modify_profile(self, current_student: Student, data: StudentEdit) -> Student:
        db = self._db
        
        if data.name:
            current_student.name = data.name
        
        if data.email:
            current_student.email = data.email
        
        if data.school_year:
            current_student.school_year = data.school_year
        
        db.add(current_student)
        db.commit()
        db.refresh(current_student)
        
        return current_student
    
    
    def student_grades_check(self, current_student: Student) -> list[Grade]:
        db = self._db
        
        query = db.query(Grade).filter(Grade.student_id == current_student.id).options(joinedload(Grade.subject))
        
        db_grades = query.all()
        
        return db_grades