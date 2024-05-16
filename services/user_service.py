from pymongo import MongoClient
from datetime import datetime
from data_definitions.schemas import UserCreate, UserUpdate
from authentication.utils import hash
from dotenv import load_dotenv
load_dotenv()
import os
# Replace with your MongoDB connection string
connection_string = os.getenv('MONGODB_CONNECTION_STRING')

# Connect to MongoDB
client = MongoClient(connection_string)

# Get the database and collection
# db = client["chatbot"]
# collection = db["users"]

class UserService():
  def __init__(self):
        MONGO_URI = os.getenv("MONGODB_CONNECTION_STRING")
        client = MongoClient(MONGO_URI)
        db = client["chatbot"]
        self.collection = db["users"]

  def create_user(self,user: UserCreate):
    """
    Creates a new user in the database.

    Args:
        user: User data to create.
    """
    existing_user = self.collection.find_one({"school_id": user.school_id})
    if existing_user:
      return {"error": "School ID already exists"}
    hash_password = hash(user.password)
    user.password = hash_password
    user_data = user.dict()
    user_data["created_at"] = datetime.utcnow()  # Set the current timestamp
    
    self.collection.insert_one(user_data)
    return user_data


  def get_all_users(self):
    """
    Retrieves all users from the database.
    """
    users = list(self.collection.find())
    if users:
      print("Users:")
      return users
    else:
      return None


  def get_user_by_email(self,email: str):
    """
    Retrieves a user by school ID from the database.

    Args:
        school_id: User's school identifier to search for.
    """
    user = self.collection.find_one({"email": email})
    if user:
      return user
    else:
      return None

  def update_user(self,school_id: str, new_data: UserUpdate):
    """
    Updates an existing user's data in the database based on school ID.

    Args:
        school_id: User's school identifier to update.
        new_data: Dictionary containing new user data to update.
    """
    result = self.collection.update_one(
        {"school_id": school_id}, {"$set": new_data}
    )
    updated_user = self.collection.find_one({"school_id": school_id})
    return updated_user



  def delete_user(self,school_id: str):
    """
    Deletes a user from the database based on school ID.

    Args:
        school_id: User's school identifier to delete.
    """
    result = self.collection.delete_one({"school_id": school_id})
    return result.deleted_count 
