from app.models.schemas import GradeInsert, TeacherEdit
from app.models.models import Teacher, Student, Grade, Subject
from app.core.security import password_hashing, check_access_token, create_access_token, create_refresh_token, check_refresh_token
from sqlalchemy.orm import Session, joinedload, selectinload


class TeacherRepository:
    def __init__(self, session: Session):
        self._db = session

    def teacher_grade_student(self, token, grade: GradeInsert):
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
        
        if not grade.subject in [subj.subject_name for subj in subjects]:
            raise ValueError(f"{db_teacher.name} doesn't teach {grade.subject}!")
        
        
        query = db.query(Student).filter(Student.id == grade.student_id).options(selectinload(Student.grades).joinedload(Grade.subject))
        db_student = query.first()
        
        if not db_student:
            raise ValueError(f"Student with id '{grade.student_id}' doesn't exist!")
        
        db_student_grades = [grd for grd in db_student.grades if grade.subject == grd.subject.subject_name]
        
        if db_student_grades:
            if grade.number in [grd.number for grd in db_student_grades]:
                raise ValueError("Grade already exists!")
            
            sub_id = db_student_grades[0].subject_id
            
        else:
            query = db.query(Subject).filter(Subject.subject_name == grade.subject)
            db_subject = query.first()
            
            if not db_subject:
                raise ValueError(f"{grade.subject} doesn't exist!")
            
            sub_id = db_subject.id
        
        db_grade = Grade(value = grade.value, number = grade.number, subject_id = sub_id, student_id = grade.student_id)
        
        db.add(db_grade)
        db.commit()
        
        return {"student": db_student, "subject": grade.subject, "value": grade.value, "number": grade.number}
        # or return {"student": {"id": int, "name": str, "email": str, "school_year": int}, "subject": subject, "value": grade.value, "number": grade.number}


    def teacher_edit_grade(self, token, grade: GradeInsert):
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
        
        if not grade.subject in [subj.subject_name for subj in subjects]:
            raise ValueError(f"{db_teacher.name} doesn't teach {grade.subject}!")
        
        
        query = db.query(Student).filter(Student.id == grade.student_id).options(selectinload(Student.grades).joinedload(Grade.subject))
        db_student = query.first()
        
        if not db_student:
            raise ValueError(f"Student with id '{grade.student_id}' doesn't exist!")
        
        db_student_grades = [grd for grd in db_student.grades if grade.subject == grd.subject.subject_name]
        
        db_grade = [grd for grd in db_student_grades if grd.number == grade.number][0]
        
        if not db_grade:
            raise ValueError("Grade doesn't exists!")
        
        query = db.query(Subject).filter(Subject.subject_name == grade.subject)
        db_subject = query.first()
        
        if not db_subject:
            raise ValueError("Subject doesn't exists!")
        
        db_grade.value = grade.value
        db_grade.number = grade.number
        
        db.add(db_grade)
        db.commit()
        
        return {"student": db_student, "subject": grade.subject, "value": grade.value, "number": grade.number}


    def teacher_modify_profile(self, token: str, data: TeacherEdit) -> Teacher:
        db = self._db
        
        result = check_access_token(token)
        
        if not result:
            raise ValueError("Invalid credentials!")
        
        if result.get("role") != "Teacher":
            raise ValueError("Unexpected role!")
        
        query = db.query(Teacher).filter(Teacher.email == result.get("sub"))
        db_teacher = query.first()
        
        if not db_teacher:
            raise ValueError("Teacher doesn't exist!")
        
        
        if data.name:
            db_teacher.name = data.name
        
        if data.email:
            db_teacher.email = data.email
        
        db.add(db_teacher)
        db.commit()
        db.refresh(db_teacher)
        
        return db_teacher