import pymongo
from pymongo import MongoClient
from app.config import settings

print(settings.DATABASE_URL)

client = MongoClient(settings.DATABASE_URL)

try:
    conn = client.server_info()
    print(f'Connected to MongoDB {conn.get("version")}')
except Exception:
    print("Unable to connect to DB Server")

db = client[settings.MONGO_INITDB_DATABASE]
User = db.users
Post = db.posts
User.create_index([("email", pymongo.ASCENDING)], unique=True)
Post.create_index([("title", pymongo.ASCENDING)], unique=True)