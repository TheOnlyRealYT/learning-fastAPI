from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from beanie import PydanticObjectId, WriteRules, Link
from typing import Annotated
from .models import User, Program, TempProgram, Exercise, ProgramExercise, UserInDB
from datetime import timedelta
from .utilities import Token, Authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, hash_password, get_current_active_user

router = APIRouter()
# split this in the main project in multiple routers for the models (prefixes, tags, dependencies, and responses)

@router.post('/token')
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = await UserInDB.find_one(UserInDB.username == form_data.username.lower())
    if user == None or user.id == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User Not Found")
    user = await Authenticate_user(user, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@router.get('/user/me', tags=["User Operations"], response_model=User)
async def get_current_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user

@router.patch('/user/change_username', tags=["User Operations"], response_model=User)
async def update_user(
    username: str,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    """Update current user's username"""
    try:         
        await current_user.set({UserInDB.username: username})
        return User(**current_user.model_dump())
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, e)

@router.post('/create/user', response_model=User, tags=["User Operations"])
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

@router.delete('/delete/user', tags=["User Operations"])
async def delete_user(user_id: PydanticObjectId, current_user: Annotated[UserInDB, Depends(get_current_active_user)]):
    # if current_user.role != "Admin": FORBIDDEN ERROR
    try:
        user = await UserInDB.get(user_id)
        if user == None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User Not Found/Not Logged In")
        if user != current_user:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Can't Another User's Account")
        await Program.find_all(Program.user.document_class.id == user_id).delete()
        await user.delete()
        return {"Success": "User Deleted Successfully"}
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, e)

@router.get('/user/me/programs', tags=["Program Operations"])
async def get_programs(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)]
    ):
    """Fetch programs of current user"""
    programs = await Program.find(Program.user == UserInDB.link_from_id(current_user.id)).to_list()
    return programs

@router.get('/user/me/programs/{program_id}', tags=["Program Operations"])
async def get_program(program_id: PydanticObjectId, current_user: Annotated[UserInDB, Depends(get_current_active_user)]):
    """Fetch current user program using ID"""
    program = await Program.get(program_id)
    if program == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Program Not Found")
    if program.user.ref != current_user.to_ref():
        user = await UserInDB.get(program.user.ref.id)
        if user == None:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "User Couldn't Be Fetched")
        print('hello')
        return RedirectResponse(f"/user/{user.username}/programs/{program_id}")
    return program

@router.get('/user/{username}', tags=["User Operations"])
async def get_user(username: str):
    """Fetch user using ID"""
    user = await UserInDB.find_one(UserInDB.username == username)
    if user == None:
        return HTTPException(status.HTTP_404_NOT_FOUND, "User Not Found")
    return User(**user.model_dump())

@router.get('/user/{username}/programs', tags=["Program Operations"])
async def get_user_programs(
    username: str
    ):
    """Fetch programs using username"""
    user = await UserInDB.find_one(User.username == username)
    if user == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User Not Found")
    return await Program.find(Program.user.document_class.id == user.id).to_list()

@router.get('/user/{username}/programs/{program_id}', tags=["Program Operations"])
async def get_user_program(username: str, program_id: PydanticObjectId):
    """Fetch current user program using ID Username is unimplemented yet"""
    user = await UserInDB.find_one(User.username == username)
    if user == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User Not Found")
    program = await Program.get(program_id)
    if program == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Program Not Found")
    if program.user == UserInDB.link_from_id(user.id):
        return program
    user = await UserInDB.get(program.user.ref.id)
    if user == None:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Program Has No User")
    return RedirectResponse(f"/user/{user.username}/programs/{program_id}")

@router.post('/create/program', response_model=Program, tags=["Program Operations"])
async def create_program(new_program: TempProgram, current_user: Annotated[UserInDB, Depends(get_current_active_user)]):
    """create programs and link with user ID"""
    program = Program(user = Link(current_user.to_ref(), UserInDB), **new_program.model_dump())
    await program.insert(link_rule=WriteRules.WRITE)
    return program

