from datetime import datetime, timezone
from pymongo import MongoClient
import os

class StatisticsServices:
    def __init__(self,course_name:str):
        MONGO_URI = os.getenv("MONGODB_CONNECTION_STRING")
        client = MongoClient(MONGO_URI)
        db = client["chat_history"]
        self.conversations = db[course_name]
    def count_messages_in_date_range(self,start_date: datetime, end_date: datetime) -> int:
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