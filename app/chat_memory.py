import boto3
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import DynamoDBChatMessageHistory
from .config import DYNAMODB_TABLE_NAME

class CustomDynamoDBChatMessageHistory(DynamoDBChatMessageHistory):
    def __init__(self, table_name, session_id):
        super().__init__(
            table_name=table_name,
            session_id=session_id,
            boto3_session=boto3.Session(region_name="ap-southeast-1")
        )

    def messages(self):
        print(f"GetItem Key: {self.key}")
        return super().messages()

def get_memory(user_id):
    if not user_id or not isinstance(user_id, str):
        raise ValueError(f"Invalid user_id: {user_id}")
    try:
        chat_history = CustomDynamoDBChatMessageHistory(
            table_name=DYNAMODB_TABLE_NAME,
            session_id=user_id
        )
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            chat_memory=chat_history,
            return_messages=True,
        )
        return memory
    except Exception as e:
        print(f"Error in get_memory: {str(e)}")
        raise
