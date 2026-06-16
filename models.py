from pydantic import BaseModel, Field
from beanie import Document, Link, Indexed, PydanticObjectId
from typing import Annotated

class User(BaseModel):
   username: Annotated[str, Indexed(unique=True)]
   email: Annotated[str, Indexed()]
   age: int
   disabled: bool = False
   account_level: int = Field(ge=1, le=4) #client coach staff admin

class UserInDB(Document, User):
   hashed_password: str #we create this so we dont send passwords in API responses as its super unsafe

   class Settings:
      name = "users"
      validate_on_save = True

class Exercise(Document):
   name: Annotated[str, Indexed()]
   difficulty: int = Field(ge=1, le=5)
   ratings: list[int] = [0, 0, 0, 0] #1, 2, 3, 4 star rating

   class Settings:
      name = "exercises"
      validate_on_save = True

class ProgramExercise(BaseModel): #base model cause its embedded in program not a separate collection 
   id: PydanticObjectId = Field(default_factory=PydanticObjectId)
   exercise: Link[Exercise]
   training_order: int
   reps: int = 0
   sets: int = 0
   weight_lb: int = 0
   training_day: int = Field(ge=0, le=6)

class TempProgram(BaseModel):
   name: Annotated[str, Indexed()]
   training_days: int = Field(ge=1, le=7)

class Program(Document):
   user: Annotated[Link[UserInDB], Indexed()]
   name: Annotated[str, Indexed()]
   training_days: int = Field(ge=1, le=7)
   exercises: list[ProgramExercise] = []

   class Settings:
      name = "programs"
      validate_on_save = True