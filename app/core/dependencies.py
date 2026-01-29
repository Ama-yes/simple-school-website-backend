from app.db.database import localSession
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from app.core.security import check_access_token
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Student, Admin, Teacher



admin_oauth2 = OAuth2PasswordBearer("/admin/login")
student_oauth2 = OAuth2PasswordBearer("/student/login")
teacher_oauth2 = OAuth2PasswordBearer("/teacher/login")


async def get_database():
    async with localSession() as db:
        yield db


async def get_current_student(token: str = Depends(student_oauth2), db: AsyncSession = Depends(get_database)):
    result = check_access_token(token)
        
    if not result:
        raise ValueError("Invalid credentials!")
        
    if result.get("role") != "Student":
        raise ValueError("Unexpected role!")
        
    email = result["sub"]
        
    query = select(Student).where(Student.email == email)
        
    result = await db.execute(query)
    
    db_student = result.scalars().first()
        
    if not db_student:
        raise ValueError("Invalid credentials!")
    
    return db_student


async def get_current_teacher(token: str = Depends(teacher_oauth2), db: AsyncSession = Depends(get_database)):
    result = check_access_token(token)
        
    if not result:
        raise ValueError("Invalid credentials!")
        
    if result.get("role") != "Teacher":
        raise ValueError("Unexpected role!")
        
    email = result["sub"]
        
    query = select(Teacher).where(Teacher.email == email)
        
    result = await db.execute(query)
    
    db_teacher = result.scalars().first()
        
    if not db_teacher:
        raise ValueError("Invalid credentials!")
    
    return db_teacher


async def get_current_admin(token: str = Depends(admin_oauth2), db: AsyncSession = Depends(get_database)):
    result = check_access_token(token)
        
    if not result:
        raise ValueError("Invalid credentials!")
        
    if result.get("role") != "Admin":
        raise ValueError("Unexpected role!") # or ValueError("You don't have the permission to perform this action!")
        
    email = result["sub"]
        
    query = select(Admin).where(Admin.email == email)
        
    result = await db.execute(query)
    
    db_admin = result.scalars().first()
        
    if not db_admin:
        raise ValueError("Invalid credentials!")
    
    return db_admin