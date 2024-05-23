from fastapi import status, HTTPException, Response, APIRouter, UploadFile
from llama_index.core import SimpleDirectoryReader
import requests
import os
from tempfile import TemporaryDirectory
import tempfile
from llama_index.core import Document
from data_definitions.schemas import Text_knowledgeBase, FacebookData, FacebookDateIngested
import tempfile
from llama_index.core import Document
from services.facebook_services import FacebookService
from services.knowledge_base_services  import  KnowledgeBaseService
from services.ingest_data_services import IngestDataService

#services
ingest_data_service = IngestDataService()
kb_service = KnowledgeBaseService()
fb_service = FacebookService()


router = APIRouter(
    prefix="/ingest_data",
    tags=["ingest_data"]

)

#to be added arg - db_name for the course
@router.post("/uploadfile/", description="Upload file")
async def upload_file(file: UploadFile, course_name: str):
    try:
        if not kb_service.valid_index_name(course_name):
            raise ValueError("Invalid Index Name")
        file_name = file.filename
        # Create a temporary directory using a context manager
        with TemporaryDirectory() as temp_dir:
            # Save the uploaded file content to the temporary directory
            temp_file_path = f"{temp_dir}/{file.filename}"
            file_content = await file.read()  # Read the uploaded file content
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(file_content)  # Write content to temporary file
            # Process the file using SimpleDirectoryReader with the full path
            data = SimpleDirectoryReader(input_files=[temp_file_path]).load_data()

            #check if file exist
            file = kb_service.get_all_files(course_name)
            if file_name in file:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{file_name} already exist")
            
            ingest_data_service.add_data(course_name, data,file_name)
            kb_service.add_file_to_course(course_name,file_name)
        return Response(status_code=status.HTTP_200_OK, content="Successfully added to knowledge base")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

@router.post("/downloadlink/", description="Add file using link")
async def upload_file_link(download_link: str, course_name:str):
  """
  Downloads a file from the specified URL and stores it in a temporary directory.

  Args:
      url (str): The URL of the file to download.

  Returns:
      str: The path to the downloaded file or None if there was an error.
  """
  if not kb_service.valid_index_name(course_name):
            raise ValueError("Invalid Index Name")
  # Create a temporary directory
  with tempfile.TemporaryDirectory() as tmpdir:
    # Extract filename from URL, considering the possibility of query parameters
    filename = download_link.split("/")[-1].split("?")[0]  # Get last part before '?'
    #prefixed_filename = f"Topic {topic}-{filename}"  # Add the prefix

    filepath = os.path.join(tmpdir, filename)
   

    # Send a GET request to download the file
    try:
      response = requests.get(download_link, stream=True)
      response.raise_for_status()  # Raise an exception for unsuccessful downloads
    except requests.exceptions.RequestException as e:
      print(f"Error downloading file: {e}")
      return None
    content_type = response.headers.get('Content-Type')
    if content_type and not content_type.startswith('text/html'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file URL or content type")

    try:
        # Write the downloaded data to the temporary file
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        data = SimpleDirectoryReader(input_files=[filepath]).load_data()
        #nodes = SentenceSplitter(chunk_size=1024, chunk_overlap=20).get_nodes_from_documents(data)
        file_name = data[0].metadata['file_name']

        #check if file exist
        file = kb_service.get_all_files(course_name)
        if file_name in file:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{file_name} already exist")
        
        ingest_data_service.add_data(course_name, data)
        kb_service.add_file_to_course(course_name,file_name)
        return Response(status_code=status.HTTP_200_OK)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    



@router.post("/add_text_knowledge_base/", description="Add text to knowledge base")
async def add_text_knowledge_base(subject:str, metadata:Text_knowledgeBase):
    try:  
        if not kb_service.valid_index_name(subject):
            raise ValueError("Invalid Index Name")
        file_name = metadata.topic
      
         #check if file exist
        file = kb_service.get_all_files(subject)
        if file_name in file:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{file_name} already exist")


        document = Document(
        
        text=metadata.text,
        metadata={
            "file_name": file_name,
        },
        excluded_llm_metadata_keys=['file_name'],
        excluded_embed_metadata_keys=['file_name'],
        metadata_seperator="::",
        metadata_template="{key}=>{value}",
        text_template="Metadata: {metadata_str}\n-----\nContent: {content}",
        )
        
        ingest_data_service.add_data(subject, [document],metadata.topic)
        kb_service.add_file_to_course(subject,file_name)
        return Response(status_code=status.HTTP_200_OK, content="Successfully added to knowledge base")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
   


@router.post("/add_facebook_data/", description="Add facebook data to knowledge base")
async def add_facebook_data(subject:str, metadata:FacebookData):
    try:  
        if not kb_service.valid_index_name(subject):
            raise ValueError("Invalid Index Name")
        file_name = "facebook_id: "+metadata.post_id
      
         #check if file exist
        file = kb_service.get_all_files(subject)
        if file_name in file:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{file_name} already exist")


        document = Document(
        
        text=metadata.content,
        metadata={
            "file_name": file_name,
            "post_created":metadata.post_created,
        },
        excluded_llm_metadata_keys=['file_name'],
        excluded_embed_metadata_keys=['file_name'],
        metadata_seperator="::",
        metadata_template="{key}=>{value}",
        text_template="Metadata: {metadata_str}\n-----\nContent: {content}",
        )
        
        ingest_data_service.add_data(subject, [document],"This contains specific information in facebook page", 0)
        kb_service.add_file_to_course(subject,file_name)
        return Response(status_code=status.HTTP_200_OK, content="Successfully added to knowledge base")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

@router.post("/ingest_facebook_posts", response_model=FacebookDateIngested)
def ingest_facebook_data(subject: str):
    try:  
        if not kb_service.valid_index_name(subject):
            raise ValueError("Invalid Index Name")
        posts = fb_service.get_facebook_page_posts()
        files = kb_service.get_all_facebook_posts(subject)
        count =0
        skip =0
        if posts:
            for post in posts['data']:
                facebook_data = FacebookData(
                    post_id= "facebook_post_id_" + post.get('id'),
                    post_created=post.get('created_time'),
                    content=post.get('message')
                )
                #check if file exist
                if facebook_data.post_id not in files:
                    count +=1
                    document = Document(
                    text=facebook_data.content,
                    metadata={
                        "file_name": facebook_data.post_id,
                        "post_created":facebook_data.post_created,
                    },
                    excluded_llm_metadata_keys=['file_name'],
                    excluded_embed_metadata_keys=['file_name'],
                    metadata_seperator="::",
                    metadata_template="{key}=>{value}",
                    text_template="Metadata: {metadata_str}\n-----\nContent: {content}",
                    )
                    ingest_data_service.add_data(subject, [document],"This contains specific information in facebook page", 0)
                    kb_service.add_file_to_course(subject,facebook_data.post_id)
                    fb_service.add_post_to_course(subject,facebook_data)
                    print("ingested", facebook_data.post_created)
                else:
                    skip +=1
                    print("already ingested")
        return FacebookDateIngested(total_ingested=count, total_already_ingested=skip)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))











