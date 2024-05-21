from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
)
from llama_index.core.chat_engine import CondensePlusContextChatEngine, ContextChatEngine
from llama_index.core import get_response_synthesizer
from llama_index.core.postprocessor import PrevNextNodePostprocessor
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.storage.docstore.mongodb import MongoDocumentStore
import os
from llama_index.core.response_synthesizers import ResponseMode
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
import pymongo
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.tools import QueryEngineTool,ToolMetadata
from llama_index.agent.openai import OpenAIAgent
from llama_index.llms.openai import OpenAI
from data_definitions.constants import SYSTEM_MESSAGE
from typing import List
from dotenv import load_dotenv
load_dotenv()

class ChatEngineService():
    """
    Service class for managing chat engine functionalities and components.
    """

    def __init__(self): 
        self.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
        self.llm = OpenAI(temperature=0, model="gpt-3.5-turbo-0125")
        self.MONGO_URI = os.getenv('MONGODB_CONNECTION_STRING')
    def get_vector_index(self,course_name):
        """
        Retrieves the vector index for a specified course.

        Parameters:
            course_name (str): Name of the course.

        Returns:
            VectorIndex: The vector index for the specified course.
        """
        try:
            client = pymongo.MongoClient(self.MONGO_URI)
            vector_store = MongoDBAtlasVectorSearch(
                client,
                db_name="vector",
                collection_name=course_name,
                index_name=course_name
            )
            index = VectorStoreIndex.from_vector_store(vector_store)
            return index
        except Exception as e:
            raise Exception("Error in getting vector index: " + str(e))
    def get_docstore(self,course_name):
        """
        Retrieves the  docstore for a specified course.

        Parameters:
            course_name (str): Name of the course.

        Returns:
            MongoDocumentStore: The document store for the specified course.
        """
        try:

            storage = StorageContext.from_defaults(
                    docstore=MongoDocumentStore.from_uri(uri=self.MONGO_URI, namespace=course_name, db_name="docstore"),
                    )
            return storage.docstore
        except Exception as e:
            raise Exception("Error in getting doc store: " + str(e))

    def create_bm25_retriever(self,docstore):
        """
        Creates a BM25 retriever for a specified document store.

        Parameters:
            docstore: The document store.

        Returns:
            BM25Retriever: The BM25 retriever.
        """
        try: 
            bm25_retriever = BM25Retriever.from_defaults(
            docstore=docstore, similarity_top_k=3
            )
            return bm25_retriever
        except Exception as e:
            raise Exception("Error in creating bm25 retriever: " + str(e))

    def query_fusion_retriever(self,vector_retriever, bm25_retriever):
        """
        Creates a query fusion retriever.

        Parameters:
            vector_retriever (VectorStoreIndex): The vector retriever.
            bm25_retriever (BM25Retriever): The BM25 retriever.

        Returns:
            QueryFusionRetriever: The query fusion retriever.
        """
        try:
            retriever = QueryFusionRetriever(
            [vector_retriever, bm25_retriever],
            similarity_top_k=4,
            num_queries=1,  # set this to 1 to disable query generation
            mode="reciprocal_rerank",
            use_async=True,
            verbose=True,
            # query_gen_prompt="...",  # we could override the query generation prompt here
            )
            
            return retriever
        except Exception as e:
            raise Exception("Error in creating fusion retriever: " + str(e))

    def create_query_engine_tool(self,vector_query_engine,name: str):
        """
        Creates a query engine tool.

        Parameters:
            vector_query_engine (VectorStoreIndex): The vector query engine.
            name (str): The name of the tool.

        Returns:
            List[QueryEngineTool]: The query engine tool.
        """
        # setup base query engine as tool
        query_engine_tools = [
            QueryEngineTool(
                query_engine=vector_query_engine,
                metadata=ToolMetadata(
                    name=name,
                    description= f"Provides information about  {name} "
                        "Use a detailed plain text question as input to the tool."
                ),
            ),
        ]
        return query_engine_tools


    def create_agent_mono(self,query_engine,course_name):
        """
        Creates an openai agent.

        Parameters:
            query_engine (VectorStoreIndex): The query engine.
            course_name (str): The name of the course.

        Returns:
            OpenAIAgent: The agent.
        """
        try:
            query_engine_tool = QueryEngineTool(
                query_engine=query_engine,
                metadata=ToolMetadata(
                    name=course_name,
                    description=(
                        f"Provides information about the {course_name} "
                        "Use a detailed plain text question as input to the tool."
                    ),
                ), 
            ),
            agent = OpenAIAgent.from_tools(
                    query_engine_tool,
                    llm=self.llm,
                    verbose=True,
                    
                    system_prompt = f"""\
            You are an agent designed to answer queries about {course_name} class.
            Your primary goal is to provide clear and concise explanations, offer helpful resources or examples when necessary, 
            Use the context and your own extensive knowledge to craft responses that are personalized and comprehensive, ensuring that students receive the most insightful answers possible
            If the query is not related to the class then respond by saying \"I am desigen to answer queries about {course_name}\"
            The exception is if their is a context provided by the Class_{course_name} then you can use the context to answer the question.
        """

        , 
        )
            return agent
        except Exception as e:
            raise Exception("Error in creating agent: " + str(e))

    def create_CondensePlusContextChatEngine(self,retriever,chat_history,docstore,course_name:str):
        """
        Creates an instance of CondensePlusContextChatEngine with the specified parameters.

        Parameters:
        - retriever: The retriever object used to fetch relevant documents.
        - chat_history: The chat history to be used by the chat engine.
        - docstore: The document store containing the documents to be used for context.
        - course_name (str): The name of the course, used to format the system prompt.
        Returns:
        - chat_engine: An instance of CondensePlusContextChatEngine configured with the provided parameters.
        """
        try:

            response_synthesizer = get_response_synthesizer(
            response_mode=ResponseMode.TREE_SUMMARIZE
            )
            chat_engine = CondensePlusContextChatEngine.from_defaults(
                retriever,
                llm=self.llm,
                chat_history=chat_history,
                system_prompt=SYSTEM_MESSAGE.format(course_name=course_name.replace("_", " ")),
                context_prompt=( 
                        "You are a chatbot, able to have normal interactions"
                        "Here are the relevant documents for the context:\n"
                        "{context_str}"
                        "\nInstruction: Use the previous chat history, or the context above, to interact and help the user."
                        
                    ),
                response_synthesizer = response_synthesizer,
                verbose=False,
            )
            return chat_engine
        except Exception as e:
            raise Exception("Error in creating CondensePlusContextChatEngine: " + str(e))







