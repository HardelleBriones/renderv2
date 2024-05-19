from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.storage.docstore.mongodb import MongoDocumentStore
from llama_index.core import Document
import os
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.core import Document
import pymongo
from llama_index.embeddings.openai import OpenAIEmbedding
from typing import List
from dotenv import load_dotenv
load_dotenv()

class IngestDataService():
    def __init__(self):
        self.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
        self.MONGO_URI = os.getenv('MONGODB_CONNECTION_STRING')
    def add_data(self,course_name: str,data: List[Document],topic:str = "", chunkingallowed: int = 1):
        """
        Adds data to the knowledge base.
        
        Parameters:
            course_name (str): Name of the course.
            data (List[Document]): List of Document objects to be added.
            topic (str, optional): Topic of the data. Defaults to "".
            chunkingallowed (int, optional): Flag indicating whether chunking is allowed. Defaults to 1.
        """
        try:
            if not self.MONGO_URI:
                raise ValueError("MongoDB URI is required.")
            
            
            mongodb_client = pymongo.MongoClient(self.MONGO_URI)
            for doc in data:
                doc.metadata["topic"] = topic
            
            if chunkingallowed ==1:
                splitter = SentenceSplitter(
                    chunk_size=512,
                    chunk_overlap=10,
                )
                nodes = splitter.get_nodes_from_documents(data)
            else:
                nodes = data
            
            #create a vector index
            store = MongoDBAtlasVectorSearch(mongodb_client,db_name="vector", collection_name=course_name)
            storage_context_vector = StorageContext.from_defaults(vector_store=store)
            VectorStoreIndex(nodes, storage_context=storage_context_vector, embed_model=self.embed_model)

            #add to docstore
            storage_context_docstore = StorageContext.from_defaults(
                docstore=MongoDocumentStore.from_uri(uri=self.MONGO_URI, namespace=course_name, db_name="docstore"),
                )
            storage_context_docstore.docstore.add_documents(nodes)
        
            print("Successfully Added to the Knowledge base")
        except Exception as e:
            raise Exception("Error in adding data: "+str(e))

 