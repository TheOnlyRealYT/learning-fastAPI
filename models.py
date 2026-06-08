from pydantic import BaseModel, Field
from beanie import Document, BackLink, Link
from pymongo import TEXT

class User(Document):
   name: str
   age: int
   program: BackLink = Field(json_schema_extra={"original_field": "owner"})

   class Settings:
      name = "users"
      indexes = [
         [
            ("name", TEXT)
         ],
      ]

class Exercise(Document):
   name: str
   difficulty: int = Field(ge=1, le=5)
   ratings: list[int] = [0, 0, 0, 0] #1, 2, 3, 4 star rating

   class Settings:
      name = "exercises"
      indexes = [
         [
            ("name", TEXT)
         ],
      ]

class ProgramExercise(BaseModel): #base model cause its embedded in program not a separate collection 
   exercise: Link[Exercise]
   training_order: int
   reps: int = 0
   sets: int = 0
   weight_lb: int = 0
   training_day: int = Field(ge=0, le=6)

class Program(Document):
   user: Link[User]
   name: str
   training_days: int = Field(ge=1, le=7)
   exercises: list[ProgramExercise] = []

   class Settings:
      name = "programs"
      indexes = [
         [
            ("name", TEXT)
         ],
      ]