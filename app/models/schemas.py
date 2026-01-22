from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class StudentSigningIn(BaseModel):
    name: str
    email: str
    password: str
    confirm_password: str
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str):
        return value.lower()
    
    @model_validator(mode="after")
    def confirm_psswd(self):
        if self.password != self.confirm_password:
            raise ValueError("Password confirmation mismatch!")


class StudentLoggingIn(BaseModel):
    email: str
    password: str
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str):
        return value.lower()

class StudentLoggedIn(BaseModel):
    id: int
    name: str


class GradeCheck(BaseModel):
    subject_name: str
    grade: float


class Admin(BaseModel):
    id: int
    username: str


class AdminLoggingIn(BaseModel):
    username: str
    password: str
    
    @field_validator("username")
    @classmethod
    def validate_email(cls, value: str):
        return value.lower()


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str