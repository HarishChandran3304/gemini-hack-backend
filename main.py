from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, status, Query, Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from passlib.context import CryptContext

from typing import List

import os
from dotenv import load_dotenv

from models import Token, TokenData, User, UserInDB, Questions, Event
from db import get_user_from_db, add_user_to_db, add_event_to_db, get_items_by_tag, onboard, get_fyp, get_liked_events, get_profile, get_events


load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


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
        detail="Invalid token",
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

async def get_author_user(current_user: User = Depends(get_current_user)):
    if current_user.role != "author":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to perform this action",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user

async def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to perform this action",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/signup", status_code=status.HTTP_201_CREATED)
async def register_user_route(user: UserInDB) -> User:
    await add_user_to_db(user)

    return User(**user.model_dump())

@app.post("/login", status_code=status.HTTP_200_OK)
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

    return Token(access_token=access_token, token_type="Bearer")

@app.post("/onboarding/", status_code=status.HTTP_200_OK)
async def onboard_user_route(current_user: Annotated[User, Depends(get_current_active_user)], answers: Questions) -> User:
    await onboard(current_user.username, answers)
    return {"message": "success"}

@app.get("/users/me/")
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]) -> User:
    return current_user

@app.post("/event/")
async def create_event_route(event: Event) -> Event:
    await add_event_to_db(event)
    return event

@app.post("/onboarding/", status_code=status.HTTP_200_OK)
async def onboard_user_route(current_user: Annotated[User, Depends(get_current_active_user)], answers: Questions) -> User:
    # TODO: Take these questions and answers, perform RAG on them, generate a bio for each user and update their db entry
    return current_user

# @app.get("/items/")
# async def get_items_by_tag_route(current_user: Annotated[User, Depends(get_current_active_user)], tag: str) -> list[Item]:
#     res = []
#     for tag in current_user.tags:
#         res.extend(await get_items_by_tag(tag))
    
#     return res

@app.get("/for-you-page/", status_code=status.HTTP_200_OK)
async def get_for_you_page_route(
    current_user: Annotated[User, Depends(get_current_active_user)],
    categoryFilter: Optional[List[str]] = Query(None),
    searchFilters: Optional[List[str]] = Query(None),
) -> list[Event]:
    return await get_fyp(categoryFilter, searchFilters)

@app.get("/liked/", status_code=status.HTTP_200_OK)
async def get_liked_events_route(current_user: Annotated[User, Depends(get_current_active_user)]) -> list[Event]:
    return await get_liked_events(current_user.username)

@app.get("/profile", status_code=status.HTTP_200_OK)
async def get_profile_route(current_user: Annotated[User, Depends(get_current_active_user)]) -> User:
    return await get_profile(current_user.username)

@app.get("/events/", status_code=status.HTTP_200_OK)
async def get_events_route(
    current_user: Annotated[User, Depends(get_current_active_user)],
    categoryFilter: Optional[List[str]] = Query(None),
    searchFilters: Optional[List[str]] = Query(None),
) -> list[Event]:
    return await get_events(categoryFilter, searchFilters)