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
ACCESS_TOKEN_EXPIRES_IN = settings.ACCESS_TOKEN_EXPIRES_IN
REFRESH_TOKEN_EXPIRES_IN = settings.REFRESH_TOKEN_EXPIRES_IN


# adding Endpoints

@router.post("/register")
async def create_user(request : Request, payload: schemas.CreateUserSchema):
    user = User.find_one({"email": payload.email.lower()})
    
    #Checking if the user email already exist
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="User with email Already Exist..")
    
    # Comparing password
    if payload.password!= payload.passwordConfirm:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Password does not match")
    
    #Hashing the password
    payload.password = utils.hash_password(payload.password)
    del payload.passwordConfirm
    payload.role = "user"
    payload.verified = True
    payload.email = payload.email.lower()
    payload.created_at = datetime.utcnow()
    payload.updated_at = payload.created_at
    result = User.insert_one(dict(payload))
    new_user = userResponseEntity(User.find_one({"_id": result.inserted_id}))
    return {"status": "Success", "user": new_user}
    

@router.post("/login")
async def login(payload: schemas.LoginUserSchema, response: Response, Authorize: AuthJWT = Depends()):
    db_user = User.find_one({"email": payload.email.lower()})
    if not db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Incorrect Email..")
    
    user = userEntity(db_user)
    
    
    if not utils.verify_password(payload.password, user.get("password")):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Incorrect Password...")
    
    #create access token
    access_token = Authorize.create_access_token(
        subject=user["id"], expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN)
    )
    
    #create refresh token
    refresh_token = Authorize.create_refresh_token(
        subject=user["id"],expires_time = timedelta(minutes=REFRESH_TOKEN_EXPIRES_IN)
    )
    
    #store refresh and access token in cookie
    response.set_cookie("access_token", access_token, ACCESS_TOKEN_EXPIRES_IN * 60,
                        ACCESS_TOKEN_EXPIRES_IN * 60, "/",None, False, True, 'lax')
    response.set_cookie("refresh_token",refresh_token, REFRESH_TOKEN_EXPIRES_IN * 60,
                        REFRESH_TOKEN_EXPIRES_IN * 60, "/", None, False,True,'lax')
    response.set_cookie("logged_in", "True", ACCESS_TOKEN_EXPIRES_IN * 60, ACCESS_TOKEN_EXPIRES_IN *60,
                        "/", None, False, False, 'lax')
    
    return {'status': "success", "access_token": access_token}

@router.get("/refresh")
async def refresh_token(response: Response, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_refresh_token_required()
        
        user_id = Authorize.get_jwt_subject()
        
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not refresh token")
        
        user = userEntity(User.find_one({"_id":ObjectId(str(user_id))}))
        
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="The user belongs to this token not longer exist..")
        
        access_token = Authorize.create_access_token(subject=str(user["id"]),
                                expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN))
    
    except Exception as e:
        error = e.__class__.__name__
        if error == 'MissingTokenError':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Please provide refresh token"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
        )
            
    response.set_cookie('access_token', access_token, ACCESS_TOKEN_EXPIRES_IN * 60,
    ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')
    response.set_cookie('logged_in', 'True', ACCESS_TOKEN_EXPIRES_IN * 60,
    ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, False, 'lax')
    
    return {'access_token': access_token}

@router.get('/logout',status_code=status.HTTP_200_OK)
async def logout(response: Response, Authorize: AuthJWT = Depends(), user_id: str = Depends(oauth2.require_user)):
    Authorize.unset_jwt_cookies()
    response.set_cookie("logged_in","",-1)
    return {"status": "success"}
