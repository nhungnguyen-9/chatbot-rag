import sys
import os
import io
import streamlit as st
import boto3

# Thêm path để import module nội bộ
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.auth import CognitoAuth
from app.rag_chain import create_rag_chain, query_rag_chain, query_with_agent
from app.vector_store import get_vector_store, index_document
from app.utils import extract_text_from_pdf
from app.config import S3_BUCKET_NAME
from frontend.auth_ui import show_login_ui
from frontend.register_ui import show_register_ui

# S3 client
s3_client = boto3.client("s3")

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

    # Giao diện upload tài liệu
    st.subheader("Upload Document")
    uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

    if uploaded_file:
        try:
            # Đọc nội dung file vào buffer để dùng nhiều lần
            file_bytes = uploaded_file.read()
            file_buffer_for_pdf = io.BytesIO(file_bytes)
            file_buffer_for_s3 = io.BytesIO(file_bytes)

            # Upload lên S3
            s3_client.upload_fileobj(file_buffer_for_s3, S3_BUCKET_NAME, uploaded_file.name)

            # Trích xuất text từ PDF
            text = extract_text_from_pdf(file_buffer_for_pdf)

            # Index vào OpenSearch
            vector_store = get_vector_store()
            index_document(vector_store, text)

            st.success("Document uploaded and indexed successfully!")
        except Exception as e:
            st.error(f"Failed to upload/index document: {str(e)}")

    # Giao diện chat
    st.subheader("Chat with the Bot")
    use_agent = st.checkbox("Use React Agent (web search, weather, etc.)", value=False)
    stream_response = st.checkbox("Stream Response", value=True)

    user_query = st.text_input("Ask a question:")
    if user_query:
        if use_agent:
            st.write("**Answer (React Agent):**")
            response_container = st.empty()
            full_response = ""
            for chunk in query_with_agent(user_id, user_query, streaming=stream_response):
                if stream_response:
                    full_response += chunk
                    response_container.write(full_response)
                else:
                    full_response = chunk
                    response_container.write(full_response)
        else:
            rag_chain = create_rag_chain(user_id, streaming=stream_response)
            st.write("**Answer (RAG):**")
            response_container = st.empty()
            full_response = ""
            for result in query_rag_chain(rag_chain, user_id, user_query, streaming=stream_response):
                if stream_response:
                    full_response += result
                    response_container.write(full_response)
                else:
                    response, sources = result  # Unpack tuple
                    response_container.write(response)
                    st.write("**Sources:**", [doc.page_content for doc in sources])
