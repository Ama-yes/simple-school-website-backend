from fastapi import APIRouter, Depends, HTTPException, status
from app.models.schemas import Token, AdminLoggingIn, AdminSigningIn, SubjectSummary, SubjectInsert
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


@router.post("/signin", response_model=Token)
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


@router.post("/change-password", response_model=dict)
def admin_change_password(new_password: str, token: str = Depends(admin_oauth2), repo: AdminRepository = Depends(get_admin_repo)):
    try:
        return repo.admin_change_password(new_password, token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/refresh", response_model=Token)
def admin_token_refresh(token: str = Depends(admin_oauth2), repo: AdminRepository = Depends(get_admin_repo)):
    try:
        return repo.admin_token_refresh(token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/resetpassword", response_model=str)
def admin_reset_password(email: str, repo: AdminRepository = Depends(get_admin_repo)):
    try:
        return repo.admin_reset_password(email)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/password-resetting/{token}", response_model=dict)
def admin_verify_reset_token(token: str, password: str, repo: AdminRepository = Depends(get_admin_repo)):
    try:
        return repo.admin_verify_reset_token(token, password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/add-subject", response_model=SubjectSummary)
def admin_add_subject(token: str, subject: SubjectInsert, repo: AdminRepository = Depends(get_admin_repo)):
    try:
        return repo.admin_add_subject(token, subject)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

