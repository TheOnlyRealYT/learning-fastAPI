from fastapi import APIRouter, status
from beanie import PydanticObjectId
from .models import User, Program, Exercise

router = APIRouter()

@router.get('/user/{user_id}')
async def get_user(user_id: PydanticObjectId):
    """Fetch user using ID"""
    return await User.get(id)

@router.post('/create/user', response_model=User)
async def create_user(user: User):
    "Creates a new user, insures already exist user data is not at risk of being overridden (which happens with .save())"
    await user.create()
    return user