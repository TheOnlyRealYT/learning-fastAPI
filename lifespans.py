from contextlib import asynccontextmanager
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from .models import (
   UserInDB,
   Program,
   Exercise
)
from typing import Any
import dotenv, os

dotenv.load_dotenv()
CONNECTION_STRING = os.getenv("CONNECTION_STRING") #super secret

@asynccontextmanager
async def life_span(_: FastAPI):
   client = AsyncIOMotorClient(CONNECTION_STRING)

   db: Any = client.gym
   await init_beanie(
      database=db,
      document_models=[UserInDB, Program, Exercise],
   )
   yield