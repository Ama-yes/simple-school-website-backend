from fastapi import APIRouter, Depends, HTTPException, status
from app.models.schemas import Token, TeacherLoggingIn, TeacherSigningIn, GradeForTch, GradeInsert, BasicResponse, ConfirmPassword, TeacherBase, TeacherEdit
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


@router.post("/signin", response_model=BasicResponse)
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


@router.post("/change-password", response_model=BasicResponse)
def teacher_change_password(new_password: ConfirmPassword, token: str = Depends(teacher_oauth2), repo: AuthRepository = Depends(get_auth_repo)):
    try:
        return repo.change_password(new_password, token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/refresh", response_model=Token)
def teacher_token_refresh(token: str = Depends(teacher_oauth2), repo: AuthRepository = Depends(get_auth_repo)):
    try:
        return repo.token_refresh(token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/resetpassword", response_model=BasicResponse)
def teacher_reset_password(email: str, repo: AuthRepository = Depends(get_auth_repo)):
    try:
        return repo.reset_password(email)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/password-resetting/{reset_token}", response_model=BasicResponse)
def teacher_verify_token_reset_psswrd(reset_token: str, password: ConfirmPassword, repo: AuthRepository = Depends(get_auth_repo)):
    try:
        return repo.verify_token_reset_psswrd(reset_token, password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/me", response_model=TeacherBase)
def student_check_profile(token: str = Depends(teacher_oauth2), repo: AuthRepository = Depends(get_auth_repo)):
    try:
        student = repo.verify_refresh_token(token)
        return student
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/grade/{student_id}", response_model=GradeForTch)
def teacher_grade_student(student_id: int, subject: str, grade: GradeInsert, token: str = Depends(teacher_oauth2), repo: TeacherRepository = Depends(get_teacher_repo)):
    try:
        return repo.teacher_grade_student(token, student_id, subject.upper(), grade)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.patch("/me", response_model=TeacherBase)
def admin_modify_profile(data: TeacherEdit, token: str = Depends(teacher_oauth2), repo: TeacherRepository = Depends(get_teacher_repo)):
    try:
        return repo.teacher_modify_profile(token, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.delete("/me", response_model=BasicResponse)
def admin_delete_self(token: str = Depends(teacher_oauth2), repo: AuthRepository = Depends(get_auth_repo)):
    try:
        return repo.delete_user(token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

