from fastapi import APIRouter, Depends, HTTPException, status
from app.models.schemas import Token, TeacherLoggingIn, TeacherSigningIn
from app.repositories.teacher_repo import TeacherRepository
from app.core.dependencies import get_database
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer


router = APIRouter()

teacher_oauth2 = OAuth2PasswordBearer("/teacher/login")

def get_teacher_repo(db: Session = Depends(get_database)):
    return TeacherRepository(db)


@router.post("/signin")
def teacher_signin(data: TeacherSigningIn, repo: TeacherRepository = Depends(get_teacher_repo)):
    try:
        return repo.teacher_signin(teacher=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=Token)
def teacher_login(data: TeacherLoggingIn, repo: TeacherRepository = Depends(get_teacher_repo)):
    try:
        return repo.teacher_login(teacher=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/change/password", response_model=dict)
def teacher_change_password(new_password: str, token: str = Depends(teacher_oauth2), repo: TeacherRepository = Depends(get_teacher_repo)):
    try:
        return repo.teacher_change_password(new_password, token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/refresh", response_model=Token)
def teacher_token_refresh(token: str = Depends(teacher_oauth2), repo: TeacherRepository = Depends(get_teacher_repo)):
    try:
        return repo.teacher_token_refresh(token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

