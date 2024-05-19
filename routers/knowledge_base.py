from fastapi import status, HTTPException, Response, APIRouter, Depends
from authentication import oauth2
from typing import List
from data_definitions.schemas import FacebookData
from services.knowledge_base_services import KnowledgeBaseService
from services.facebook_services import FacebookService

#services
fb_sevice = FacebookService()
kb_service = KnowledgeBaseService()

router = APIRouter(
    prefix="/knowledge_base",
    tags=["knowledge_base"]
)    


@router.get("/get_files/")
def get_course_files(course_name:str):
    """
    Endpoint to retrieve all files associated with a specific course.

    Parameters:
    - course_name (str): The name of the course.

    Returns:
    - List of files if found.
    - HTTP 204 if no files or course are found.
    - HTTP 404 if the course is not found (ValueError).
    - HTTP 500 for any other server errors.
    """
    try:
        result = kb_service.get_all_files(course_name)
        if result:
            return result
        else:
            raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No files or course found")
    except ValueError as e:
        # Raise an HTTPException with status code 404 (Not Found) if the course is not found
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 

@router.get("/get_course/")
def get_course():
    """
    Endpoint to retrieve a list of all available courses.

    Returns:
    - List of courses if found.
    - HTTP 204 if no courses are found.
    - HTTP 404 if a ValueError occurs.
    - HTTP 500 for any other server errors.
    """
    try:
   
        result = kb_service.get_all_course()
        if result:
            return result
        else:
            raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
    except ValueError as e:
        # Raise an HTTPException with status code 404 (Not Found) if the course is not found
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 

@router.get("/get_facebook_posts/", response_model=List[FacebookData])
def get_ingested_facebook_post(course_name: str):
    """
    Endpoint to retrieve ingested Facebook posts for a specific course.

    Parameters:
    - course_name (str): The name of the course.

    Returns:
    - List of FacebookData if found.
    - HTTP 204 if no posts are found.
    - HTTP 500 for any other server errors.
    """
    try:
   
        posts = fb_sevice.get_ingested_facebook_post_by_course(course_name)
        if posts:
            facebook_posts = []
            for post in posts:
                facebook_post = FacebookData(
                    post_id=post['post_id'],
                    post_created=post['post_created'],
                    content=post['content']
                )
                facebook_posts.append(facebook_post)

            return facebook_posts
        else:
            raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 
    
@router.delete("/delete_file/")
def delete_course_files(course_name: str, file_name: str):  
    """
    Endpoint to delete a specific file from a course.

    Parameters:
    - course_name (str): The name of the course.
    - file_name (str): The name of the file to be deleted.

    Returns:
    - HTTP 204 if the file is successfully deleted.
    - HTTP 404 if the course or file is not found.
    - HTTP 500 for any other server errors.
    """
    try:
        if not course_name in kb_service.get_all_course():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{course_name} not found")

        if file_name in kb_service.get_all_files(course_name):
            kb_service.delete_file(course_name,file_name)
            kb_service.delete_course_file(course_name,file_name)
            if file_name.startswith("facebook_post_id_"):
                fb_sevice.delete_post_from_course(course_name,file_name)
            
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{file_name} not found")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except ValueError as e:
        # Raise an HTTPException with status code 404 (Not Found) if the course is not found
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 
   

















    