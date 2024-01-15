from datetime import datetime, timedelta
from fastapi import APIRouter, Response, status, Depends, Request, HTTPException
from pymongo.collection import ReturnDocument
from app import schemas
from app.oauth2 import require_user
from app.database import Post
from app.serializers.postSerializers import postEntity, postListEntity
from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError

router = APIRouter()

#Get All Posts
@router.get("/")
async def get_posts(limit: int = 10, page: int = 1, search: str = "", user_id: str = Depends(require_user)):
    skip = (page - 1) * limit
    pipeline = [
        {'$match': {}},
        {'$lookup': {'from': 'users', 'localField': 'user','foreignField': '_id', 'as': 'user'}},
        {'$unwind': '$user'},
        {
            '$skip': skip
        }, 
        {
            '$limit': limit
        }
    ]
    posts = postListEntity(Post.aggregate(pipeline))
    return {'status': 'success', 'results': len(posts), 'posts': posts}

@router.post("/",status_code=status.HTTP_201_CREATED)
async def create_post(post: schemas.CreatePostSchema, user_id: str = Depends(require_user)):
    post.user = ObjectId(user_id)
    post.created_at = datetime.utcnow()
    post.updated_at = post.created_at
    try:
        result = Post.insert_one(dict(post))
        pipeline = [
            {"$match": {"_id": result.inserted_id}},
            {"$lookup": {"from" : "users", "localField": "user",
                "foreignField":"_id","as":"user"}},
            {"$unwind":"$user"}
        ]
        new_post = postListEntity(Post.aggregate(pipeline))[0]
        return new_post
    except DuplicateKeyError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                        detail=f"Post with title: "{post.title}"already exists")
    
