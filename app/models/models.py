from sqlalchemy import Boolean, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.database import Base



class Student(Base):
    __tablename__ = "student"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, index=True)
    token_version = Column(Integer, index=True)
    grades = relationship("grade", back_populates="student")

class Teacher(Base):
    __tablename__ = "teacher"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, index=True)
    token_version = Column(Integer, index=True)
    subjects = relationship("subject", back_populates="teacher")


class Subject(Base):
    __tablename__ = "subject"
    id = Column(Integer, primary_key=True, index=True)
    subject_name = Column(String, index=True)
    teacher_id = Column(Integer, ForeignKey("teacher.id", ondelete="CASCADE"))
    teacher = relationship("teacher", back_populates="subjects")


class Grade(Base):
    __tablename__ = "grade"
    id = Column(Integer, primary_key=True, index=True)
    subject_name = Column(String, index=True)
    value = Column(Float)
    number = Column(Integer)
    subject_id = Column(Integer, ForeignKey("subject.id", ondelete="CASCADE"))
    student_id = Column(Integer, ForeignKey("student.id", ondelete="CASCADE"))
    student = relationship("student", back_populates="grades")


class Admin(Base):
    __tablename__ = "admin"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, index=True)
    token_version = Column(Integer, index=True)