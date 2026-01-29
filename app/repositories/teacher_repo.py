from app.models.schemas import GradeInsert, TeacherEdit, GradeDelete
from app.models.models import Teacher, Student, Grade, Subject
from app.core.security import check_access_token
from sqlalchemy.orm import Session, selectinload


class TeacherRepository:
    def __init__(self, session: Session):
        self._db = session

    def teacher_grade_student(self, current_teacher: Teacher, grade: GradeInsert):
        db = self._db
        
        if current_teacher.subjects:
            subjects = current_teacher.subjects
        else:
            raise ValueError(f"{current_teacher.name} has no subjects assigned!")
        
        if not grade.subject in [subj.subject_name for subj in subjects]:
            raise ValueError(f"{current_teacher.name} doesn't teach {grade.subject}!")
        
        
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


    def teacher_edit_grade(self, current_teacher: Teacher, grade: GradeInsert):
        db = self._db
        
        if current_teacher.subjects:
            subjects = current_teacher.subjects
        else:
            raise ValueError(f"{current_teacher.name} has no subjects assigned!")
        
        if not grade.subject in [subj.subject_name for subj in subjects]:
            raise ValueError(f"{current_teacher.name} doesn't teach {grade.subject}!")
        
        
        query = db.query(Student).filter(Student.id == grade.student_id).options(selectinload(Student.grades).joinedload(Grade.subject))
        db_student = query.first()
        
        if not db_student:
            raise ValueError(f"Student with id '{grade.student_id}' doesn't exist!")
        
        db_student_grades = [grd for grd in db_student.grades if grade.subject == grd.subject.subject_name]
        
        if not db_student_grades:
            raise ValueError(f"Student with id '{grade.student_id}' has no grades!")
        
        db_grade = next((grd for grd in db_student_grades if grd.number == grade.number), None)
        
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


    def teacher_delete_grade(self, current_teacher: Teacher, grade: GradeDelete):
        db = self._db
        
        if current_teacher.subjects:
            subjects = current_teacher.subjects
        else:
            raise ValueError(f"{current_teacher.name} has no subjects assigned!")
        
        if not grade.subject in [subj.subject_name for subj in subjects]:
            raise ValueError(f"{current_teacher.name} doesn't teach {grade.subject}!")
        
        
        query = db.query(Student).filter(Student.id == grade.student_id).options(selectinload(Student.grades).joinedload(Grade.subject))
        db_student = query.first()
        
        if not db_student:
            raise ValueError(f"Student with id '{grade.student_id}' doesn't exist!")
        
        db_student_grades = [grd for grd in db_student.grades if grade.subject == grd.subject.subject_name]
        
        if not db_student_grades:
            raise ValueError(f"Student with id '{grade.student_id}' has no grades!")
        
        db_grade = next((grd for grd in db_student_grades if grd.number == grade.number), None)
        
        if not db_grade:
            raise ValueError("Grade doesn't exists!")
        
        db.delete(db_grade)
        db.commit()
        
        return {"status": "Completed", "detail": f"Grade number '{grade.number}' of subject '{grade.subject}' has been deleted from {db_student.name}!"}
    
    
    def teacher_list_subjects(self, current_teacher: Teacher) -> list[Subject]:
        db = self._db
        
        query = db.query(Subject).filter(Subject.teacher_id == current_teacher.id)
        
        db_subjects = query.all()
        
        return db_subjects


    def teacher_modify_profile(self, current_teacher: Teacher, data: TeacherEdit) -> Teacher:
        db = self._db
        
        if data.name:
            current_teacher.name = data.name
        
        if data.email:
            current_teacher.email = data.email
        
        db.add(current_teacher)
        db.commit()
        db.refresh(current_teacher)
        
        return current_teacher