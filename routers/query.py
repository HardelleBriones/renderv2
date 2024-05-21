from fastapi import Depends, status, HTTPException, APIRouter
from services.chat_services import ChatEngineService
from services.memory_services import ChatHistory
from llama_index.core.response_synthesizers import ResponseMode
from llama_index.core import get_response_synthesizer
from data_definitions.constants import SYSTEM_MESSAGE
from llama_index.core.postprocessor import PrevNextNodePostprocessor
from services.knowledge_base_services import KnowledgeBaseService

#services
kb_services = KnowledgeBaseService()
chat_services = ChatEngineService()

router = APIRouter(
    prefix="/query",
    tags=["query"]
)    


@router.get("/fusion_retriever/")
def fusion_retriever_bm25(query: str, course_name: str, user: str):
    """
    Endpoint to perform a query using a fusion retriever (BM25 and vector retriever) and interact with a chat engine.

    Parameters:
    - query (str): The query string provided by the user.
    - course_name (str): The name of the course to search within.
    - user (str): The user ID.

    Returns:
    - str: The response from the chat engine.

    Raises:
    - HTTPException: If the course is not found or any other error occurs.
    """
    try: 
        # Check if the course exists
        if course_name not in kb_services.get_all_course():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{course_name} not found")
        
        #create vector retriever
        index = chat_services.get_vector_index(course_name)
        vector_retriever = index.as_retriever(similarity_top_k=3)

        #create bm25 retriever
        docstore = chat_services.get_docstore(course_name)
        bm25_retriever = chat_services.create_bm25_retriever(docstore)

        #create fusion retriever
        fusion_retriever =  chat_services.query_fusion_retriever(vector_retriever,bm25_retriever)
        
        #instantiate Chathistory for storing and retrieving convertsations
        user_conversation = ChatHistory(subject=course_name,user_id=user)

        #retrieve chathistory
        chat_history =  user_conversation.get_chat_history()

        #create CondensePlusContextChatEngine
        chat_engine = chat_services.create_CondensePlusContextChatEngine(fusion_retriever,chat_history,docstore,course_name)
        
        #chat with the chatbot
        response = chat_engine.chat(query)

        #store conversation
        user_conversation.add_message(query,str(response))

        return str(response)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
