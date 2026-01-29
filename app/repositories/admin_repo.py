from app.models.schemas import SubjectInsert, AdminEdit
from app.models.models import Admin, Subject, Student, Teacher
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError


class AdminRepository:
    def __init__(self, session: AsyncSession):
        self._db = session

    async def admin_add_subject(self, subject: SubjectInsert):
        db = self._db
        
        db_subject = Subject(subject_name = subject.subject_name, teacher_id = subject.teacher_id)
                
        try:
            db.add(db_subject)
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise ValueError(f"Subject with name '{subject.subject_name}' already exists!")
        
        await db.refresh(db_subject)
        return db_subject


    async def admin_list_students(self, skip: int, limit: int) -> list[Student]:
        db = self._db
        
        query = select(Student).limit(limit).offset(skip)
                
        result = await db.execute(query)
    
        students = result.scalars().all()
        
        return students


    async def admin_list_teachers(self, skip: int, limit: int) -> list[Teacher]:
        db = self._db
                
        query = select(Teacher).options(selectinload(Teacher.subjects)).limit(limit).offset(skip)
                
        result = await db.execute(query)
    
        teachers = result.scalars().all()
        
        return teachers


    async def admin_list_subjects(self, skip: int, limit: int) -> list[Subject]:
        db = self._db
                
        query = select(Subject).options(joinedload(Subject.teacher)).limit(limit).offset(skip)
                
        result = await db.execute(query)
    
        subjects = result.scalars().all()
        
        return subjects


    async def admin_assign_subject_to_teacher(self, subject_id: int, teacher_id: int):
        db = self._db
                
        query = select(Subject).where(Subject.id == subject_id).options(joinedload(Subject.teacher))
                
        result = await db.execute(query)
    
        subject = result.scalars().first()
        
        if not subject:
            raise ValueError(f"No subject with id '{subject_id}' found!")
        
        if subject.teacher:
            raise ValueError(f"Subject with id '{subject_id}' is already assigned to {subject.teacher.name} with id '{subject.teacher_id}'!")
                
        query = select(Teacher).where(Teacher.id == teacher_id)
                
        result = await db.execute(query)
    
        teacher = result.scalars().first()
        
        if not teacher:
            raise ValueError(f"No teacher with id '{teacher_id}' found!")
        
        subject.teacher_id = teacher_id
        db.add(subject)
        await db.commit()
        
        return {"status": "Completed", "detail": f"{subject.subject_name} has been assigned to {teacher.name}!"}


    async def admin_modify_profile(self, current_admin: Admin, data: AdminEdit) -> Admin:
        db = self._db
                
        if data.username:
            current_admin.username = data.username
        
        if data.email:
            current_admin.email = data.email
        
        db.add(current_admin)
        await db.commit()
        await db.refresh(current_admin)
        
        return current_admin


    async def admin_approve_user(self, user_id: int, role: str):
        db = self._db
        
        match role:
            case "Teacher":
                query = select(Teacher).where(Teacher.id == user_id)
                
                result = await db.execute(query)
            case "Student":
                query = select(Student).where(Student.id == user_id)
                
                result = await db.execute(query)
        
        if not result:
            raise ValueError(f"{role} account with id '{user_id}' doesn't exist!")
        
        db_user = result.scalars().first()
                
        if db_user.approved:
            raise ValueError(f"{role} account with id '{user_id}' was already activated!")
        
        db_user.approved = True
        
        db.add(db_user)
        await db.commit()
        
        return {"status": "Completed", "detail": f"{role} account with id '{user_id}' has been activated!"}


    async def admin_disapprove_user(self, user_id: int, role: str):
        db = self._db
        
        match role:
            case "Teacher":
                query = select(Teacher).where(Teacher.id == user_id)
                
                result = await db.execute(query)
            case "Student":
                query = select(Student).where(Student.id == user_id)
                
                result = await db.execute(query)
        
        if not result:
            raise ValueError(f"{role} account with id '{user_id}' doesn't exist!")
        
        db_user = result.scalars().first()
                
        if not db_user.approved:
            raise ValueError(f"{role} account with id '{user_id}' was already disactivated or has not been activated yet!")
        
        db_user.approved = False
        
        db.add(db_user)
        await db.commit()
        
        return {"status": "Completed", "detail": f"{role} account with id '{user_id}' has been disactivated!"}