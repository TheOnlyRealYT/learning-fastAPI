from fastapi import APIRouter, status, Response
from beanie import PydanticObjectId, WriteRules
from .models import User, Program, Exercise, ProgramExercise

router = APIRouter()

@router.get('/user/{user_id}')
async def get_user(user_id: PydanticObjectId):
    """Fetch user using ID"""
    return await User.get(id)

@router.post('/create/user', response_model=User)
async def create_user(user: User):
    "Creates a new user, insures already exist user data is not at risk of being overridden (which happens with .save())"
    await user.insert()
    return user

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

@router.patch('/user/{user_id}/programs/{program_id}/add_exercise', response_model=ProgramExercise)
async def add_program_exercise(program_id: PydanticObjectId, program_exercise: ProgramExercise):
    """Add exercise to program"""
    program = await Program.get(program_id)
    if program == None:
        return Response({"Error": "User Has no Program"}, 404)
    program.exercises.append(program_exercise)
    await program.save()
    await program.sync()
    return program_exercise

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