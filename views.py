from fastapi import APIRouter, status, Response
from beanie import PydanticObjectId, WriteRules, UpdateResponse
from .models import User, Program, Exercise, ProgramExercise

router = APIRouter()

@router.get('/user/{user_id}')
async def get_user(user_id: PydanticObjectId):
    """Fetch user using ID"""
    return await User.get(id)

@router.post('/create/user', response_model=User)
async def create_user(user: User):
    """Creates a new user, insures already exist user data is not at risk of being overridden (which happens with .save())"""
    await user.insert()
    return user

@router.patch('/user/{user_id}/update_profile', response_model=User)
async def update_user(user_id: PydanticObjectId, new_user: User):
    """Update a user's profile"""
    try: 
        await new_user.replace()
        return new_user
    except Exception as e:
        return Response({"Error": e}, status_code=status.HTTP_404_NOT_FOUND)

@router.delete('/delete/user')
async def delete_user(user_id: PydanticObjectId):
    try:
        return await User.find_one(User.id == user_id).delete()
    except Exception as e:
        return Response({"Error": e}, status_code=status.HTTP_404_NOT_FOUND)

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
        return new_program
    except Exception as e:
        return Response({"Error": e}, status_code=status.HTTP_404_NOT_FOUND)
    
@router.delete('/delete/program')
async def delete_program(program_id: PydanticObjectId):
    try:
        return await Program.find_one(Program.id == program_id).delete()
    except Exception as e:
        return Response({"Error": e}, status_code=status.HTTP_404_NOT_FOUND)

@router.patch('/user/{user_id}/programs/{program_id}/add_exercise', response_model=ProgramExercise)
async def add_program_exercise(program_id: PydanticObjectId, program_exercise: ProgramExercise):
    """Add exercise to program"""
    program = await Program.get(program_id)
    if program == None:
        return Response({"Error": "User Has no Program"}, status_code=status.HTTP_404_NOT_FOUND)
    program.exercises.append(program_exercise)
    await program.save()
    await program.sync()
    return program_exercise

@router.get('/user/{user_id}/programs/{program_id}/exercise/{exercise_id}')
async def get_program_exercise(program_id: PydanticObjectId, exercise_id: PydanticObjectId):
    program = await Program.get(program_id)
    if program == None:
        return Response({"Error": "User Has no Program"}, status_code=status.HTTP_404_NOT_FOUND)
    for exercise_ in program.exercises:
        if exercise_.id == exercise_id:
            return exercise_
    return Response({"Error": "Program Exercise Not Found"}, status_code=status.HTTP_404_NOT_FOUND)

@router.patch('/user/{user_id}/programs/{program_id}/exercise/{exercise_id}/update', response_model=ProgramExercise)
async def update_program_exercise(program_id: PydanticObjectId, exercise_id: PydanticObjectId, program_exercise: ProgramExercise):
    """Update a program exercise"""
    program = await Program.get(program_id)
    if program == None:
        return Response({"Error": "User Has no Program"}, status_code=status.HTTP_404_NOT_FOUND)
    for exercise_ in program.exercises:
        if exercise_.id == exercise_id:
            exercise_ = program_exercise
            return exercise_
    return Response({"Error": "Program Exercise Not Found"}, status_code=status.HTTP_404_NOT_FOUND)

@router.delete('/delete/program/{program_id}/exercise/{exercise_id}')
async def delete_program_exercise(program_id: PydanticObjectId, exercise_id: PydanticObjectId):
    """Delete a program exercise"""
    program = await Program.get(program_id)
    if program == None:
        return Response({"Error": "User Has no Program"}, status_code=status.HTTP_404_NOT_FOUND)
    for exercise_ in enumerate(program.exercises):
        if exercise_[1].id == exercise_id:
            temp = program.exercises.pop(exercise_[0])
            program.exercises.sort(key=id)
            return temp
    return Response({"Error": "Program Exercise Not Found"}, status_code=status.HTTP_404_NOT_FOUND)

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