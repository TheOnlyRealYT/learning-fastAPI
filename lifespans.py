from contextlib import asynccontextmanager
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from .models import (
   User,
   Program,
   Exercise
)
from typing import Any

CONNECTION_STRING = "mongodb+srv://bungy:Qv4EO2Icc1F9kO3C@gymtest.lgwl2bo.mongodb.net/?appName=GymTest" #super secret

@asynccontextmanager
async def life_span(_: FastAPI):
   client = AsyncIOMotorClient(CONNECTION_STRING)

   db: Any = client.gym
   await init_beanie(
      database=db,
      document_models=[User, Program, Exercise],
   )
   yield