from fastapi import APIRouter, Depends, HTTPException, status
from app.models.schemas import Token, AdminLoggingIn
from app.repositories.admin_repo import AdminRepository
from app.core.dependencies import get_database
from sqlalchemy.orm import Session


router = APIRouter()


def get_admin_repo(db: Session = Depends(get_database)):
    return AdminRepository(db)


@router.post("/login", response_model=Token)
def admin_login(data: AdminLoggingIn, repo: AdminRepository = Depends(get_admin_repo)):
    try:
        return repo.admin_login(admin=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)


@router.post("/change/password", response_model=dict)
def admin_change_password(token: Token, new_password: str, repo: AdminRepository = Depends(get_admin_repo)):
    try:
        return repo.admin_change_password(token, new_password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e)

