from sqlalchemy import Boolean, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.database import Base



class Student(Base):
    __tablename__ = "Student"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    token_version = Column(Integer)
    grades = relationship("Grade", back_populates="student")


class Grade(Base):
    __tablename__ = "Grade"
    id = Column(Integer, primary_key=True, index=True)
    subject_name = Column(String, unique=True, index=True)
    grade = Column(Float)
    student_id = Column(Integer, ForeignKey("Student.id", ondelete="CASCADE"))
    student = relationship("Student", back_populates="grades")


class Admin(Base):
    __tablename__ = "Admin"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    token_version = Column(Integer)