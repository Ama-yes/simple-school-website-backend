from fastapi import APIRouter, Depends, HTTPException, status
from app.models.schemas import Token, StudentLoggingIn, StudentSigningIn
from app.repositories.student_repo import StudentRepository
from app.core.dependencies import get_database
from sqlalchemy.orm import Session


router = APIRouter()


def get_student_repo(db: Session = Depends(get_database)):
    return StudentRepository(db)


@router.post("/signin")
def student_signin(data: StudentSigningIn, repo: StudentRepository = Depends(get_student_repo)):
    try:
        return repo.student_signin(student=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)


@router.post("/login", response_model=Token)
def student_login(data: StudentLoggingIn, repo: StudentRepository = Depends(get_student_repo)):
    try:
        return repo.student_login(student=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)

