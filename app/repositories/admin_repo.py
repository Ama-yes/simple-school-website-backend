from app.models.schemas import AdminLoggingIn, AdminSigningIn
from app.models.models import Admin
from app.core.security import check_token, check_password, create_access_token, create_refresh_token, password_hashing
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.exc import IntegrityError


class AdminRepository:
    def __init__(self, session: Session):
        self._db = session
    
    
    def admin_signin(self, admin: AdminSigningIn):
        db = self._db
        admin = Admin(username=admin.username, email=admin.email, hashed_password=password_hashing(admin.password), token_version=1)
        
        try:
            db.add(admin)
            db.commit()
        except IntegrityError:
            db.rollback()
            raise ValueError("Admin already exists!")
        
        db.refresh(admin)
        
        access_token = create_access_token({"sub": admin.username, "role": "admin"})
        refresh_token = create_refresh_token({"sub": admin.username, "version": admin.token_version, "role": "admin"})
        
        return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}
    
    
    def admin_login(self, admin: AdminLoggingIn):
        db = self._db
        query = db.query(Admin).filter(Admin.username == admin.username)
        
        db_admin = query.first()
        
        if not db_admin or not check_password(plain_password=admin.password, hashed_password=db_admin.hashed_password):
            raise ValueError("Email or password incorrect!")
        
        access_token = create_access_token({"sub": admin.username, "role": "admin"})
        refresh_token = create_refresh_token({"sub": admin.username, "version": db_admin.token_version, "role": "admin"})
        
        return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}
    
    
    def admin_verify_refresh_token(self, token) -> Admin:
        result = check_token(token)
        
        if not result:
            raise ValueError("Invalid credentials!")
        
        if not result.get("version"):
            raise ValueError("Invalid token type!")
        
        if result.get("role") != "admin":
            raise ValueError("Unexpected role!")
        
        username = result["sub"]
        token_v = result["version"]
        db = self._db
        query = db.query(Admin).filter(Admin.username == username)
        
        db_admin = query.first()
        
        if not db_admin:
            raise ValueError("Admin doesn't exist!")
        
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
        db.refresh(db_admin)
        
        return {"status": "Completed", "detail": "Log back in necessary!"}
    
    
    def admin_token_refresh(self, token: str):
        db_admin = self.admin_verify_refresh_token(token)
        
        access_token = create_access_token({"sub": db_admin.username, "role": "admin"})
        
        return {"access_token": access_token, "token_type": "bearer", "refresh_token": token}
        
        