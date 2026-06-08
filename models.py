from pydantic import BaseModel, Field
from beanie import Document, BackLink, Link, Indexed
from typing import Annotated
from pymongo import TEXT

class User(Document):
   name: Annotated[str, Indexed()]
   age: int
   
   class Settings:
      name = "users"

class Exercise(Document):
   name: Annotated[str, Indexed()]
   difficulty: int = Field(ge=1, le=5)
   ratings: list[int] = [0, 0, 0, 0] #1, 2, 3, 4 star rating

   class Settings:
      name = "exercises"

class ProgramExercise(BaseModel): #base model cause its embedded in program not a separate collection 
   exercise: Link[Exercise]
   training_order: int
   reps: int = 0
   sets: int = 0
   weight_lb: int = 0
   training_day: int = Field(ge=0, le=6)

class Program(Document):
   user: Annotated[Link[User], Indexed()]
   name: Annotated[str, Indexed()]
   training_days: int = Field(ge=1, le=7)
   exercises: list[ProgramExercise] = []

   class Settings:
      name = "programs"