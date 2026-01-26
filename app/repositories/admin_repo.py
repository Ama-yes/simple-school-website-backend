from app.models.schemas import SubjectInsert
from app.models.models import Admin, Subject
from app.core.security import check_refresh_token, check_access_token, create_access_token, create_refresh_token, password_hashing
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.exc import IntegrityError


class AdminRepository:
    def __init__(self, session: Session):
        self._db = session

    def admin_add_subject(self, token: str, subject: SubjectInsert):
        db = self._db
        
        result = check_access_token(token)
        
        if not result:
            raise ValueError("Invalid credentials!")
        
        if result.get("role") != "Admin":
            raise ValueError("You don't have the permission to perform this action!")
        
        
        query = db.query(Admin).filter(Admin.email == result.get("sub"))
        db_admin = query.first()
        
        if not db_admin:
            raise ValueError("Admin doesn't exist!")
        
        db_subject = Subject(subject_name = subject.subject_name, teacher_id = subject.teacher_id)
                
        try:
            db.add(db_subject)
            db.commit()
        
            db.refresh(db_subject)
            return db_subject
        except IntegrityError:
            db.rollback()
            raise ValueError(f"Subject with name '{subject.subject_name}' already exists!")