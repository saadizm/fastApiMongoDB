from datetime import datetime
from pydantic import BaseModel, EmailStr, constr
from bson.objectid import ObjectId
from typing import Union, List


class UserBaseSchema(BaseModel):
    name: str
    email: str
    photo: str
    role: str
    created_at: datetime
    updated_at: datetime


    class Config:
        orm_model = True

class CreateUserSchema(UserBaseSchema):
    password: constr(min_length=8)
    passwordConfirm: str
    verified: bool = False


class LoginUserSchema(BaseModel):
    email: EmailStr
    password: constr(min_length=8)


class UserResponseSchema(UserBaseSchema):
    id: str


class UserResponse(BaseModel):
    status: str
    user: UserResponseSchema


class FilteredUserResponse(UserBaseSchema):
    id: str

class PostBaseSchema(BaseModel):
    title: str
    content: str
    category: str
    image: str
    created_at: datetime 
    updated_at: datetime 
    
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitary_types_allowed = True
        json_encoders = {ObjectId: str}

class CreatePostSchema(PostBaseSchema):
    user: ObjectId 
    
class PostResponse(PostBaseSchema):
    id: str
    user: FilteredUserResponse
    created_at: datetime
    updated_at: datetime
    
class UpdatePostSchema(BaseModel):
    title: Union[str, None] = None
    content: Union[str, None] = None
    category: Union[str, None] = None
    image: Union[str, None] = None
    user: Union[str, None] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ListPostResponse(BaseModel):
    status: str
    results: int
    posts: List[PostResponse]
    
    
    
