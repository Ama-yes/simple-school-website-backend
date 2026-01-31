from fastapi import APIRouter, Depends, HTTPException, status
from app.models.models import Student
from app.models.schemas import Token, StudentLoggingIn, StudentSigningIn, GradeForStd, BasicResponse, ConfirmPassword, StudentBase, StudentEdit
from app.repositories.student_repo import StudentRepository
from app.repositories.auth_repo import AuthRepository
from app.core.dependencies import get_database, get_current_student, student_oauth2, username_identifier
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.caching import cache, delete_cache, delete_cache_pattern
from fastapi_limiter.depends import RateLimiter


router = APIRouter()


def get_student_repo(db: AsyncSession = Depends(get_database)):
    return StudentRepository(db)

def get_auth_repo(db: AsyncSession = Depends(get_database)):
    return AuthRepository(db, "Student")


@router.post("/signin", response_model=BasicResponse, dependencies=[Depends(RateLimiter(times=10, seconds=60)), Depends(RateLimiter(times=5, seconds=60, identifier=username_identifier))])
async def student_signin(data: StudentSigningIn, repo: AuthRepository = Depends(get_auth_repo)):
    try:
        return await repo.signin(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=Token, dependencies=[Depends(RateLimiter(times=10, seconds=60)), Depends(RateLimiter(times=5, seconds=60, identifier=username_identifier))])
async def student_login(user: StudentLoggingIn, repo: AuthRepository = Depends(get_auth_repo)):
    try:
        return await repo.login(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/change-password", response_model=BasicResponse)
async def student_change_password(new_password: ConfirmPassword, token: str = Depends(student_oauth2), repo: AuthRepository = Depends(get_auth_repo)):
    try:
        return await repo.change_password(new_password, token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/refresh", response_model=Token)
async def student_token_refresh(token: str = Depends(student_oauth2), repo: AuthRepository = Depends(get_auth_repo)):
    try:
        return await repo.token_refresh(token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/resetpassword", response_model=BasicResponse)
async def student_reset_password(email: str, repo: AuthRepository = Depends(get_auth_repo)):
    try:
        return await repo.reset_password(email)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/password-resetting/{reset_token}", response_model=BasicResponse)
async def student_verify_token_reset_psswrd(reset_token: str, password: ConfirmPassword, repo: AuthRepository = Depends(get_auth_repo)):
    try:
        return await repo.verify_token_reset_psswrd(reset_token, password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/me", response_model=StudentBase)
@cache("student/{current_student.id}/me", 60)
async def student_check_profile(current_student: Student = Depends(get_current_student)):
    try:
        return current_student
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/grades", response_model=list[GradeForStd])
@cache("student/{current_student.id}/grades", 60)
async def student_grades_check(current_student: Student = Depends(get_current_student), repo: StudentRepository = Depends(get_student_repo)):
    try:
        return await repo.student_grades_check(current_student)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.patch("/me", response_model=StudentBase)
async def student_modify_profile(data: StudentEdit, current_student: Student = Depends(get_current_student), repo: StudentRepository = Depends(get_student_repo)):
    try:
        await delete_cache(f"student/{current_student.id}/me")
        await delete_cache_pattern("admin/students*")
        return await repo.student_modify_profile(current_student, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.delete("/me", response_model=BasicResponse)
async def student_delete_self(current_student: Student = Depends(get_current_student), repo: AuthRepository = Depends(get_auth_repo)):
    try:
        await delete_cache(f"student/{current_student.id}/me")
        await delete_cache_pattern("admin/students*")
        return await repo.delete_user(current_student)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

