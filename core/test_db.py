import asyncio
# from sqlmodel import SQLModel, create_engine
from sqlalchemy.ext.asyncio import create_async_engine

from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=True)

async def test_connection():
    async with engine.begin() as conn:
        print("✅ Connected to the DB!")

asyncio.run(test_connection())
