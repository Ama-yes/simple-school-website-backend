from app.core.security import password_hashing, check_password, create_access_token, create_refresh_token, check_refresh_token, check_access_token
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.models.schemas import AdminLoggingIn, AdminSigningIn, StudentLoggingIn, StudentSigningIn, TeacherLoggingIn, TeacherSigningIn, ConfirmPassword
from app.models.models import Admin, Teacher, Student
from app.core.config import settings
from app.worker.tasks import send_email
from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe




class AuthRepository:
    def __init__(self, session: AsyncSession, role: str):
        self._db = session
        self._role = role
    
    
    async def signin(self, data: AdminSigningIn | StudentSigningIn | TeacherSigningIn):
        db = self._db
        role = self._role
        
        match role:
            case "Teacher":
                user = Teacher(name=data.name, email=data.email, hashed_password=password_hashing(data.password), token_version=1)
            case "Student":
                user = Student(name=data.name, email=data.email, hashed_password=password_hashing(data.password), school_year=data.school_year, token_version=1)
            case "Admin":
                user = Admin(username=data.username, email=data.email, hashed_password=password_hashing(data.password), token_version=1)
        
        try:
            db.add(user)
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise ValueError(f"{role} already exists!")
        
        return {"status": "Completed", "detail": "Sign in successful!"}
    
    
    async def login(self, user: AdminLoggingIn | StudentLoggingIn | TeacherLoggingIn):
        db = self._db
        role = self._role
        
        match role:
            case "Teacher":
                query = select(Teacher).where(Teacher.email == user.email)
            case "Student":
                query = select(Student).where(Student.email == user.email)
            case "Admin":
                query = select(Admin).where(Admin.username == user.username)
        
        result = await db.execute(query)
        
        db_user = result.scalars().first()
        
        if not db_user or not check_password(plain_password=user.password, hashed_password=db_user.hashed_password):
            raise ValueError("Email or password incorrect!")
        
        if role != "Admin" and not db_user.approved:
            raise ValueError("Account locked or not yet approved by an admin!")
        
        access_token = create_access_token({"sub": db_user.email, "role": role})
        refresh_token = create_refresh_token({"sub": db_user.email, "version": db_user.token_version, "role": role})
        
        return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}


    async def verify_refresh_token(self, token: str) -> Student | Admin | Teacher:
        role = self._role
        
        result = check_refresh_token(token)
        
        if not result:
            raise ValueError("Invalid credentials!")
        
        if not result.get("version"):
            raise ValueError("Invalid token type!")
        
        if result.get("role") != role:
            raise ValueError("Unexpected role!")
        
        email = result["sub"]
        token_v = result["version"]
        
        db = self._db
        
        match role:
            case "Teacher":
                query = select(Teacher).where(Teacher.email == email)
            case "Student":
                query = select(Student).where(Student.email == email)
            case "Admin":
                query = select(Admin).where(Admin.email == email)
        
        result = await db.execute(query)
        
        db_user = result.scalars().first()
        
        if not db_user:
            raise ValueError("Invalid credentials!")
        
        if db_user.token_version != token_v:
            raise ValueError("Invalid token version!")
        
        return db_user
        
        
    async def change_password(self, new_psswrd: ConfirmPassword, token: str):
        db = self._db
        db_user = await self.verify_refresh_token(token)
        
        db_user.token_version += 1
        db_user.hashed_password = password_hashing(password=new_psswrd.password) 
        db.add(db_user)
        await db.commit()
        
        return {"status": "Completed", "detail": "Log back in necessary!"}
    
    
    async def token_refresh(self, token: str):
        role = self._role
        db = self._db
        
        db_user = await self.verify_refresh_token(token)
        
        access_token = create_access_token({"sub": db_user.email, "role": role})
        
        db_user.token_version += 1
        db.add(db_user)
        await db.commit()
        
        refresh_token = create_refresh_token({"sub": db_user.email, "version": db_user.token_version, "role": role})
        
        return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}
    
    
    async def reset_password(self, email: str):
        db = self._db
        role = self._role
        
        match role:
            case "Teacher":
                query = select(Teacher).where(Teacher.email == email)
            case "Student":
                query = select(Student).where(Student.email == email)
            case "Admin":
                query = select(Admin).where(Admin.email == email)
        
        result = await db.execute(query)
        
        db_user = result.scalars().first()
        
        if not db_user:
            raise ValueError(f"{email} is not linked to any account!")
        
        reset_token = token_urlsafe(32)
        
        db_user.reset_token = reset_token
        db_user.reset_token_expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        
        await db.commit()
        
        link = f"{settings.hostname}/{role.lower()}/password-resetting/{reset_token}"
        
        send_email.delay(email, f"Hey {db_user.username if role == 'Admin' else db_user.name},\nClick below to reset your password:\n{link}\nNOTE: THIS ISN'T A CLICKABLE LINK, YOU SHOULD SEND A 'POST' REQUEST TO IT INCLUDING THE NEW PASSWORD!", "Password Reset Request")
        
        return {"status": "Completed", "detail": "Email sent in the backgroud!"}
    
    
    async def verify_token_reset_psswrd(self, token: str, psswrd: ConfirmPassword):
        db = self._db
        role = self._role
        
        match role:
            case "Teacher":
                query = select(Teacher).where(Teacher.reset_token == token)
            case "Student":
                query = select(Student).where(Student.reset_token == token)
            case "Admin":
                query = select(Admin).where(Admin.reset_token == token)
        
        result = await db.execute(query)
        
        db_user = result.scalars().first()
        
        if not db_user or db_user.reset_token_expire < datetime.now(timezone.utc):
            raise ValueError("Invalid link!")
        
        db_user.token_version += 1
        db_user.hashed_password = password_hashing(psswrd.password) 
        db_user.reset_token = None
        db_user.reset_token_expire = None
        db.add(db_user)
        await db.commit()
        
        return {"status": "Completed", "detail": "Log back in necessary!"}
    
    
    async def delete_user(self, current_user: Admin | Student | Teacher, todelete_id = None, user_type = None):
        role = self._role
        
        if not isinstance(current_user, Admin) and todelete_id:
            raise ValueError("Insufficient permissions!")
        
        db = self._db
        
        if isinstance(current_user, Teacher):
            db_user = current_user
        
        if isinstance(current_user, Student):
            db_user = current_user
        
        if isinstance(current_user, Admin):
            if not todelete_id:
                db_user = current_user
                
            elif user_type == "Teacher":
                query = select(Teacher).where(Teacher.id == todelete_id)
                result = await db.execute(query)
                db_user = result.scalars().first()    
                
            elif user_type == "Student":
                query = select(Student).where(Student.id == todelete_id)
                result = await db.execute(query)
                db_user = result.scalars().first()        
        
        if not db_user:
            raise ValueError(f"{user_type if user_type else role} doesn't exist!")
        
        
        await db.delete(db_user)
        await db.commit()
        
        return {"status": "Completed", "detail": "Deletion successful!"}
