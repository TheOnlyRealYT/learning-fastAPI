from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from typing import Annotated, Literal
from pymongo import MongoClient

def get_database():
   CONNECTION_STRING = "mongodb+srv://bungy:Qv4EO2Icc1F9kO3C@gymtest.lgwl2bo.mongodb.net/?appName=GymTest"
 
   client = MongoClient(CONNECTION_STRING)
 
   return client['user_shopping_list']

app = FastAPI(debug=True)

class User(BaseModel):
    id: int
    name: str
    age: int
    score: int = 0
    profile_image: str | None = None

fake_db = {
    "user_table": [],
    "program_table": [],
    "exercise_table": [],
    "program_exercise_table": []
}

@app.get("/user/users")
async def get_all_users():
    response = []
    for user in fake_db['user_table']:
        response.append(user)
    return response 

@app.get("/user/{user_id}")
async def get_user_id(user_id: int):
    for user in fake_db["user_table"]:
        if user.id == user_id:
            return user
    return {"Error": "User not found"}

@app.post("/user/create", response_model=User)
async def create_user(user: User):
    fake_db['user_table'].append(user)
    return user

#program
class Program(BaseModel):
    id: int
    user_id: int
    name: str = "Program"

@app.get('/user/{user_id}/program')
async def get_user_program(user_id: int):
    for program_ in fake_db["program_table"]:
        if program_.user_id == user_id:
            program = program_
            break
    else: 
        return {"Error": "Not Found"}
    return program

@app.post('/create_program', response_model=Program)
async def create_program(program: Program):
    for user in fake_db["user_table"]:
        if program.user_id == user.id:
            fake_db["program_table"].append(program)
            return program
    return {"Error": "user not found"}

#exercises
class ProgramExercise(BaseModel):
    id: int
    program_id: int
    exercise_id: int
    reps: int = 0
    weight: int = 0
    day: int = Field(0, ge=0, le=6)

class Exercise(BaseModel):
    id: int 
    name: str
    difficulty: int = Field(0, ge=0, le=5) 

@app.post('/create_exercise', response_model = Exercise)
async def create_exercise(exercise: Exercise):
    fake_db["exercise_table"].append(exercise)
    return exercise

@app.post('/user/{user_id}/program/add_exercise')
async def create_program_exercise(program_exercise: ProgramExercise):
    for program_ in fake_db["program_table"]:
        if program_.id == program_exercise.program_id:
            program = program_
            break
    else:
        return {"Error": "program not found"}
    for exercise_ in fake_db["exercise_table"]:
        if exercise_.id == program_exercise.exercise_id:
            exercise = exercise_
            break
    else:
        return {"Error": "exercise not found"}
    fake_db["program_exercise_table"].append(program_exercise)
    return "[Program: {0}\nExercise: {1}\n{2}]".format(program.model_dump(), exercise.model_dump(), program_exercise.model_dump())

@app.get('/user/{user_id}/program/exercises')
async def get_exercises(user_id: int):
    exercises = []
    for user_ in fake_db["user_table"]:
        if user_.id == user_id:
            user = user_
            break
    else:
        return {"Error": "User Doesn't Exist"}

    for program_ in fake_db['program_table']:
        if program_.user_id == user_id:
            for exercise in fake_db["program_exercise_table"]:
                if exercise.program_id == program_.id:
                    exercises.append(exercise)
            if len(exercises) == 0:
                return {"Error": "No Exercises in the program"}
            else:
                break
    else:
        return {"Error": "User has no program"}
    return exercises

@app.patch('/user/{user_id}/program/update_exercise')
async def update_exercise(exercise_id: int, exercise: ProgramExercise):
    for exercise_ in fake_db['program_exercise_table']:
        if exercise_.id == exercise_id:
            exercise_ = exercise
    return {"Error": "Exercise Not Found, Can't Update"}

#debug tools
@app.get('/print_fake_db')
async def print_fake_db():
    print(fake_db)

"""
mongodb+srv://bungy:Qv4EO2Icc1F9kO3C@gymtest.lgwl2bo.mongodb.net/?appName=GymTest
"""