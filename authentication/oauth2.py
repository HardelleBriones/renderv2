from jose import JWTError
import jwt
from datetime import datetime, timedelta
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pymongo import MongoClient
import os
from data_definitions.schemas import Token, TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')
# Replace with your MongoDB connection string
connection_string = os.getenv("MONGODB_CONNECTION_STRING")

# Connect to MongoDB
client = MongoClient(connection_string)
# SECRET_KEY
# Algorithm
# Expriation time
# Get the database and collection
db = client["chatbot"]
collection = db["users"]

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES =  os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

# Convert ACCESS_TOKEN_EXPIRE_MINUTES to an integer
if ACCESS_TOKEN_EXPIRE_MINUTES is not None:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(ACCESS_TOKEN_EXPIRE_MINUTES)
else:
    # Provide a default value if the environment variable is not set
    ACCESS_TOKEN_EXPIRE_MINUTES = 0


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_access_token(token: str, credentials_exception):

    try:

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("email")
        if id is None:
            raise credentials_exception
        token_data = TokenData(id=id)
    except JWTError:
        raise credentials_exception

    return token_data


def get_current_user(token: int = Depends(oauth2_scheme)):
  
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
   
    token = verify_access_token(token, credentials_exception)

    #user = db.query(models.User).filter(models.User.id == token.id).first()
    user = collection.find_one({"email": token.id})
    return user
