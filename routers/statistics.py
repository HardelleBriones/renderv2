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
def get_messages_count(course_name: str, start_date: datetime, end_date: datetime):
    try:
        stats = StatisticsServices(course_name)
        result = kb_service.get_all_course()
        if course_name not in result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Course '{course_name}' not found")
        
        total_messages = stats.count_messages_in_date_range(start_date, end_date)
        return MessageCountResponse(course_name=course_name,message_count=total_messages)
    except Exception as e:
        return {"error": str(e)}
@router.get("/conversation-count", response_model=ConversationCountResponse)
def get_conversations_count(course_name: str):
    try:
        courses = kb_service.get_all_course()
        if course_name not in courses:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Course '{course_name}' not found")
        stats = StatisticsServices(course_name)
        total_conversations = stats.count_total_conversations()
        return ConversationCountResponse(course_name=course_name,conversation_count=total_conversations)
    except Exception as e:
        return {"error": str(e)}