from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

class User(BaseModel):
    """
    Container for a single user record.
    """
    name: str
    school_id: str
    email: EmailStr
    department: str
    account_type: str 

class TokenData(BaseModel):
    id: Optional[str] = None

class Login(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class Message(BaseModel):
    message_id: str 
    user_query:str
    ai_response: str
    user_reaction: Optional[int] = 0
    timestamp: datetime = datetime.utcnow()

class Conversation(BaseModel):
    user_id: str
    created_at: datetime = datetime.utcnow()
    subject: str
    messages: List[Message] = []


class FacebookData(BaseModel):
    post_id: str
    post_created: str
    content: str
        

class Text_knowledgeBase(BaseModel):
    topic: str
    text: str


class UserCreate(User):
    """
    Schema for creating a new user.
    """
    password: str

class UserUpdate(BaseModel):
    name: str
    email: EmailStr



class MessageCountResponse(BaseModel):
    subject: str
    message_count: int

class ConversationCountResponse(BaseModel):
    subject: str
    conversation_count: int



class FeedBack(BaseModel):
    user_id: str
    subject: str
    status: str


class FacebookDateIngested(BaseModel):
    total_ingested: int



