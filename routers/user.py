from fastapi import APIRouter, Depends, status, HTTPException, Response
from data_definitions.schemas import User, UserCreate, UserUpdate
from pymongo import MongoClient
import datetime
import os
from authentication.utils import hash
from services.user_service import UserService
router = APIRouter(
    prefix="/users",
    tags=["users"]
)    

user_service = UserService()
# Replace with your MongoDB connection string
connection_string = os.getenv("MONGODB_CONNECTION_STRING")

# Connect to MongoDB
client = MongoClient(connection_string)

# Get the database and collection
db = client["chatbot"]
collection = db["users"]



@router.post("/", status_code=status.HTTP_201_CREATED, response_model=User)
async def create_user(user:UserCreate):
    """
    Creates a new user in the database.

    Args:
        user: User data to create.
    """
    existing_user = collection.find_one({"school_id": user.school_id})
    if existing_user:
        raise HTTPException(status_code=400, detail="School ID already exists")
    user_data = user_service.create_user(user)
    # user_data = user.dict()
    # #user_data["created_at"] = datetime.utcnow()  # Set the current timestamp
  
    # collection.insert_one(user_data)
    return user_data


# @router.get("/users")
# async def get_all_users():
#     users = list(db.collection.find())
#     if not users:
#        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No users found")
#     return users

@router.get("/users/{school_id}", status_code=status.HTTP_200_OK, response_model=User)
async def get_user_by_email(email: str):
    # user = collection.find_one({"school_id": school_id})
    user = user_service.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.patch("/users/{school_id}", status_code=status.HTTP_200_OK, response_model=User)
async def update_user(school_id: str, new_data: UserUpdate):
    # result = collection.update_one(
    #     {"school_id": school_id}, {"$set": new_data.dict()}
    # )
    user = user_service.update_user(school_id,new_data)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    # Retrieve and return the updated user object
   
    return user

@router.delete("/users/{school_id}")
async def delete_user(school_id: str):

    result = user_service.delete_user(school_id)
    if result == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)