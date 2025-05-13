from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_community.embeddings import BedrockEmbeddings
from .bedrock import get_bedrock_client
from .config import OPENSEARCH_ENDPOINT
from langchain.text_splitter import RecursiveCharacterTextSplitter

def get_vector_store():
    bedrock_client = get_bedrock_client()
    embeddings = BedrockEmbeddings(
        client=bedrock_client,
        model_id="cohere.embed-english-v3"
    )

    vector_store = OpenSearchVectorSearch(
        opensearch_url=OPENSEARCH_ENDPOINT,
        index_name="chatbot-index",
        embedding_function=embeddings
    )

    return vector_store

def split_text_into_chunks(text, chunk_size=1000, chunk_overlap=200):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    return splitter.split_text(text)

def index_document(vector_store, document_text):
    chunks = split_text_into_chunks(document_text)
    vector_store.add_texts(chunks)