@router.patch('/user/me/programs/{program_id}/update', response_model=Program, tags=["Program Operations"])
async def update_program(program_id: PydanticObjectId, new_program: TempProgram, current_user: Annotated[UserInDB, Depends(get_current_active_user)]):
    """Update Program"""
    program = await Program.get(program_id)
    if program == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Program Not Found")
    if program.user.ref != current_user.to_ref():
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Cant Update A Program That Isn't Yours")
    try: 
        await program.set({Program.name: new_program.name, Program.training_days: new_program.training_days})
        return program
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, e)
    
@router.delete('/delete/program', tags=["Program Operations"])
async def delete_program(program_id: PydanticObjectId, current_user: Annotated[UserInDB, Depends(get_current_active_user)]):
    try:
        program = await Program.find_one(Program.id == program_id)
        if program == None:
            return HTTPException(status.HTTP_404_NOT_FOUND, "Program Not Found, Check ID")
        if program.user.ref != current_user.to_ref():
            return HTTPException(status.HTTP_401_UNAUTHORIZED, "Can't delete a program that isn't yours")
        await program.delete()
        return {"Success": "Program Deleted Successfully"}
    except Exception as e:
        return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, e)

@router.patch('/user/me/programs/{program_id}/add_exercise', response_model=ProgramExercise)
async def add_program_exercise(program_id: PydanticObjectId, program_exercise: ProgramExercise, current_user: Annotated[UserInDB, Depends(get_current_active_user)]):
    """Add exercise to program"""
    program = await Program.get(program_id)
    if program == None:
        return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "User Program Not Found")
    if program.user != UserInDB.link_from_id(current_user.id):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Can't Make Changes To a Program That Isn't Yours")
    program.exercises.append(program_exercise)
    await program.save()
    await program.sync()
    return program_exercise

@router.get('/user/me/programs/{program_id}/exercise/{exercise_id}')
async def get_program_exercise(program_id: PydanticObjectId, exercise_id: PydanticObjectId):
    program = await Program.get(program_id)
    if program == None:
        return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "User Program Not Found")
    for exercise_ in program.exercises:
        if exercise_.id == exercise_id:
            return exercise_
    return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Program Exercise Not Found")

@router.patch('/user/me/programs/{program_id}/exercise/{exercise_id}/update', response_model=ProgramExercise)
async def update_program_exercise(program_id: PydanticObjectId, 
                                  exercise_id: PydanticObjectId, 
                                  program_exercise: ProgramExercise, current_user: Annotated[UserInDB, Depends(get_current_active_user)]):
    """Update a program exercise"""
    program = await Program.get(program_id)
    if program == None:
        return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "User Program Not Found")
    if program.user != UserInDB.link_from_id(current_user.id):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Can't Update A Program That Isn't Yours")
    for exercise_ in program.exercises:
        if exercise_.id == exercise_id:
            exercise_ = program_exercise
            return exercise_
    return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Program Exercise Not Found")

@router.delete('/delete/program/{program_id}/exercise/{exercise_id}')
async def delete_program_exercise(program_id: PydanticObjectId, 
                                  exercise_id: PydanticObjectId, 
                                  current_user: Annotated[UserInDB, Depends(get_current_active_user)]):
    """Delete a program exercise"""
    program = await Program.get(program_id)
    if program == None:
        return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "User Program Not Found")
    if program.user != UserInDB.link_from_id(current_user.id):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Can't Update A Program That Isn't Yours")
    for exercise_ in enumerate(program.exercises):
        if exercise_[1].id == exercise_id:
            temp = program.exercises.pop(exercise_[0])
            program.exercises.sort(key=id)
            return temp
    return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Program Exercise Not Found")

@router.get('/exercises')
async def get_all_exercises(category: str | None = None):
    """Get all Exercises"""
    if category:
        return await Exercise.find(Exercise.catagory.name == category).to_list()
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