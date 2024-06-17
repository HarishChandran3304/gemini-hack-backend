import motor.motor_asyncio
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from models import User, UserInDB, Item
from datetime import datetime, timedelta, timezone


load_dotenv()
uri = os.getenv("MONGO_URI")
client = motor.motor_asyncio.AsyncIOMotorClient(uri)
db = client["gemini-hack"]
users = db["users"]
items = db["items"]


async def add_user_to_db(user: UserInDB) -> User:
    await users.insert_one(user.model_dump())
    return user

async def get_user_from_db(username: str) -> UserInDB | None:
    user = await users.find_one({"username": username})
    return user

async def add_item_to_db(item: Item) -> Item:
    await items.insert_one(item.model_dump())
    return item

async def check_if_item_has_ended(itemId: int) -> bool:
    item = await items.find_one({"itemId": itemId})
    return item["ended"]

async def update_if_item_ended(itemId: int):
    item = await items.find_one({"itemId": itemId})

    if item["date"] < datetime.now():
        await items.update_one({"itemId": itemId}, {"$set": {"ended": True}})
        return True

async def main():
    await update_if_item_ended(1)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())