from passlib.context import CryptContext
from app.core.config import settings
from datetime import datetime, timedelta
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError
from app.core.logging import setup_logger


context = CryptContext(schemes=["bcrypt"])


ENCODING_KEY = settings.encoder_key
ALGORITHM = "HS256"
ACCES_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7


logger = setup_logger()


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
    
    expire = datetime.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    
    encoded = jwt.encode(to_encode, key=ENCODING_KEY, algorithm=ALGORITHM)
    
    return encoded

def check_token(token):
    to_decode = token
    try:
        decoded = jwt.decode(token=to_decode, key=ENCODING_KEY, algorithms=ALGORITHM)
        return decoded
    
    except ExpiredSignatureError:
        raise ValueError("Token expired!")
    except JWTError as e:
        raise ValueError(f"Error: {e}")