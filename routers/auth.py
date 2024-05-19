from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from authentication.utils import verify
from authentication.oauth2 import create_access_token
from pymongo import MongoClient
import os
from data_definitions import schemas
from dotenv import load_dotenv
load_dotenv()
# Replace with your MongoDB connection string
connection_string = os.getenv("MONGODB_CONNECTION_STRING")

# Connect to MongoDB
client = MongoClient(connection_string)

# Get the database and collection
db = client["chatbot"]
collection = db["users"]
router = APIRouter(tags=['Authentication'])


@router.post('/login', response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint for user login, which verifies credentials and returns an access token.

    Parameters:
    - user_credentials (OAuth2PasswordRequestForm): The user's login credentials, provided by dependency injection.

    Returns:
    - Token: A dictionary containing the access token and token type.

    Raises:
    - HTTPException: If the credentials are invalid, with a 403 status code.
    """
    user = collection.find_one({"email": user_credentials.username})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    if not verify(user_credentials.password, user.get('password')):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    access_token = create_access_token(data={"email": user.get('email')})

    return {"access_token": access_token, "token_type": "bearer"}