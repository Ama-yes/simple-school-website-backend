from app.models.schemas import AdminLoggingIn, AdminSigningIn
from app.models.models import Admin
from app.core.config import settings
from app.core.security import check_refresh_token, check_password, create_access_token, create_refresh_token, password_hashing
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.exc import IntegrityError
from app.worker.tasks import send_email
from datetime import datetime, timedelta
import uuid


class AdminRepository:
    def __init__(self, session: Session):
        self._db = session
    
    def admin_verify_refresh_token(self, token) -> Admin:
        result = check_refresh_token(token)
        
        if not result:
            raise ValueError("Invalid credentials!")
        
        if not result.get("version"):
            raise ValueError("Invalid token type!")
        
        if result.get("role") != "Admin":
            raise ValueError("Unexpected role!")
        
        username = result["sub"]
        token_v = result["version"]
        db = self._db
        query = db.query(Admin).filter(Admin.username == username)
        
        db_admin = query.first()
        
        if not db_admin:
            raise ValueError("Invalid credentials!")
        
        if db_admin.token_version != token_v:
            raise ValueError("Invalid token version!")
        
        return db_admin
    
    
    def admin_change_password(self, new_password: str, token: str):
        db = self._db
        db_admin = self.admin_verify_refresh_token(token)
        
        db_admin.token_version += 1
        db_admin.hashed_password = password_hashing(password=new_password) 
        db.add(db_admin)
        db.commit()
        
        return {"status": "Completed", "detail": "Log back in necessary!"}
    
    
    def admin_token_refresh(self, token: str):
        db_admin = self.admin_verify_refresh_token(token)
        
        access_token = create_access_token({"sub": db_admin.username, "role": "Admin"})
        
        return {"access_token": access_token, "token_type": "bearer", "refresh_token": token}
    
    
    def admin_reset_password(self, email: str):
        db = self._db
        
        query = db.query(Admin).filter(Admin.email == email)
        db_admin = query.first()
        
        if not db_admin:
            raise ValueError(f"{email} is not linked to any account!")
        
        reset_token = str(uuid.uuid4())
        
        db_admin.reset_token = reset_token
        db_admin.reset_token_expire = datetime.now() + timedelta(minutes=15)
        
        db.commit()
        
        link = f"{settings.hostname}/admin/password-resetting/{reset_token}"
        
        result = send_email.apply_async(args=(email, f"Hey {db_admin.username},\nClick below to reset your password:\n{link}", "Password Reset Request"), expires=30, countdown=5)
        return result
    
    
    def admin_verify_reset_token(self, token: str, password: str):
        db = self._db
        
        query = db.query(Admin).filter(Admin.reset_token == token)
        db_admin = query.first()
        
        if not db_admin or db_admin.reset_token_expire < datetime.now():
            raise ValueError("Invalid link!")
        
        
        db_admin.token_version += 1
        db_admin.hashed_password = password_hashing(password) 
        db_admin.reset_token = None
        db_admin.reset_token_expire = None
        db.add(db_admin)
        db.commit()
        
        return {"status": "Completed", "detail": "Log back in necessary!"}