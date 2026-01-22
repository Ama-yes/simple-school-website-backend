from fastapi import APIRouter, Depends, HTTPException, status
from app.models.schemas import Token, AdminLoggingIn, AdminSigningIn
from app.repositories.admin_repo import AdminRepository
from app.core.dependencies import get_database
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer


router = APIRouter()

admin_oauth2 = OAuth2PasswordBearer("/admin/login")

def get_admin_repo(db: Session = Depends(get_database)):
    return AdminRepository(db)


@router.post("/signin", response_model=Token)
def admin_signin(data: AdminSigningIn, repo: AdminRepository = Depends(get_admin_repo)):
    try:
        return repo.admin_signin(admin=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)


@router.post("/login", response_model=Token)
def admin_login(data: AdminLoggingIn, repo: AdminRepository = Depends(get_admin_repo)):
    try:
        return repo.admin_login(admin=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)


@router.post("/change/password", response_model=dict)
def admin_change_password(new_password: str, token: str = Depends(admin_oauth2), repo: AdminRepository = Depends(get_admin_repo)):
    try:
        return repo.admin_change_password(new_password, token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e)

