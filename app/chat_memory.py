from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import DynamoDBChatMessageHistory
from .config import DYNAMODB_TABLE_NAME

def get_memory(user_id):
    chat_history = DynamoDBChatMessageHistory(
        table_name=DYNAMODB_TABLE_NAME,
        session_id=user_id
    )
    memory = ConversationBufferMemory(
        chat_memory=chat_history,
        return_messages=True,
        memory_key="chat_history"
    )
    return memory