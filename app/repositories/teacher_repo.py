from app.models.schemas import GradeInsert, TeacherSigningIn
from app.models.models import Teacher, Student, Grade, Subject
from app.core.config import settings
from app.core.security import password_hashing, check_access_token, create_access_token, create_refresh_token, check_refresh_token
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.exc import IntegrityError
from app.worker.tasks import send_email
from datetime import datetime, timedelta
import uuid


class TeacherRepository:
    def __init__(self, session: Session):
        self._db = session
    
    def teacher_verify_refresh_token(self, token) -> Teacher:
        result = check_refresh_token(token)
        
        if not result:
            raise ValueError("Invalid credentials!")
        
        if not result.get("version"):
            raise ValueError("Invalid token type!")
        
        if result.get("role") != "Teacher":
            raise ValueError("Unexpected role!")
        
        email = result["sub"]
        token_v = result["version"]
        
        db = self._db
        query = db.query(Teacher).filter(Teacher.email == email)
        
        db_teacher = query.first()
        
        if not db_teacher:
            raise ValueError("Invalid credentials!")
        
        if db_teacher.token_version != token_v:
            raise ValueError("Invalid token version!")
        
        return db_teacher
        
    
    def teacher_change_password(self, new_password: str, token: str):
        db = self._db
        db_teacher = self.teacher_verify_refresh_token(token)
        
        db_teacher.token_version += 1
        db_teacher.hashed_password = password_hashing(password=new_password) 
        db.add(db_teacher)
        db.commit()
        db.refresh(db_teacher)
        
        return {"status": "Completed", "detail": "Log back in necessary!"}
    
    
    def teacher_token_refresh(self, token: str):
        db_teacher = self.teacher_verify_refresh_token(token)
        
        access_token = create_access_token({"sub": db_teacher.email, "role": "Teacher"})
        
        return {"access_token": access_token, "token_type": "bearer", "refresh_token": token}
    
    
    def teacher_reset_password(self, email: str):
        db = self._db
        
        query = db.query(Teacher).filter(Teacher.email == email)
        db_teacher = query.first()
        
        if not db_teacher:
            raise ValueError(f"{email} is not linked to any account!")
        
        reset_token = str(uuid.uuid4())
        
        db_teacher.reset_token = reset_token
        db_teacher.reset_token_expire = datetime.now() + timedelta(minutes=15)
        
        db.commit()
        
        link = f"{settings.hostname}/teacher/password-resetting/{reset_token}"
        
        send_email.apply_async(args=(email, f"Hey {db_teacher.name},\nClick below to reset your password:\n{link}\nNOTE: THIS ISN'T A CLICKABLE LINK, YOU SHOULD SEND A 'POST' REQUEST TO IT INCLUDING THE NEW PASSWORD!", "Password Reset Request"), expires=30, countdown=5)
        
        return {"status": "Completed", "detail": "Email sent in the backgroud!"}
    
    
    def teacher_verify_reset_token(self, token: str, password: str):
        db = self._db
        
        query = db.query(Teacher).filter(Teacher.reset_token == token)
        db_teacher = query.first()
        
        if not db_teacher or db_teacher.reset_token_expire < datetime.now():
            raise ValueError("Invalid link!")
        
        
        db_teacher.token_version += 1
        db_teacher.hashed_password = password_hashing(password) 
        db_teacher.reset_token = None
        db_teacher.reset_token_expire = None
        db.add(db_teacher)
        db.commit()
        
        return {"status": "Completed", "detail": "Log back in necessary!"}
    
    
    def teacher_grade_student(self, token, student_id, subject: str, grade: GradeInsert):
        db = self._db
        
        result = check_access_token(token)
        
        if not result:
            raise ValueError("Invalid credentials!")
        
        if result.get("role") != "Teacher":
            raise ValueError("You don't have the permission to perform this action!")
        
        
        query = db.query(Teacher).filter(Teacher.email == result.get("sub")).options(selectinload(Teacher.subjects))
        db_teacher = query.first()
        
        if not db_teacher:
            raise ValueError("Teacher doesn't exist!")
        
        if db_teacher.subjects:
            subjects = db_teacher.subjects
        else:
            raise ValueError(f"{db_teacher.name} has no subjects assigned!")
        
        if not subject in [subj.subject_name for subj in subjects]:
            raise ValueError(f"{db_teacher.name} doesn't teach {subject}!")
        
        
        query = db.query(Student).filter(Student.id == student_id).options(selectinload(Student.grades).joinedload(Grade.subject))
        db_student = query.first()
        
        if not db_student:
            raise ValueError(f"Student with id '{student_id}' doesn't exist!")
        
        db_student_grades = [grd for grd in db_student.grades if subject == grd.subject.subject_name]
        
        if db_student_grades:
            if grade.number in [grd.number for grd in db_student_grades]:
                raise ValueError("Grade already exists!")
            
            sub_id = db_student_grades[0].subject_id
            
        else:
            query = db.query(Subject).filter(Subject.subject_name == subject)
            db_subject = query.first()
            
            if not db_subject:
                raise ValueError(f"{subject} doesn't exist!")
            
            sub_id = db_subject.id
        
        db_grade = Grade(value = grade.value, number = grade.number, subject_id = sub_id, student_id = student_id)
        
        db.add(db_grade)
        db.commit()
        
        return {"student": db_student, "value": grade.value, "number": grade.number}
        # or return {"student": {"id": int, "name": str, "email": str, "school_year": int}, "value": grade.value, "number": grade.number}