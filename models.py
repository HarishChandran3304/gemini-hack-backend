from pydantic import BaseModel
from typing import Literal, List, Dict, Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str

class Answers(BaseModel):
    answers: List[Dict[str, str]]

class User(BaseModel):
    username: str
    email: str
    role: Literal["user", "author", "admin"] = "user"
    bio: Optional[Answers]
    tags: Optional[List[str]] = []
    likes: Optional[List[int]] = []

class UserInDB(User):
    password: str

class EventData(BaseModel):
    date: datetime
    location: Literal["online", "offline"]
    prize: str
    organizer: str

class Event(BaseModel):
    itemId: int
    title: str
    imageUrl: str
    tags: List[str]
    data: EventData
    description: str
    category: Literal["event", "challenge", "workshop", "project", "contest"]

class EmbeddingsQuery(BaseModel):
    sentence: str

class EmbeddingsResponse(BaseModel):
    embedding: List[float]

class Profile(BaseModel):
    name: str
    grade: str
    school: str
    description: str
    profilePic: str
    tags: List[str]
    eventList: List[Event] = []