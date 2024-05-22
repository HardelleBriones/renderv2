from pymongo import MongoClient
import uuid
from llama_index.core.llms import ChatMessage
from data_definitions.schemas import Message, FeedBack
import os

from typing import List
from dotenv import load_dotenv
load_dotenv()
class ConversationManager:
    """
    Class for managing conversation in a MongoDB database.
    """
    def __init__(self):
        MONGO_URI = os.getenv("MONGODB_CONNECTION_STRING")
        self.client = MongoClient(MONGO_URI)


    def get_messages(self,subject:str, user_id: str) -> List[Message]:
        """
        Retrieves messages for a given subject and user ID from the database.

        Args:
            subject (str): The subject of the conversation.
            user_id (str): The user ID for which to retrieve messages.

        Returns:
            List[Message]: A list of messages for the given subject and user ID.
        """
        try:
            db = self.client["chat_history"]
            conversations = db[subject]
            conversation = conversations.find_one({"user_id": user_id})
            if conversation:
                return [Message(**msg) for msg in conversation.get("messages", [])]
            else:
                print("Conversation not found")
                return []
        except Exception as e:
            print(f"Error retrieving messages: {e}")
            return []
        
    def add_feedback(self,feedback:FeedBack):
        """
        Adds feedback to the database.

        Args:
            feedback (FeedBack): The feedback data to be added.
        """
        try:
            db = self.client["feedback"]
            conversation = db[feedback.subject]
            new_conversation_data = FeedBack(user_id=feedback.user_id, subject=feedback.subject, status="New")
            conversation.insert_one(new_conversation_data.model_dump())
        except Exception as e:
            raise

    def update_feedback_status(self, feedback: FeedBack) -> FeedBack:
        """
        Updates the status of a feedback entry in the database.

        Args:
            feedback (FeedBack): The feedback data with updated status.

        Returns:
            FeedBack: The updated feedback data.
        """
        try:
            db = self.client["feedback"]
            collection = db[feedback.subject]
            result = collection.update_one(
                {"user_id": feedback.user_id},
                {"$set": {"status": feedback.status}}
            )
            if result.matched_count > 0:
                updated_feedback = collection.find_one({"user_id": feedback.user_id})
                return updated_feedback
            else:
                raise ValueError(f"No feedback found for user_id {feedback.user_id}")
        except Exception as e:
            raise
    def check_user_id_exists(self, user_id: str, subject:str) -> bool:
        """
        Checks if a user ID exists for a given subject in the database.

        Args:
            user_id (str): The user ID to check.
            subject (str): The subject to check.

        Returns:
            bool: True if the user ID exists, False otherwise.
        """
        try:
            db = self.client["feedback"]
            collection = db[subject]
            if collection.find_one({"user_id": user_id}):
                return True
            return False
        except Exception as e:
            raise
    def check_subject_exists(self, subject: str) -> bool:
        """
        Checks if a subject exists in the feedback database.

        Args:
            subject (str): The subject to check.

        Returns:
            bool: True if the subject exists, False otherwise.
        """
        try:
            db = self.client["feedback"]
            collections = db.list_collection_names()
            return subject in collections
        except Exception as e:
            raise

    def get_all_feedback_for_subject(self, subject: str, status: str) -> List[FeedBack]:
        """
        Retrieves all feedback entries for a given subject and status.

        Args:
            subject (str): The subject of the feedback.
            status (str): The status of the feedback to filter by.

        Returns:
            List[FeedBack]: A list of feedback entries matching the subject and status.
        """
        try:
            db = self.client["feedback"]
            collection = db[subject]
            query = {"status": status} if status else {}
            feedbacks = collection.find(query)
            return [FeedBack(**feedback) for feedback in feedbacks]
        except Exception as e:
            raise