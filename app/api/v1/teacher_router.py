from fastapi import APIRouter, Depends, HTTPException, status
from app.models.models import Teacher
from app.models.schemas import Token, TeacherLoggingIn, TeacherSigningIn, GradeForTch, GradeInsert, BasicResponse, ConfirmPassword, TeacherBase, TeacherEdit, GradeDelete, SubjectMinimal
from app.repositories.teacher_repo import TeacherRepository
from app.repositories.auth_repo import AuthRepository
from app.core.dependencies import get_database, teacher_oauth2, get_current_teacher
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.caching import cache, delete_cache_pattern, delete_cache
from fastapi_limiter.depends import RateLimiter


router = APIRouter()


def get_teacher_repo(db: AsyncSession = Depends(get_database)):
    return TeacherRepository(db)

def get_auth_repo(db: AsyncSession = Depends(get_database)):
    return AuthRepository(db, "Teacher")


@router.post("/signin", response_model=BasicResponse)
async def teacher_signin(data: TeacherSigningIn, repo: AuthRepository = Depends(get_auth_repo)):
    try:
        return await repo.signin(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=Token, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def teacher_login(user: TeacherLoggingIn, repo: AuthRepository = Depends(get_auth_repo)):
    try:
        return await repo.login(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/change-password", response_model=BasicResponse)
async def teacher_change_password(new_password: ConfirmPassword, token: str = Depends(teacher_oauth2), repo: AuthRepository = Depends(get_auth_repo)):
    try:
        return await repo.change_password(new_password, token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/refresh", response_model=Token)
async def teacher_token_refresh(token: str = Depends(teacher_oauth2), repo: AuthRepository = Depends(get_auth_repo)):
    try:
        return await repo.token_refresh(token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/resetpassword", response_model=BasicResponse)
async def teacher_reset_password(email: str, repo: AuthRepository = Depends(get_auth_repo)):
    try:
        return await repo.reset_password(email)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/password-resetting/{reset_token}", response_model=BasicResponse)
async def teacher_verify_token_reset_psswrd(reset_token: str, password: ConfirmPassword, repo: AuthRepository = Depends(get_auth_repo)):
    try:
        return await repo.verify_token_reset_psswrd(reset_token, password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/grade/{student_id}", response_model=GradeForTch)
async def teacher_grade_student(grade: GradeInsert, current_teacher: Teacher = Depends(get_current_teacher), repo: TeacherRepository = Depends(get_teacher_repo)):
    try:
        await delete_cache_pattern(f"student/{grade.student_id}/grades")
        await delete_cache_pattern("admin/students*")
        return await repo.teacher_grade_student(current_teacher, grade)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.patch("/grade/{student_id}", response_model=GradeForTch)
async def teacher_edit_grade(grade: GradeInsert, current_teacher: Teacher = Depends(get_current_teacher), repo: TeacherRepository = Depends(get_teacher_repo)):
    try:
        await delete_cache(f"student/{grade.student_id}/grades")
        await delete_cache_pattern("admin/students*")
        return await repo.teacher_edit_grade(current_teacher, grade)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.delete("/grade/{student_id}", response_model=BasicResponse)
async def teacher_delete_grade(grade: GradeDelete, current_teacher: Teacher = Depends(get_current_teacher), repo: TeacherRepository = Depends(get_teacher_repo)):
    try:
        await delete_cache(f"student/{grade.student_id}/grades")
        await delete_cache_pattern("admin/students*")
        return await repo.teacher_delete_grade(current_teacher, grade)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/subjects", response_model=list[SubjectMinimal])
@cache("teacher/{current_teacher.id}/subjects", 60)
async def teacher_list_subjects(current_teacher: Teacher = Depends(get_current_teacher), repo: TeacherRepository = Depends(get_teacher_repo)):
    try:
        return await repo.teacher_list_subjects(current_teacher)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/me", response_model=TeacherBase)
@cache("teacher/{current_teacher.id}/me", 60)
async def teacher_check_profile(current_teacher: Teacher = Depends(get_current_teacher)):
    try:
        return current_teacher
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.patch("/me", response_model=TeacherBase)
async def teacher_modify_profile(data: TeacherEdit, current_teacher: Teacher = Depends(get_current_teacher), repo: TeacherRepository = Depends(get_teacher_repo)):
    try:
        await delete_cache(f"teacher/{current_teacher.id}/me")
        await delete_cache_pattern("admin/teachers*")
        return await repo.teacher_modify_profile(current_teacher, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.delete("/me", response_model=BasicResponse)
async def teacher_delete_self(current_teacher: Teacher = Depends(get_current_teacher), repo: AuthRepository = Depends(get_auth_repo)):
    try:
        await delete_cache(f"teacher/{current_teacher.id}/me")
        await delete_cache_pattern("admin/teachers*")
        return await repo.delete_user(current_teacher)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

