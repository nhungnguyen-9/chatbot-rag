import sys
import os
import io
import streamlit as st
import boto3
import time
from botocore.exceptions import ClientError

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.auth import CognitoAuth
from app.rag_chain import create_rag_chain, query_rag_chain, query_with_agent
from app.vector_store import get_vector_store
from app.utils import extract_text_from_pdf
from app.config import S3_BUCKET_NAME
from frontend.auth_ui import show_login_ui
from frontend.register_ui import show_register_ui

# S3 client
s3_client = boto3.client("s3", region_name="ap-southeast-1")

# Giao diện Streamlit
st.title("RAG Chatbot")

# Tabs đăng nhập và đăng ký
auth_tab = st.tabs(["Login", "Register"])
with auth_tab[0]:
    show_login_ui()
with auth_tab[1]:
    show_register_ui()

# Chỉ hiển thị phần còn lại nếu đã đăng nhập
if "access_token" in st.session_state:
    user_id = st.session_state["user_id"]
    credentials = st.session_state.get("credentials")  # Lấy credentials từ session state

    # Giao diện upload tài liệu
    st.subheader("Upload Document")
    uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

    if uploaded_file:
        try:
            file_bytes = uploaded_file.read()
            file_buffer = io.BytesIO(file_bytes)
            s3_client.upload_fileobj(file_buffer, S3_BUCKET_NAME, uploaded_file.name)
            st.success("Document uploaded to S3 successfully! Indexing will be handled by Lambda.")
        except Exception as e:
            st.error(f"Failed to upload document: {str(e)}")

    # Giao diện chat
    st.subheader("Chat with the Bot")
    use_agent = st.checkbox("Use React Agent (web search, weather, etc.)", value=False)
    stream_response = st.checkbox("Stream Response", value=True)

    user_query = st.text_input("Ask a question:")
    if user_query:
        if "last_query_time" in st.session_state and time.time() - st.session_state["last_query_time"] < 5:
            st.warning("Please wait a few seconds before submitting another query.")
        else:
            st.session_state["last_query_time"] = time.time()
            response_container = st.empty()
            full_response = ""

            try:
                if use_agent:
                    if user_query.lower().startswith("weather") and "last_weather" in st.session_state:
                        if time.time() - st.session_state["last_weather_time"] < 300:
                            st.write("**Answer (Cached):**")
                            response_container.write(st.session_state["last_weather"])
                        else:
                            st.write("**Answer (React Agent):**")
                            for chunk in query_with_agent(user_id, user_query, streaming=stream_response):
                                if stream_response:
                                    full_response += chunk
                                    response_container.write(full_response)
                                else:
                                    full_response = chunk
                                    response_container.write(full_response)
                            st.session_state["last_weather"] = full_response
                            st.session_state["last_weather_time"] = time.time()
                    else:
                        st.write("**Answer (React Agent):**")
                        for chunk in query_with_agent(user_id, user_query, streaming=stream_response):
                            if stream_response:
                                full_response += chunk
                                response_container.write(full_response)
                            else:
                                full_response = chunk
                                response_container.write(full_response)
                        if user_query.lower().startswith("weather"):
                            st.session_state["last_weather"] = full_response
                            st.session_state["last_weather_time"] = time.time()
                else:
                    rag_chain = create_rag_chain(user_id, streaming=stream_response)
                    st.write("**Answer (RAG):**")

                    if stream_response:
                        for chunk in query_rag_chain(rag_chain, user_id, user_query, streaming=True):
                            full_response += chunk
                            response_container.write(full_response)
                        st.write("**(Sources not available in streaming mode)**")
                    else:
                        response, sources = query_rag_chain(rag_chain, user_id, user_query, streaming=False)
                        response_container.write(response)
                        st.write("**Sources:**", [doc.page_content for doc in sources])
            except ClientError as e:
                if e.response['Error']['Code'] == 'ThrottlingException':
                    st.error("Too many requests to the AI service. Please wait a moment and try again.")
                else:
                    st.error(f"Error: {str(e)}")
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")
