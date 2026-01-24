from app.models.schemas import TeacherLoggingIn, TeacherSigningIn
from app.models.models import Teacher
from app.core.security import password_hashing, check_password, create_access_token, create_refresh_token, check_refresh_token
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.exc import IntegrityError
from app.worker.tasks import send_email


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
            raise ValueError("Teacher doesn't exist!")
        
        result = send_email.apply_async(args=(db_teacher.name, email, "Click here to reset your password!"), expires=30, countdown=5)
        return result