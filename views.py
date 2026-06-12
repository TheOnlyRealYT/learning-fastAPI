from fastapi import APIRouter, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from beanie import PydanticObjectId, WriteRules
from .models import User, Program, Exercise, ProgramExercise, UserInDB
from .utilities import hash_password

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get('/user/{user_id}', tags=["New"])
async def get_user(user_id: PydanticObjectId):
    """Fetch user using ID"""
    user = await UserInDB.get(user_id)
    if user == None:
        return HTTPException(status.HTTP_404_NOT_FOUND, "User Not Found")
    return User(**user.model_dump())

@router.post('/create/user', response_model=User, tags=["New"])
async def register_user(user: User, password: str):
    """
    Creates a new user, insures already existing user data is not at risk of being overridden (which happens with .save())
    intakes a user model and a password to be hashed and saved in the database, to ensure never returning an API request
    with a user password attached
    """
    try: 
        hashed_password = hash_password(password)
        userindb = UserInDB(**user.model_dump(), hashed_password=hashed_password)
        await userindb.insert()
        return user
    except Exception as e:
        return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, e)

@router.get('/user/login')
async def login():
    return 

@router.patch('/user/{user_id}/update_profile', response_model=User)
async def update_user(user_id: PydanticObjectId, new_user: UserInDB):
    """Update a user's profile"""
    try: 
        await new_user.update()
        await new_user.save()
        await new_user.sync()
        return User(**new_user.model_dump())
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, e)

@router.delete('/delete/user')
async def delete_user(user_id: PydanticObjectId):
    try:
        await Program.find_all(Program.user.document_class.id == user_id).delete()
        await UserInDB.find_one(UserInDB.id == user_id).delete()
        return {"Success": "User Deleted Successfully"}
    except Exception as e:
        return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, e)

@router.get('/user/{user_id}/programs')
async def get_programs(user_id: PydanticObjectId):
    """Fetch programs using user ID"""
    return await Program.find(Program.user.document_class.id == user_id).to_list()

@router.get('/user/{user_id}/programs/{program_id}')
async def get_program(program_id: PydanticObjectId):
    """Fetch one program using ID"""
    return await Program.get(program_id)

@router.post('/create/program', response_model=Program)
async def create_program(program: Program):
    """create programs and link with user ID"""
    await program.insert(link_rule=WriteRules.WRITE)
    return program

@router.patch('/user/{user_id}/programs/{program_id}/update', response_model=Program)
async def update_program(new_program: Program):
    """Update Program"""
    try: 
        await new_program.replace()
        await new_program.save()
        await new_program.sync()
        return new_program
    except Exception as e:
        return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, e)
    
@router.delete('/delete/program')
async def delete_program(program_id: PydanticObjectId):
    try:
        await Program.find_one(Program.id == program_id).delete()
        return {"Success": "Program Deleted Successfully"}
    except Exception as e:
        return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, e)

@router.patch('/user/{user_id}/programs/{program_id}/add_exercise', response_model=ProgramExercise)
async def add_program_exercise(program_id: PydanticObjectId, program_exercise: ProgramExercise):
    """Add exercise to program"""
    program = await Program.get(program_id)
    if program == None:
        return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "User Program Not Found")
    program.exercises.append(program_exercise)
    await program.save()
    await program.sync()
    return program_exercise

@router.get('/user/{user_id}/programs/{program_id}/exercise/{exercise_id}')
async def get_program_exercise(program_id: PydanticObjectId, exercise_id: PydanticObjectId):
    program = await Program.get(program_id)
    if program == None:
        return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "User Program Not Found")
    for exercise_ in program.exercises:
        if exercise_.id == exercise_id:
            return exercise_
    return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Program Exercise Not Found")

@router.patch('/user/{user_id}/programs/{program_id}/exercise/{exercise_id}/update', response_model=ProgramExercise)
async def update_program_exercise(program_id: PydanticObjectId, exercise_id: PydanticObjectId, program_exercise: ProgramExercise):
    """Update a program exercise"""
    program = await Program.get(program_id)
    if program == None:
        return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "User Program Not Found")
    for exercise_ in program.exercises:
        if exercise_.id == exercise_id:
            exercise_ = program_exercise
            return exercise_
    return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Program Exercise Not Found")

@router.delete('/delete/program/{program_id}/exercise/{exercise_id}')
async def delete_program_exercise(program_id: PydanticObjectId, exercise_id: PydanticObjectId):
    """Delete a program exercise"""
    program = await Program.get(program_id)
    if program == None:
        return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "User Program Not Found")
    for exercise_ in enumerate(program.exercises):
        if exercise_[1].id == exercise_id:
            temp = program.exercises.pop(exercise_[0])
            program.exercises.sort(key=id)
            return temp
    return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Program Exercise Not Found")

@router.get('/exercises')
async def get_all_exercises():
    """Get all Exercises"""
    return await Exercise.find_all().to_list()

@router.get('/exercise/{exercise_id}')
async def get_exercise(exercise_id: PydanticObjectId):
    """Get Exercise by ID"""
    return await Exercise.get(exercise_id)

@router.post('/create/exercise', response_model=Exercise)
async def create_exercise(exercise: Exercise):
    """Create Exercise"""
    await exercise.insert()
    return exercise

@router.patch('/exercise/{exercise_id}/update', response_model=Exercise)
async def update_exercise(exercise: Exercise):
    """Update an exercise"""
    try:
        await exercise.replace()
        await exercise.save()
        await exercise.sync()
        return exercise
    except Exception as e:
        return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, e)
    
@router.delete('/exercise/{exercise_id}/delete')
async def delete_exercise(exercise_id: PydanticObjectId):
    try:
        await Exercise.find_one(Exercise.id == exercise_id).delete()
        return {"Success": "Exercise Deleted Successfully"}
    except Exception as e:
        return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, e)