import motor.motor_asyncio
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from models import User, UserInDB


load_dotenv()
uri = os.getenv("MONGO_URI")
client = motor.motor_asyncio.AsyncIOMotorClient(uri)
db = client["gemini-hack"]
users = db["users"]


async def add_user_to_db(user: UserInDB) -> None:
    await users.insert_one(user.model_dump())

async def get_user_from_db(username: str) -> UserInDB | None:
    user = await users.find_one({"username": username})
    return user

async def main():
    await add_user_to_db(UserInDB(
        username="test",
        email="test@gmail.com",
        password="test",
        bio=""
    ))

    user = await get_user_from_db("test")
    print(user)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())