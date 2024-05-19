
import requests
import os
import pymongo
from data_definitions.schemas import FacebookData
from typing import List
from dotenv import load_dotenv
load_dotenv()



class FacebookService():
    """
    Service class for interacting with Facebook posts data and MongoDB database.
    """
    def __init__(self):
        self.PAGE_ID = os.getenv("PAGE_ID")
        self.FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
        MONGO_URI = os.getenv("MONGODB_CONNECTION_STRING")
        self.client = pymongo.MongoClient(MONGO_URI)
        self.db_name = "facebook_records"


    def get_facebook_page_posts(self):
        """
        Retrieve posts from a specified Facebook page using the Graph API.

        Returns:
            dict or None: A dictionary containing the posts if the request is successful, None otherwise.
        """
            
        url = f'https://graph.facebook.com/v17.0/{self.PAGE_ID}/posts'
        params = {
            'access_token': self.FB_ACCESS_TOKEN
        }
        
        response = requests.get(url, params=params)

        
        if response.status_code == 200:
            posts = response.json()
            return posts
        else:
            print(f'Error: {response.status_code}')
            return None
        

    def add_post_to_course(self,course_name: str, fb_data: FacebookData):
        """
        Add a post to a specified course collection in the database.

        Args:
            course_name (str): The name of the course collection.
            fb_data (FacebookData): The data of the Facebook post to be added.

        Raises:
            Exception: If there is an error during the database operation.
        """
        try:
            # Access the specified database and collection
            db = self.client[self.db_name]
            facebook_collection = db[course_name]

            # Insert the Facebook data into the collection
            facebook_collection.insert_one(fb_data.dict())

        except Exception as e:
            # Raise an exception with a clear error message
            raise Exception(f"Error adding post to course {course_name}: {str(e)}")


    def delete_post_from_course(self,course_name: str, post_id: str):
        """
        Delete a post from a specified course collection in the database.

        Args:
            course_name (str): The name of the course collection.
            post_id (str): The ID of the post to be deleted.

        Raises:
            Exception: If there is an error during the database operation.
        """
        try:
            # Access the specified database and collection
            db = self.client[self.db_name] 
            facebook_collection = db[course_name]
            
            # Find and delete the post
            post = facebook_collection.find_one({'post_id': post_id})
            if post is None:
                raise Exception(f"Post with ID {post_id} not found in course {course_name}.")
            
            facebook_collection.delete_one({'post_id': post_id})
            
            if facebook_collection.count_documents({}) == 0:
                # If it's empty, delete the collection
                db.drop_collection(course_name)
                print("deleted")
            else:
                print("not deleted")
        
        except Exception as e:
            raise Exception(f"Error deleting post with ID {post_id} from course {course_name}: {str(e)}")
        

    def get_ingested_facebook_post_by_course(self,course_name:str):
        """
        Retrieves ingested Facebook posts by course name from the database.

        Parameters:
            course_name (str): Name of the course.

        Returns:
            List[dict]: List of dictionaries representing the ingested Facebook posts.
        """
        try:
            db = self.client[self.db_name] 
            facebook_collection = db[course_name]
            # Retrieve all documents from the collection
            posts = list(facebook_collection.find())
            return posts
        except Exception as e:
            raise Exception(f"Error in getting ingested posts: {str(e)}")
    
        
