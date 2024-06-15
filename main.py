from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from passlib.context import CryptContext

import os
from dotenv import load_dotenv

from models import Token, TokenData, User, UserInDB
from db import get_user_from_db, add_user_to_db


load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 2


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def get_user(username: str):
    user = await get_user_from_db(username)
    if user:
        return UserInDB(**user)
    return None

async def authenticate_user(username: str, password: str):
    user = await get_user(username)

    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    invalid_credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    expired_credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise invalid_credentials_exception
        
        token_data = TokenData(username=username)
    
    except ExpiredSignatureError:
        raise expired_credentials_exception
    
    except InvalidTokenError:
        raise invalid_credentials_exception

    user = await get_user(username=token_data.username)

    if user is None:
        raise invalid_credentials_exception

    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/register")
async def register_user_route(user: UserInDB) -> User:
    user = UserInDB(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
        bio=user.bio
    )

    await add_user_to_db(user)
    return User(**user.model_dump())

@app.post("/login")
async def login_route(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = await authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")

@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]) -> User:
    return current_user