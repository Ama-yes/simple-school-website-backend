from app.db.database import localSession
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from app.core.security import check_access_token
from sqlalchemy.orm import Session
from app.models.models import Student, Admin, Teacher



admin_oauth2 = OAuth2PasswordBearer("/admin/login")
student_oauth2 = OAuth2PasswordBearer("/student/login")
teacher_oauth2 = OAuth2PasswordBearer("/teacher/login")


def get_database():
    db = localSession()
    try:
        yield db
    finally:
        db.close()


def get_current_student(token: str = Depends(student_oauth2), db: Session = Depends(get_database)):
    result = check_access_token(token)
        
    if not result:
        raise ValueError("Invalid credentials!")
        
    if result.get("role") != "Student":
        raise ValueError("Unexpected role!")
        
    email = result["sub"]
        
    query = db.query(Student).filter(Student.email == email)
    
    db_student = query.first()
        
    if not db_student:
        raise ValueError("Invalid credentials!")
    
    return db_student


def get_current_teacher(token: str = Depends(teacher_oauth2), db: Session = Depends(get_database)):
    result = check_access_token(token)
        
    if not result:
        raise ValueError("Invalid credentials!")
        
    if result.get("role") != "Teacher":
        raise ValueError("Unexpected role!")
        
    email = result["sub"]
        
    query = db.query(Teacher).filter(Teacher.email == email)
    
    db_teacher = query.first()
        
    if not db_teacher:
        raise ValueError("Invalid credentials!")
    
    return db_teacher


def get_current_admin(token: str = Depends(admin_oauth2), db: Session = Depends(get_database)):
    result = check_access_token(token)
        
    if not result:
        raise ValueError("Invalid credentials!")
        
    if result.get("role") != "Admin":
        raise ValueError("Unexpected role!") # or ValueError("You don't have the permission to perform this action!")
        
    email = result["sub"]
        
    query = db.query(Admin).filter(Admin.email == email)
    
    db_admin = query.first()
        
    if not db_admin:
        raise ValueError("Invalid credentials!")
    
    return db_admin