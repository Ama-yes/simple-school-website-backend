from fastapi import APIRouter, Depends, HTTPException, status
from app.models.schemas import Token, StudentLoggingIn, StudentSigningIn
from app.repositories.student_repo import StudentRepository
from app.core.dependencies import get_database
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer


router = APIRouter()

student_oauth2 = OAuth2PasswordBearer("/student/login")

def get_student_repo(db: Session = Depends(get_database)):
    return StudentRepository(db)


@router.post("/signin")
def student_signin(data: StudentSigningIn, repo: StudentRepository = Depends(get_student_repo)):
    try:
        return repo.student_signin(student=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=Token)
def student_login(data: StudentLoggingIn, repo: StudentRepository = Depends(get_student_repo)):
    try:
        return repo.student_login(student=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/change/password", response_model=dict)
def student_change_password(new_password: str, token: str = Depends(student_oauth2), repo: StudentRepository = Depends(get_student_repo)):
    try:
        return repo.student_change_password(new_password, token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/refresh", response_model=Token)
def student_token_refresh(token: str = Depends(student_oauth2), repo: StudentRepository = Depends(get_student_repo)):
    try:
        return repo.student_token_refresh(token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

