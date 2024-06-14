import motor.motor_asyncio
from pydantic import BaseModel
from dotenv import load_dotenv
import os


load_dotenv()
uri = os.getenv("MONGO_URI")
client = motor.motor_asyncio.AsyncIOMotorClient(uri)
db = client["gemini-hack"]
users = db["users"]


class UserModel(BaseModel):
    username: str
    email: str
    password: str # Hashed password
    bio: str | None = None


async def add_user(user: UserModel):
    await users.insert_one(user.model_dump())

async def get_user(username: str):
    user = await users.find_one({"username": username})
    return user

async def main():
    await add_user(UserModel(
        username="test",
        email="test@gmail.com",
        password="test",
        bio=""
    ))

    user = await get_user("test")
    print(user)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())