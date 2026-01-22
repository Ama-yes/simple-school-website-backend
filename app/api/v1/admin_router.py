from fastapi import APIRouter, Depends
from app.models.schemas import Token, AdminLoggingIn
from app.repositories.admin_repo import AdminRepository
from app.core.dependencies import get_database
from sqlalchemy.orm import Session


router = APIRouter()


def get_admin_repo(db: Session = Depends(get_database)):
    return AdminRepository(db)


@router.post("/login", response_model=Token)
def admin_login(data: AdminLoggingIn, repo: AdminRepository = Depends(get_admin_repo)):
    return repo.admin_login(admin=data)


@router.post("/change/password", response_model=dict)
def admin_change_password(token: Token, new_password: str, repo: AdminRepository = Depends(get_admin_repo)):
    return repo.admin_change_password(token, new_password)

