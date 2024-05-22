from fastapi import Depends, status, HTTPException, Response, APIRouter, UploadFile, File
from llama_index.core import (
    SimpleDirectoryReader,
)
from llama_index.core.node_parser import SentenceSplitter
import requests
from tempfile import TemporaryDirectory
from services.evaluation_services import file_cost_embeddings
from services.statistics_services import StatisticsServices
from services.knowledge_base_services import KnowledgeBaseService
from services.conversation_services import ConversationManager
from data_definitions.schemas import Message, FeedBack
from typing import List
router = APIRouter(
    prefix="/conversation",
    tags=["conversation"]
)   

conversation_manager = ConversationManager()


@router.get("/get_messages/", response_model=List[Message])
def get_messages_by_user(subject:str, user_id:str):
    try:
        messages = conversation_manager.get_messages(subject, user_id)
        return messages
    except Exception as e:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/feedback/")
def add_user_feedback(feedback: FeedBack):
    try:
        conversation_manager.add_feedback(feedback)
        return {"message": "Feedback added successfully"}   
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.get("/feedback/{subject}", response_model=List[FeedBack])
def get_feedback(subject: str, status:str="New"):
    try:
        feedback_list  = conversation_manager.get_all_feedback_for_subject(subject,status)
        return feedback_list
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    


@router.post("/update_feedback_status/", response_model=FeedBack)
def update_user_feedback_status(feedback: FeedBack):
    try:
        subject = conversation_manager.check_subject_exists(feedback.subject)
        if not subject:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"subject: {feedback.subject} not found")
        
        user = conversation_manager.check_user_id_exists(feedback.user_id,feedback.subject)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user id: {feedback.user_id} not found")
        
        feedback = conversation_manager.update_feedback_status(feedback)
        return feedback
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


