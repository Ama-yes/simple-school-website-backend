from pydantic import BaseModel, ConfigDict, field_validator, model_validator





# ---- Validation Functions ---- #
## Password ##
def password_validator(value: str) -> str:
    value = value.strip()
    if len(value) < 8 or value == value.upper() or value == value.lower() or not any(char.isdigit() for char in value):
        raise ValueError("Password is weak! (Must contain mixed case and at least one digit)")
    
    if len(value) > 32:
        raise ValueError("Password is too long!")
    return value


## Email ##
def email_validator(value: str):
    value = value.strip()
    if len(value) < 4 or '@' not in value:
        raise ValueError("Invalid email!")
    return value.lower()


## Name ##
def name_validator(value: str):
    if len(value.strip()) < 6:
        raise ValueError("Invalid name!")
    return value.lower()


## Name ##
def username_validator(value: str):
    value = value.strip()
    if len(value) < 6:
        raise ValueError("Invalid username!")
    return value.lower()


## Subject ##
def subject_name_validator(value: str):
    return value.upper().strip()


## Grade ##
def grade_value_validator(value: float):
    if value < 0 or value > 100:
        raise ValueError("Invalid grade!")
    return value


def grade_number_validator(value: int):
    if value < 0 or value > 100:
        raise ValueError("Invalid grade number!")
    return value



# ---- Validation Models ---- #
## Misc ##
class ConfirmPassword(BaseModel):
    password: str
    confirm_password: str
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return password_validator(value)
    
    @model_validator(mode="after")
    def confirm_psswd(self):
        if self.password != self.confirm_password:
            raise ValueError("Password confirmation mismatch!")
        return self



## Student ##
class StudentSigningIn(BaseModel):
    name: str
    email: str
    password: str
    confirm_password: str
    school_year: int | None
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str):
        return name_validator(value)
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str):
        return email_validator(value)
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return password_validator(value)
    
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
        return email_validator(value)
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return password_validator(value)


class StudentEdit(BaseModel):
    name: str
    email: str
    school_year: int | None
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str):
        return name_validator(value)
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str):
        return email_validator(value)



## Teacher ##
class TeacherSigningIn(BaseModel):
    name: str
    email: str
    password: str
    confirm_password: str
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str):
        return name_validator(value)
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str):
        return email_validator(value)
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return password_validator(value)
    
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
        return email_validator(value)
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return password_validator(value)


class TeacherEdit(BaseModel):
    name: str
    email: str
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str):
        return name_validator(value)
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str):
        return email_validator(value)



## Admin ##
class AdminSigningIn(BaseModel):
    username: str
    email: str
    password: str
    confirm_password: str
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str):
        return username_validator(value)
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str):
        return email_validator(value)
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return password_validator(value)
    
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
        return username_validator(value)


class AdminEdit(BaseModel):
    username: str
    email: str
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str):
        return username_validator(value)
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str):
        return email_validator(value)



## Grade ##
class GradeInsert(BaseModel):
    student_id: int
    subject: str
    value: float
    number: int
    
    @field_validator("subject")
    @classmethod
    def validate_subject_name(cls, value: str):
        return subject_name_validator(value)
    
    @field_validator("value")
    @classmethod
    def validate_value(cls, value: float):
        return grade_value_validator(value)
    
    @field_validator("number")
    @classmethod
    def validate_number(cls, value: int):
        return grade_number_validator(value)


class GradeDelete(BaseModel):
    student_id: int
    subject: str
    number: int
    
    @field_validator("subject")
    @classmethod
    def validate_subject_name(cls, value: str):
        return subject_name_validator(value)
    
    @field_validator("number")
    @classmethod
    def validate_number(cls, value: int):
        return grade_number_validator(value)



## Subject ##
class SubjectInsert(BaseModel):
    subject_name: str
    teacher_id: int | None
    
    @field_validator("subject_name")
    @classmethod
    def validate_subject_name(cls, value: str):
        return subject_name_validator(value)




# ---- Response Models ---- #
class GradeBase(BaseModel):
    value: float
    number: int
    model_config = ConfigDict(from_attributes=True)


class TeacherSummary(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class SubjectMinimal(BaseModel):
    id: int
    subject_name: str
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
    school_year: int | None
    model_config = ConfigDict(from_attributes=True)


class GradeForTch(BaseModel):
    student: StudentSummary
    subject: str
    value: float
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


class BasicResponse(BaseModel):
    status: str
    detail: str

