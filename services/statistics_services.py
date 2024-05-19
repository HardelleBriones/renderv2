from datetime import datetime, timezone
from pymongo import MongoClient
import os

class StatisticsServices:
    """
    Class providing methods to retrieve statistical information from a MongoDB database containing chat history data.
    """
    def __init__(self,subject:str):
        """
        Initializes the StatisticsServices object.

        Parameters:
            subject (str): Name of the subject for which the chat history is being analyzed.
        """
        MONGO_URI = os.getenv("MONGODB_CONNECTION_STRING")
        client = MongoClient(MONGO_URI)
        db = client["chat_history"]
        self.conversations = db[subject]
    def count_messages_in_date_range(self,start_date: datetime, end_date: datetime) -> int:
        """
        Counts the number of messages within the specified date range in the chat history for the given subject.

        Parameters:
            start_date (datetime): Start date of the date range.
            end_date (datetime): End date of the date range.

        Returns:
            int: Total count of messages within the specified date range.
        """
        try:
            pipeline = [
                {"$unwind": "$messages"},
                {"$match": {"messages.timestamp": {"$gte": start_date, "$lte": end_date}}},
                {"$count": "message_count"}
            ]
            result = list(self.conversations.aggregate(pipeline))
            if result:
                return result[0]['message_count']
            return 0
        except Exception as e:
            print(f"Error counting messages: {e}")
            return 0
    def count_total_conversations(self) ->int:
        """
        Counts the total number of conversations in the chat history for the given subject.

        Returns:
            int: Total count of conversations in the chat history for the given subject.
        """
        try:
            result=self.conversations.count_documents({})
            return result
        except Exception as e:
            print(f"Error counting conversations: {e}")

# if __name__ == "__main__":
#     stat = StatisticsServices("Wild_Cats_Innovation_Labs")
#     # Count messages in the last 2 days
#     start_date = datetime(2024, 5, 17, tzinfo=timezone.utc)
#     print(start_date)
#     end_date = datetime(2024, 5, 19, tzinfo=timezone.utc)
#     message_count = stat.count_messages_in_date_range(start_date, end_date)
#     print(f"Number of messages in the last 2 days: {message_count}")