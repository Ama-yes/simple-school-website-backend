from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class StudentSigningIn(BaseModel):
    name: str
    email: str
    password: str
    confirm_password: str
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str):
        if len(value) < 8:
            raise ValueError("Invalid name!")
        return value.lower()
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str):
        if len(value) < 4 or '@' not in value:
            raise ValueError("Invalid email!")
        return value.lower()
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8 or value == value.upper() or value == value.lower():
            raise ValueError("Password is weak!")
        
        if len(value) > 32:
            raise ValueError("Password is too long!")
        return value
    
    @model_validator(mode="after")
    def confirm_psswd(self):
        if self.password != self.confirm_password:
            raise ValueError("Password confirmation mismatch!")
        return self


class StudentLoggingIn(BaseModel):
    email: str
    password: str
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str):
        if len(value) < 4 or '@' not in value:
            raise ValueError("Invalid email!")
        return value.lower()
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8 or value == value.upper() or value == value.lower():
            raise ValueError("Password is weak!")
        
        if len(value) > 32:
            raise ValueError("Password is too long!")
        return value

class StudentLoggedIn(BaseModel):
    id: int
    name: str


class GradeCheck(BaseModel):
    subject_name: str
    grade: float


class Admin(BaseModel):
    id: int
    username: str


class AdminSigningIn(BaseModel):
    username: str
    email: str
    password: str
    confirm_password: str
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str):
        if len(value) < 6:
            raise ValueError("Invalid username!")
        return value.lower()
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str):
        if len(value) < 4 or '@' not in value:
            raise ValueError("Invalid email!")
        return value.lower()
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8 or value == value.upper() or value == value.lower():
            raise ValueError("Password is weak!")
        
        if len(value) > 32:
            raise ValueError("Password is too long!")
        return value
    
    @model_validator(mode="after")
    def confirm_psswd(self):
        if self.password != self.confirm_password:
            raise ValueError("Password confirmation mismatch!")
        return self


class AdminLoggingIn(BaseModel):
    username: str
    password: str
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str):
        return value.lower()


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str