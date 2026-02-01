from sqlalchemy import Boolean, Column, Integer, String, Float, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.database import Base



class Student(Base):
    __tablename__ = "student"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    school_year = Column(Integer, index=True)
    token_version = Column(Integer)
    grades = relationship("Grade", back_populates="student")
    reset_token = Column(String, unique=True, nullable=True)
    reset_token_expire = Column(DateTime, nullable=True)
    approved = Column(Boolean, default=False)


class Teacher(Base):
    __tablename__ = "teacher"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    token_version = Column(Integer)
    subjects = relationship("Subject", back_populates="teacher")
    reset_token = Column(String, unique=True, nullable=True)
    reset_token_expire = Column(DateTime, nullable=True)
    approved = Column(Boolean, default=False)


class Subject(Base):
    __tablename__ = "subject"
    id = Column(Integer, primary_key=True, index=True)
    subject_name = Column(String, unique=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teacher.id", ondelete="SET NULL"))
    teacher = relationship("Teacher", back_populates="subjects")
    grades = relationship("Grade", back_populates="subject")


class Grade(Base):
    __tablename__ = "grade"
    id = Column(Integer, primary_key=True, index=True)
    value = Column(Float)
    number = Column(Integer)
    subject_id = Column(Integer, ForeignKey("subject.id", ondelete="CASCADE"))
    student_id = Column(Integer, ForeignKey("student.id", ondelete="CASCADE"))
    subject = relationship("Subject", back_populates="grades")
    student = relationship("Student", back_populates="grades")
    
    __table_args__ = (UniqueConstraint("subject_id", "student_id", "number", name="unique_grade_per_subject"),)


class Admin(Base):
    __tablename__ = "admin"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    token_version = Column(Integer)
    reset_token = Column(String, unique=True, nullable=True)
    reset_token_expire = Column(DateTime, nullable=True)