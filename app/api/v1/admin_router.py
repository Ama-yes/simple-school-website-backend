from fastapi import APIRouter, Depends, HTTPException, status
from app.models.models import Admin
from app.models.schemas import Token, AdminLoggingIn, AdminSigningIn, SubjectSummary, SubjectInsert, BasicResponse, ConfirmPassword, AdminBase, StudentSummary, TeacherBase, AdminEdit
from app.repositories.admin_repo import AdminRepository
from app.repositories.auth_repo import AuthRepository
from app.core.dependencies import get_database, get_current_admin, admin_oauth2
from sqlalchemy.orm import Session
from app.core.caching import cache, delete_cache, delete_cache_pattern


router = APIRouter()


def get_admin_repo(db: Session = Depends(get_database)):
    return AdminRepository(db)

def get_auth_repo(db: Session = Depends(get_database)):
    return AuthRepository(db, "Admin")


@router.post("/signin", response_model=BasicResponse)
def admin_signin(data: AdminSigningIn, repo: AuthRepository = Depends(get_auth_repo)):
    try:
        return repo.signin(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=Token)
def admin_login(user: AdminLoggingIn, repo: AuthRepository = Depends(get_auth_repo)):
    try:
        return repo.login(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/change-password", response_model=BasicResponse)
def admin_change_password(new_password: ConfirmPassword, token: str = Depends(admin_oauth2), repo: AuthRepository = Depends(get_auth_repo)):
    try:
        return repo.change_password(new_password, token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/refresh", response_model=Token)
def admin_token_refresh(token: str = Depends(admin_oauth2), repo: AuthRepository = Depends(get_auth_repo)):
    try:
        return repo.token_refresh(token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/resetpassword", response_model=BasicResponse)
def admin_reset_password(email: str, repo: AuthRepository = Depends(get_auth_repo)):
    try:
        return repo.reset_password(email)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/password-resetting/{reset_token}", response_model=BasicResponse)
def admin_verify_token_reset_psswrd(reset_token: str, password: ConfirmPassword, repo: AuthRepository = Depends(get_auth_repo)):
    try:
        return repo.verify_token_reset_psswrd(reset_token, password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/me", response_model=AdminBase)
@cache("admin/{current_admin.id}/me", 60)
def admin_check_profile(current_admin: Admin = Depends(get_current_admin)):
    try:
        return current_admin
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/add-subject", response_model=SubjectSummary)
def admin_add_subject(subject: SubjectInsert, require_admin: Admin = Depends(get_current_admin), repo: AdminRepository = Depends(get_admin_repo)):
    try:
        delete_cache_pattern("admin/subjects*")
        return repo.admin_add_subject(subject)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/students", response_model=list[StudentSummary])
@cache("admin/students_{skip}_{limit}", 60)
def admin_list_students(skip: int = 0, limit: int = 10, require_admin: Admin = Depends(get_current_admin), repo: AdminRepository = Depends(get_admin_repo)):
    try:
        return repo.admin_list_students(skip, limit)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/teachers", response_model=list[TeacherBase])
@cache("admin/teachers_{skip}_{limit}", 60)
def admin_list_teachers(skip: int = 0, limit: int = 10, require_admin: Admin = Depends(get_current_admin), repo: AdminRepository = Depends(get_admin_repo)):
    try:
        return repo.admin_list_teachers(skip, limit)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/subjects", response_model=list[SubjectSummary])
@cache("admin/subjects_{skip}_{limit}", 60)
def admin_list_subjects(skip: int = 0, limit: int = 10, require_admin: Admin = Depends(get_current_admin), repo: AdminRepository = Depends(get_admin_repo)):
    try:
        return repo.admin_list_subjects(skip, limit)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/assign-subject", response_model=BasicResponse)
def admin_assign_subject_to_teacher(subject_id: int, teacher_id: int, require_admin: Admin = Depends(get_current_admin), repo: AdminRepository = Depends(get_admin_repo)):
    try:
        delete_cache_pattern("admin/teachers*")
        delete_cache_pattern("admin/subjects*")
        return repo.admin_assign_subject_to_teacher(subject_id, teacher_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.patch("/me", response_model=AdminBase)
def admin_modify_profile(data: AdminEdit, current_admin: Admin = Depends(get_current_admin), repo: AdminRepository = Depends(get_admin_repo)):
    try:
        delete_cache(f"admin/{current_admin.id}/me")
        return repo.admin_modify_profile(current_admin, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.patch("/student/{student_id}/approve", response_model=BasicResponse)
def admin_approve_student(student_id: int, require_admin: Admin = Depends(get_current_admin), repo: AdminRepository = Depends(get_admin_repo)):
    try:
        return repo.admin_approve_user(student_id, "Student")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.patch("/teacher/{teacher_id}/approve", response_model=BasicResponse)
def admin_approve_teacher(teacher_id: int, require_admin: Admin = Depends(get_current_admin), repo: AdminRepository = Depends(get_admin_repo)):
    try:
        return repo.admin_approve_user(teacher_id, "Teacher")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.patch("/student/{student_id}/disapprove", response_model=BasicResponse)
def admin_disapprove_student(student_id: int, require_admin: Admin = Depends(get_current_admin), repo: AdminRepository = Depends(get_admin_repo)):
    try:
        return repo.admin_disapprove_user(student_id, "Student")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.patch("/teacher/{teacher_id}/disapprove", response_model=BasicResponse)
def admin_disapprove_teacher(teacher_id: int, require_admin: Admin = Depends(get_current_admin), repo: AdminRepository = Depends(get_admin_repo)):
    try:
        return repo.admin_disapprove_user(teacher_id, "Teacher")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.delete("/me", response_model=BasicResponse)
def admin_delete_self(current_admin: Admin = Depends(get_current_admin), repo: AuthRepository = Depends(get_auth_repo)):
    try:
        delete_cache(f"admin/{current_admin.id}/me")
        return repo.delete_user(current_admin)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.delete("/student/{student_id}", response_model=BasicResponse)
def admin_delete_student(student_id: int, current_admin: Admin = Depends(get_current_admin), repo: AuthRepository = Depends(get_auth_repo)):
    try:
        delete_cache_pattern("admin/students*")
        return repo.delete_user(current_admin, student_id, "Student")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.delete("/teacher/{teacher_id}", response_model=BasicResponse)
def admin_delete_teacher(teacher_id: int, current_admin: Admin = Depends(get_current_admin), repo: AuthRepository = Depends(get_auth_repo)):
    try:
        delete_cache_pattern("admin/teachers*")
        return repo.delete_user(current_admin, teacher_id, "Teacher")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

