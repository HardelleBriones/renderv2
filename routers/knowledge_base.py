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
    #current_user: str = Depends(oauth2.get_current_user)
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
    #current_user: str = Depends(oauth2.get_current_user)
    try:
   
        posts = fb_sevice.get_ingested_facebook_post_by_course(course_name)
        if posts:
            facebook_posts = []
            for post in posts:
                facebook_post = FacebookData(
                    post_id=post.post_id,
                    post_created=post.post_created,
                    content=post.content
                )
                facebook_posts.append(facebook_post)

            return facebook_posts
        else:
            raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 
    
@router.delete("/delete_file/")
def delete_course_files(course_name: str, file_name: str):  
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
   

















    