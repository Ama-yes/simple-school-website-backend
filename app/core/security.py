from passlib.context import CryptContext
from app.core.config import settings
from datetime import datetime, timedelta
from jose import jwt


context = CryptContext(schemes=["bcrypt"])


ENCODING_KEY = settings.encoder_key
ALGORITHM = "HS256"
ACCES_TOKEN_EXPIRE_MINUTES = 5
REFRESH_TOKEN_EXPIRE_DAYS = 7

def password_hashing(password: str):
    return context.hash(password)

def check_password(plain_password: str, hashed_password: str):
    return context.verify(secret=plain_password, hash=hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    
    expire = datetime.now() + timedelta(minutes=ACCES_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encoded = jwt.encode(to_encode, key=ENCODING_KEY, algorithm=ALGORITHM)
    
    return encoded

def create_refresh_token(data: dict):
    to_encode = data.copy()
    
    expire = datetime.now() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    
    encoded = jwt.encode(to_encode, key=ENCODING_KEY, algorithm=ALGORITHM)
    
    return encoded