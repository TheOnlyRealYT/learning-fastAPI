from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Annotated, Literal
from pymongo import MongoClient
from beanie import Document