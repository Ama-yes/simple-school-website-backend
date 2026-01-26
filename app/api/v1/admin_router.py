from fastapi import APIRouter, Depends, HTTPException, status
from app.models.schemas import Token, AdminLoggingIn, AdminSigningIn, SubjectSummary, SubjectInsert, BasicResponse, ConfirmPassword, AdminBase, StudentSummary, TeacherBase, AdminEdit
from app.repositories.admin_repo import AdminRepository
from app.repositories.auth_repo import AuthRepository
from app.core.dependencies import get_database
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer


router = APIRouter()

admin_oauth2 = OAuth2PasswordBearer("/admin/login")

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
def student_check_profile(token: str = Depends(admin_oauth2), repo: AuthRepository = Depends(get_auth_repo)):
    try:
        student = repo.verify_refresh_token(token)
        return student
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/add-subject", response_model=SubjectSummary)
def admin_add_subject(subject: SubjectInsert, token: str = Depends(admin_oauth2), repo: AdminRepository = Depends(get_admin_repo)):
    try:
        return repo.admin_add_subject(token, subject)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/students", response_model=list[StudentSummary])
def admin_list_students(skip: int = 0, limit: int = 10, token: str = Depends(admin_oauth2), repo: AdminRepository = Depends(get_admin_repo)):
    try:
        return repo.admin_list_students(token, skip, limit)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/teachers", response_model=list[TeacherBase])
def admin_list_teachers(skip: int = 0, limit: int = 10, token: str = Depends(admin_oauth2), repo: AdminRepository = Depends(get_admin_repo)):
    try:
        return repo.admin_list_teachers(token, skip, limit)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/subjects", response_model=list[SubjectSummary])
def admin_list_subjects(skip: int = 0, limit: int = 10, token: str = Depends(admin_oauth2), repo: AdminRepository = Depends(get_admin_repo)):
    try:
        return repo.admin_list_subjects(token, skip, limit)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/assign-subject", response_model=BasicResponse)
def admin_assign_subject_to_teacher(subject_id: int, teacher_id: int, token: str = Depends(admin_oauth2), repo: AdminRepository = Depends(get_admin_repo)):
    try:
        return repo.admin_assign_subject_to_teacher(token, subject_id, teacher_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.patch("/me", response_model=AdminBase)
def admin_modify_profile(data: AdminEdit, token: str = Depends(admin_oauth2), repo: AdminRepository = Depends(get_admin_repo)):
    try:
        return repo.admin_modify_profile(token, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.patch("/student/{student_id}", response_model=BasicResponse)
def admin_approve_student(student_id: int, token: str = Depends(admin_oauth2), repo: AdminRepository = Depends(get_admin_repo)):
    try:
        return repo.admin_approve_student(token, student_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.patch("/teacher/{teacher_id}", response_model=BasicResponse)
def admin_approve_teacher(teacher_id: int, token: str = Depends(admin_oauth2), repo: AdminRepository = Depends(get_admin_repo)):
    try:
        return repo.admin_approve_teacher(token, teacher_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.patch("/student/{student_id}", response_model=BasicResponse)
def admin_disapprove_student(student_id: int, token: str = Depends(admin_oauth2), repo: AdminRepository = Depends(get_admin_repo)):
    try:
        return repo.admin_disapprove_student(token, student_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.patch("/teacher/{teacher_id}", response_model=BasicResponse)
def admin_disapprove_teacher(teacher_id: int, token: str = Depends(admin_oauth2), repo: AdminRepository = Depends(get_admin_repo)):
    try:
        return repo.admin_disapprove_teacher(token, teacher_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.delete("/me", response_model=BasicResponse)
def admin_delete_self(token: str = Depends(admin_oauth2), repo: AuthRepository = Depends(get_auth_repo)):
    try:
        return repo.delete_user(token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.delete("/student/{student_id}", response_model=BasicResponse)
def admin_delete_student(student_id: int, token: str = Depends(admin_oauth2), repo: AuthRepository = Depends(get_auth_repo)):
    try:
        return repo.delete_user(token, student_id, "Student")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.delete("/teacher/{teacher_id}", response_model=BasicResponse)
def admin_delete_teacher(teacher_id: int, token: str = Depends(admin_oauth2), repo: AuthRepository = Depends(get_auth_repo)):
    try:
        return repo.delete_user(token, teacher_id, "Teacher")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

