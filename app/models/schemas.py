from pydantic import BaseModel, ConfigDict, field_validator, model_validator



# ---- Validation Models ---- #
## Student ##
class StudentSigningIn(BaseModel):
    name: str
    email: str
    password: str
    confirm_password: str
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str):
        if len(value) < 6:
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



## Teacher ##
class TeacherSigningIn(BaseModel):
    name: str
    email: str
    password: str
    confirm_password: str
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str):
        if len(value) < 6:
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


class TeacherLoggingIn(BaseModel):
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



## Admin ##
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




# ---- Response Models ---- #
class GradeBase(BaseModel):
    value: float
    number: int
    model_config = ConfigDict(from_attributes=True)


class TeacherSummary(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class SubjectSummary(BaseModel):
    id: int
    subject_name: str
    teacher: TeacherSummary | None
    model_config = ConfigDict(from_attributes=True)


class GradeForStd(BaseModel):
    subject: SubjectSummary
    value: float
    number: int
    model_config = ConfigDict(from_attributes=True)


class StudentSummary(BaseModel):
    id: int
    name: str
    email: str
    school_year: int
    model_config = ConfigDict(from_attributes=True)


class GradeForTch(BaseModel):
    student: StudentSummary
    value: float # or maybe just "grade: Grade" ?
    number: int
    model_config = ConfigDict(from_attributes=True)


class StudentBase(BaseModel):
    id: int
    name: str
    email: str
    school_year: int
    grades: list[GradeForStd]
    model_config = ConfigDict(from_attributes=True)


class SubjectBase(BaseModel):
    id: int
    subject_name: str
    teacher: TeacherSummary | None
    grades: list[GradeBase]
    model_config = ConfigDict(from_attributes=True)


class TeacherBase(BaseModel):
    id: int
    name: str
    email: str
    subjects: list[SubjectBase]
    model_config = ConfigDict(from_attributes=True)


class AdminBase(BaseModel):
    id: int
    username: str
    email: str
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

