from app.models.schemas import SubjectInsert, AdminEdit
from app.models.models import Admin, Subject, Student, Teacher
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
        except IntegrityError:
            db.rollback()
            raise ValueError(f"Subject with name '{subject.subject_name}' already exists!")
        
        db.refresh(db_subject)
        return db_subject


    def admin_list_students(self, token: str) -> list[Student]:
        db = self._db
        
        result = check_access_token(token)
        
        if not result:
            raise ValueError("Invalid credentials!")
        
        if result.get("role") != "Admin":
            raise ValueError("You don't have the permission to perform this action!")
        
        
        query = db.query(Student)
        
        students = query.all()
        
        return students


    def admin_list_teachers(self, token: str) -> list[Teacher]:
        db = self._db
        
        result = check_access_token(token)
        
        if not result:
            raise ValueError("Invalid credentials!")
        
        if result.get("role") != "Admin":
            raise ValueError("You don't have the permission to perform this action!")
        
        
        query = db.query(Teacher).options(selectinload(Teacher.subjects))
        
        teachers = query.all()
        
        return teachers


    def admin_list_subjects(self, token: str) -> list[Subject]:
        db = self._db
        
        result = check_access_token(token)
        
        if not result:
            raise ValueError("Invalid credentials!")
        
        if result.get("role") != "Admin":
            raise ValueError("You don't have the permission to perform this action!")
        
        
        query = db.query(Subject).options(joinedload(Subject.teacher))
        
        subjects = query.all()
        
        return subjects


    def admin_assign_subject_to_teacher(self, token, subject_id, teacher_id):
        db = self._db
        
        result = check_access_token(token)
        
        if not result:
            raise ValueError("Invalid credentials!")
        
        if result.get("role") != "Admin":
            raise ValueError("You don't have the permission to perform this action!")
        
        
        query = db.query(Subject).filter(Subject.id == subject_id).options(joinedload(Subject.teacher))
        
        subject = query.first()
        
        if not subject:
            raise ValueError(f"No subject with id '{subject_id}' found!")
        
        if subject.teacher:
            raise ValueError(f"Subject with id '{subject_id}' is already assigned to {subject.teacher.name} with id '{subject.teacher_id}'!")
        
        
        query = db.query(Teacher).filter(Teacher.id == teacher_id)
        
        teacher = query.first()
        
        if not teacher:
            raise ValueError(f"No teacher with id '{teacher_id}' found!")
        
        subject.teacher_id = teacher_id
        db.add(subject)
        db.commit()
        
        return {"status": "Completed", "detail": f"{subject.subject_name} has been assigned to {teacher.name}!"}


    def admin_modify_profile(self, token: str, data: AdminEdit) -> Admin:
        db = self._db
        
        result = check_access_token(token)
        
        if not result:
            raise ValueError("Invalid credentials!")
        
        if result.get("role") != "Admin":
            raise ValueError("Unexpected role!")
        
        query = db.query(Admin).filter(Admin.email == result.get("sub"))
        db_admin = query.first()
        
        if not db_admin:
            raise ValueError("Admin doesn't exist!")
        
        
        if data.username:
            db_admin.username = data.username
        
        if data.email:
            db_admin.email = data.email
        
        db.add(db_admin)
        db.commit()
        db.refresh(db_admin)
        
        return db_admin