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
from datetime import datetime
from data_definitions.schemas import MessageCountResponse, ConversationCountResponse
router = APIRouter(
    prefix="/stats",
    tags=["stats"]
)    
kb_service = KnowledgeBaseService()
@router.get("/message-count", response_model=MessageCountResponse)
def get_messages_count(subject: str, start_date: datetime, end_date: datetime):
    """
    Endpoint to get the count of messages within a date range for a specific subject.

    Parameters:
    - subject (str): The name of the subject.
    - start_date (datetime): The start date of the date range.
    - end_date (datetime): The end date of the date range.

    Returns:
    - MessageCountResponse: The response containing the subject name and the message count.
    - HTTP 404 if the subject is not found.
    - HTTP 500 for any other server errors.
    """
    try:
        stats = StatisticsServices(subject)
        result = kb_service.get_all_course()
        if subject not in result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Course '{subject}' not found")
        
        total_messages = stats.count_messages_in_date_range(start_date, end_date)
        return MessageCountResponse(subject=subject,message_count=total_messages)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 
@router.get("/conversation-count-all", response_model=ConversationCountResponse)
def get_all_conversations_count(subject: str):
    """
    Endpoint to get the total count of conversations for a specific course.

    Parameters:
    - subject (str): The name of the course.

    Returns:
    - ConversationCountResponse: The response containing the course name and the conversation count.
    - HTTP 404 if the course is not found.
    - HTTP 500 for any other server errors.
    """
    try:
        courses = kb_service.get_all_course()
        if subject not in courses:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Course '{subject}' not found")
        stats = StatisticsServices(subject)
        total_conversations = stats.count_total_conversations()
        return ConversationCountResponse(course_name=subject,conversation_count=total_conversations)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 
    



@router.get("/conversation-count", response_model=ConversationCountResponse)
def get_conversations_count(subject: str, start_date: datetime, end_date: datetime):
    """
    Endpoint to get the count of messages within a date range for a specific subject.

    Parameters:
    - subject (str): The name of the subject.
    - start_date (datetime): The start date of the date range.
    - end_date (datetime): The end date of the date range.

    Returns:
    - MessageCountResponse: The response containing the subject name and the message count.
    - HTTP 404 if the subject is not found.
    - HTTP 500 for any other server errors.
    """
    try:
        stats = StatisticsServices(subject)
        result = kb_service.get_all_course()
        if subject not in result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"subject '{subject}' not found")
        
        total_messages = stats.count_conversations_in_date_range(start_date, end_date)
        return ConversationCountResponse(subject=subject,conversation_count=total_messages)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 