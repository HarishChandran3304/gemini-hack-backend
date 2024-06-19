from pydantic import BaseModel
from typing import Literal, List, Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str

class User(BaseModel):
    username: str
    email: str
    role: Literal["user", "author", "admin"] = "user"
    bio: Optional[str] = ""
    tags: Optional[List[str]] = []

class UserInDB(User):
    password: str

class Item(BaseModel):
    itemId: int
    name: str
    itemType: Literal["Contest", "Project", "Activity", "Event"]
    desc: str
    date: datetime
    link: str
    tags: List[str]
    ended: Optional[bool] = False

class Questions(BaseModel):
    questions: list[dict[str, str]] = [
        {"question": "what do you do?", "answer": ""},
        {"question": "What are your interests?", "answer": ""},
        {"question": "What are your achievements?", "answer": ""}
    ]

class EmbeddingsQuery(BaseModel):
    sentence: str

class EmbeddingsResponse(BaseModel):
    embedding: List[float]