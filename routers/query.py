from fastapi import Depends, status, HTTPException, APIRouter
from services.chat_services import ChatEngineService
from services.memory_services import ChatHistory
from llama_index.agent.openai import OpenAIAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.response_synthesizers import ResponseMode
from llama_index.core import get_response_synthesizer
from data_definitions.constants import SYSTEM_MESSAGE
from llama_index.core.chat_engine import CondensePlusContextChatEngine
from llama_index.core.postprocessor import PrevNextNodePostprocessor
from services.knowledge_base_services import KnowledgeBaseService

#services
kb_services = KnowledgeBaseService()
chat_services = ChatEngineService()

router = APIRouter(
    prefix="/query",
    tags=["query"]
)    
llm = OpenAI(temperature=0, model="gpt-3.5-turbo-0125")

@router.get("/retriever/")
def retriever(query: str, course_name: str, user: str ="user"):
     
       
    index = chat_services.get_vector_index(course_name)
    vector_retriever = index.as_retriever(similarity_top_k=2)
    #create bm25 retriever
    docstore = chat_services.get_docstore(course_name)
    bm25_retriever = chat_services.create_bm25_retriever(docstore)
    #use fusion retriever
    fusion_retriever =  chat_services.query_fusion_retriever(vector_retriever,bm25_retriever)
    # will retrieve context from specific companies


    node_postprocessor = PrevNextNodePostprocessor(docstore=docstore, num_nodes=4)
    nodes_with_scores = fusion_retriever.retrieve(query)
    for node in nodes_with_scores:
        print(f"Score: {node.score:.2f} - {node.text}...\n-----\n")
    return "ok"



      
@router.get("/")
def query_openai_agent(query: str, course_name: str):
    try: 
       
        if course_name not in kb_services.get_all_course():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{course_name} not found")
        vector = chat_services.get_vector_index(course_name)
        response_synthesizer = get_response_synthesizer(
        response_mode=ResponseMode.TREE_SUMMARIZE
        )
        query_engine_tools = chat_services.create_query_engine_tool(vector.as_query_engine(similarity_top_k=4, response_synthesizer=response_synthesizer),course_name)
        agent = OpenAIAgent.from_tools(query_engine_tools, verbose=True,llm=llm,
                                       system_prompt=SYSTEM_MESSAGE.format(course_name=course_name))
        response = agent.chat(query, tool_choice=course_name)
        # engine = vector.as_query_engine(similarity_top_k=2, response_synthesizer=response_synthesizer)
        # response = engine.query(query)
        return str(response)
    except Exception as e:
          raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

@router.get("/fusion_retriever/")
def fusion_retriever_bm25(query: str, course_name: str, user: str ="user"):
    try: 
       
        if course_name not in kb_services.get_all_course():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{course_name} not found")
            #create vector retriever
        index = chat_services.get_vector_index(course_name)
        vector_retriever = index.as_retriever(similarity_top_k=2)
        #create bm25 retriever
        docstore = chat_services.get_docstore(course_name)
        bm25_retriever = chat_services.create_bm25_retriever(docstore)
        #use fusion retriever
        fusion_retriever =  chat_services.query_fusion_retriever(vector_retriever,bm25_retriever)
        # engine_tool = create_query_engine_tool(engine,course_name)
        
        response_synthesizer = get_response_synthesizer(
        response_mode=ResponseMode.TREE_SUMMARIZE
        )
        node_postprocessor = PrevNextNodePostprocessor(docstore=docstore, num_nodes=4)
        user_conversation = ChatHistory(subject=course_name,user_id=user)
        chat_history1 =  user_conversation.get_chat_history()

        chat_engine = CondensePlusContextChatEngine.from_defaults(
            fusion_retriever,
            llm=llm,
            chat_history=chat_history1,
            system_prompt=SYSTEM_MESSAGE.format(course_name=course_name.replace("_", " ")),
            context_prompt=( 
                    "You are a chatbot, able to have normal interactions"
                    "Here are the relevant documents for the context:\n"
                    "{context_str}"
                    "\nInstruction: Use the previous chat history, or the context above, to interact and help the user."
                    
                ),
            response_synthesizer = response_synthesizer,
            node_postprocessors=[node_postprocessor],
                
            verbose=False,
        )
        response = chat_engine.chat(query)
        user_conversation.add_message(query,str(response))

        return str(response)
    except Exception as e:
          raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
   






















# chroma_client = chromadb.PersistentClient(path="../chroma_db")
# #add db_name for the course
# @router.get("/")
# def query(query: str):
#     try:
#         agents = {}
#         names = chroma_client.list_collections()
#         collections = [collection.name for collection in names]
#         for collection in collections:
#             #also add db to specify the collection
#             vector = create_vector_engine(collection)
#             summary = create_summary_engine(collection)
#             tools = create_engine_tools(vector,summary,collection)
#             agent = create_document_agent(tools,collection)
#             agents[collection] = agent
#         all_tools = convert_tool_agent(collections,agents)
#         obj_index = create_object_index(all_tools)
#         #chat_history1 =  get_chat_history("user")
#         top_agent = fnRetriever(obj_index)
#         #chat_history = chat_history1
#         response = top_agent.chat(query)
#         return str(response)
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")

# #add db_name for the course
# @router.get("/atlas")
# def query_atlas(query: str, subject:str, user: str ="user"):

#     try:
        
#         agents = {}
        
#         collections = get_collections(subject)
#         print(collections)
#         if not collections:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No subject found")
        
#         for collection in collections:
#             #also add db to specify the collection
#             vector = create_vector_engine_atlas(collection,subject)
#             summary = create_summary_engine_atlas(collection,subject)
#             tools = create_engine_tools(vector,summary,collection)
#             agent = create_document_agent(tools,collection)
#             agents[collection] = agent
#         all_tools = convert_tool_agent(collections,agents)
#         obj_index = create_object_index(all_tools)
#         #chat_history1 =  get_chat_history("user")
#         user_conversation = ChatHistory(subject=subject,user_id=user)
#         top_agent = fnRetriever(obj_index)
#         #chat_history = chat_history1
#         response = top_agent.chat(query, user_conversation.get_chat_history())
#         user_conversation.add_message(query,str(response))
#         return str(response)
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")