from argon2 import PasswordHasher
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from fastapi import HTTPException, status, Depends
from pydantic import BaseModel
from beanie import PydanticObjectId
from .models import UserInDB
from datetime import datetime, timedelta, timezone
import jwt, dotenv, os
from jwt.exceptions import InvalidTokenError

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: PydanticObjectId | None = None

dotenv.load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = os.getenv("ALGORITHM", "")
ACCESS_TOKEN_EXPIRE_MINUTES = float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 0.0))
credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

password_context = PasswordHasher()

def hash_password(password: str) -> str:
    return password_context.hash(password)

def verify_password(hashed_password: str, password: str) -> bool:
    return password_context.verify(hashed_password, password)

async def Authenticate_user(user_id: str, password: str):
    print(user_id)
    user = await UserInDB.get(PydanticObjectId(user_id))
    if user == None:
        HTTPException(status.HTTP_404_NOT_FOUND, "User Not Found")
        return False
    if not verify_password(user.hashed_password, password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("sub")

        if id is None:
            raise credentials_exception
        token_data = TokenData(id=id)
    except InvalidTokenError:
        raise credentials_exception
    user = await UserInDB.get(token_data.id)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[UserInDB, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user