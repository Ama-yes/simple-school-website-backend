from fastapi import APIRouter, Depends, HTTPException, status
from app.models.schemas import Token, TeacherLoggingIn, TeacherSigningIn, GradeForTch, GradeInsert
from app.models.models import Teacher
from app.repositories.teacher_repo import TeacherRepository
from app.repositories.auth_repo import AuthRepository
from app.core.dependencies import get_database
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer


router = APIRouter()

teacher_oauth2 = OAuth2PasswordBearer("/teacher/login")

def get_teacher_repo(db: Session = Depends(get_database)):
    return TeacherRepository(db)

def get_auth_repo(db: Session = Depends(get_database)):
    return AuthRepository(db, "Teacher")


@router.post("/signin")
def teacher_signin(data: TeacherSigningIn, repo: AuthRepository = Depends(get_auth_repo)):
    try:
        return repo.signin(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=Token)
def teacher_login(user: TeacherLoggingIn, repo: AuthRepository = Depends(get_auth_repo)):
    try:
        return repo.login(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/change-password", response_model=dict)
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


@router.post("/resetpassword", response_model=str)
def teacher_reset_password(email: str, repo: TeacherRepository = Depends(get_teacher_repo)):
    try:
        return repo.teacher_reset_password(email)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/password-resetting/{token}", response_model=dict)
def teacher_verify_reset_token(token: str, password: str, repo: TeacherRepository = Depends(get_teacher_repo)):
    try:
        return repo.teacher_verify_reset_token(token, password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/grade/{student_id}", response_model=GradeForTch)
def teacher_grade_student(student_id: int, subject: str, grade: GradeInsert, token: str = Depends(teacher_oauth2), repo: TeacherRepository = Depends(get_teacher_repo)):
    try:
        return repo.teacher_grade_student(token, student_id, subject.upper(), grade)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

