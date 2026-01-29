from fastapi import APIRouter, Depends, HTTPException, status
from app.models.models import Student
from app.models.schemas import Token, StudentLoggingIn, StudentSigningIn, GradeForStd, BasicResponse, ConfirmPassword, StudentBase, StudentEdit
from app.repositories.student_repo import StudentRepository
from app.repositories.auth_repo import AuthRepository
from app.core.dependencies import get_database, get_current_student, student_oauth2
from sqlalchemy.orm import Session
from app.core.caching import cache, delete_cache, delete_cache_pattern


router = APIRouter()


def get_student_repo(db: Session = Depends(get_database)):
    return StudentRepository(db)

def get_auth_repo(db: Session = Depends(get_database)):
    return AuthRepository(db, "Student")


@router.post("/signin", response_model=BasicResponse)
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
def student_verify_token_reset_psswrd(reset_token: str, password: ConfirmPassword, repo: AuthRepository = Depends(get_auth_repo)):
    try:
        return repo.verify_token_reset_psswrd(reset_token, password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/me", response_model=StudentBase)
@cache("student/{current_student.id}/me", 60)
def student_check_profile(current_student: Student = Depends(get_current_student)):
    try:
        return current_student
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/grades", response_model=list[GradeForStd])
@cache("student/{current_student.id}/grades", 60)
def student_grades_check(current_student: Student = Depends(get_current_student), repo: StudentRepository = Depends(get_student_repo)):
    try:
        return repo.student_grades_check(current_student)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.patch("/me", response_model=StudentBase)
def student_modify_profile(data: StudentEdit, current_student: Student = Depends(get_current_student), repo: StudentRepository = Depends(get_student_repo)):
    try:
        delete_cache(f"student/{current_student.id}/me")
        delete_cache_pattern("admin/students*")
        return repo.student_modify_profile(current_student, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.delete("/me", response_model=BasicResponse)
def student_delete_self(current_student: Student = Depends(get_current_student), repo: AuthRepository = Depends(get_auth_repo)):
    try:
        delete_cache(f"student/{current_student.id}/me")
        delete_cache_pattern("admin/students*")
        return repo.delete_user(current_student)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

