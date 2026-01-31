from app.models.schemas import StudentEdit
from app.models.models import Student, Grade
from sqlalchemy.orm import joinedload
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class StudentRepository:
    def __init__(self, session: AsyncSession):
        self._db = session

    async def student_modify_profile(self, current_student: Student, data: StudentEdit) -> Student:
        db = self._db
        
        if data.name:
            current_student.name = data.name
        
        if data.email:
            current_student.email = data.email
        
        if data.school_year:
            current_student.school_year = data.school_year
        
        db.add(current_student)
        await db.commit()
        await db.refresh(current_student)
        
        return current_student
    
    
    async def student_grades_check(self, current_student: Student) -> list[Grade]:
        db = self._db
        
        query = select(Grade).where(Grade.student_id == current_student.id).options(joinedload(Grade.subject))
        
        result = await db.execute(query)
        
        db_grades = result.scalars().all()
        
        return db_grades