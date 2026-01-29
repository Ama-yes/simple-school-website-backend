from app.models.schemas import SubjectInsert, AdminEdit
from app.models.models import Admin, Subject, Student, Teacher
from app.core.security import check_refresh_token, check_access_token, create_access_token, create_refresh_token, password_hashing
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.exc import IntegrityError


class AdminRepository:
    def __init__(self, session: Session):
        self._db = session

    def admin_add_subject(self, subject: SubjectInsert):
        db = self._db
        
        db_subject = Subject(subject_name = subject.subject_name, teacher_id = subject.teacher_id)
                
        try:
            db.add(db_subject)
            db.commit()
        except IntegrityError:
            db.rollback()
            raise ValueError(f"Subject with name '{subject.subject_name}' already exists!")
        
        db.refresh(db_subject)
        return db_subject


    def admin_list_students(self, skip: int, limit: int) -> list[Student]:
        db = self._db
                
        query = db.query(Student).limit(limit).offset(skip)
        
        students = query.all()
        
        return students


    def admin_list_teachers(self, skip: int, limit: int) -> list[Teacher]:
        db = self._db
                
        query = db.query(Teacher).options(selectinload(Teacher.subjects)).limit(limit).offset(skip)
        
        teachers = query.all()
        
        return teachers


    def admin_list_subjects(self, skip: int, limit: int) -> list[Subject]:
        db = self._db
                
        query = db.query(Subject).options(joinedload(Subject.teacher)).limit(limit).offset(skip)
        
        subjects = query.all()
        
        return subjects


    def admin_assign_subject_to_teacher(self, subject_id: int, teacher_id: int):
        db = self._db
                
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


    def admin_modify_profile(self, current_admin: Admin, data: AdminEdit) -> Admin:
        db = self._db
                
        if data.username:
            current_admin.username = data.username
        
        if data.email:
            current_admin.email = data.email
        
        db.add(current_admin)
        db.commit()
        db.refresh(current_admin)
        
        return current_admin


    def admin_approve_user(self, user_id: int, role: str):
        db = self._db
        
        match role:
            case "Teacher":
                query = db.query(Teacher).filter(Teacher.id == user_id)
            case "Student":
                query = db.query(Student).filter(Student.id == user_id)
        
        db_user = query.first()
        
        if not db_user:
            raise ValueError(f"{role} account with id '{user_id}' doesn't exist!")
                
        if db_user.approved:
            raise ValueError(f"{role} account with id '{user_id}' was already activated!")
        
        db_user.approved = True
        
        db.add(db_user)
        db.commit()
        
        return {"status": "Completed", "detail": f"{role} account with id '{user_id}' has been activated!"}


    def admin_disapprove_user(self, user_id: int, role: str):
        db = self._db
        
        match role:
            case "Teacher":
                query = db.query(Teacher).filter(Teacher.id == user_id)
            case "Student":
                query = db.query(Student).filter(Student.id == user_id)
        
        db_user = query.first()
        
        if not db_user:
            raise ValueError(f"{role} account with id '{user_id}' doesn't exist!")
                
        if not db_user.approved:
            raise ValueError(f"{role} account with id '{user_id}' was already disactivated or has not been activated yet!")
        
        db_user.approved = False
        
        db.add(db_user)
        db.commit()
        
        return {"status": "Completed", "detail": f"{role} account with id '{user_id}' has been disactivated!"}