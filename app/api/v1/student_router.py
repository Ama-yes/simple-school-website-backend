from fastapi import APIRouter, Depends, HTTPException, status
from app.models.schemas import Token, StudentLoggingIn, StudentSigningIn, GradeForStd, BasicResponse, ConfirmPassword, StudentBase, StudentEdit
from app.repositories.student_repo import StudentRepository
from app.repositories.auth_repo import AuthRepository
from app.core.dependencies import get_database
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer


router = APIRouter()

student_oauth2 = OAuth2PasswordBearer("/student/login")

def get_student_repo(db: Session = Depends(get_database)):
    return StudentRepository(db)

def get_auth_repo(db: Session = Depends(get_database)):
    return AuthRepository(db, "Student")


@router.post("/signin")
def student_signin(data: StudentSigningIn, repo: AuthRepository = Depends(get_auth_repo)):
    try:
        return repo.signin(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=Token)
def student_login(user: StudentLoggingIn, repo: AuthRepository = Depends(get_auth_repo)):
    try:
        return repo.login(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/change-password", response_model=BasicResponse)
def student_change_password(new_password: ConfirmPassword, token: str = Depends(student_oauth2), repo: AuthRepository = Depends(get_auth_repo)):
    try:
        return repo.change_password(new_password, token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/refresh", response_model=Token)
def student_token_refresh(token: str = Depends(student_oauth2), repo: AuthRepository = Depends(get_auth_repo)):
    try:
        return repo.token_refresh(token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/resetpassword", response_model=BasicResponse)
def student_reset_password(email: str, repo: AuthRepository = Depends(get_auth_repo)):
    try:
        return repo.reset_password(email)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/password-resetting/{reset_token}", response_model=BasicResponse)
def student_verify_reset_token(reset_token: str, password: ConfirmPassword, repo: AuthRepository = Depends(get_auth_repo)):
    try:
        return repo.verify_reset_token(reset_token, password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/me", response_model=StudentBase)
def student_check_profile(token: str = Depends(student_oauth2), repo: AuthRepository = Depends(get_auth_repo)):
    try:
        student = repo.verify_refresh_token(token)
        return student
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/grades", response_model=list[GradeForStd])
def student_grades_check(token: str = Depends(student_oauth2), repo: StudentRepository = Depends(get_student_repo)):
    try:
        return repo.student_grades_check(token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.patch("/me", response_model=StudentBase)
def student_modify_profile(data: StudentEdit, token: str = Depends(student_oauth2), repo: StudentRepository = Depends(get_student_repo)):
    try:
        return repo.student_modify_profile(token, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

