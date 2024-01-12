from datetime import datetime, timedelta
from bson.objectid import ObjectId
from fastapi import APIRouter, Response, status, Depends, Request, HTTPException

from app import oauth2
from app.oauth2 import AuthJWT
from app.database import User
from app.serializers.userSerializers import userEntity, userResponseEntity

from ..import schemas, utils
from ..config import settings


router = APIRouter()

@router.get("/me", response_model=schemas.UserResponseSchema)
async def get_me(user_id: str = Depends(oauth2.require_user)):
    user = userResponseEntity(User.find_one( {"_id":ObjectId(str(user_id)) } ))
    return {"status": "success", "user": user}
    