import os
import boto3
from requests_aws4auth import AWS4Auth
from opensearchpy import OpenSearch, RequestsHttpConnection
from langchain_community.vectorstores.opensearch_vector_search import OpenSearchVectorSearch
from langchain_aws import BedrockEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

OPENSEARCH_ENDPOINT = os.getenv("OPENSEARCH_ENDPOINT")
OPENSEARCH_INDEX = os.getenv("OPENSEARCH_INDEX")
AWS_REGION = "ap-southeast-1"
AWS_SERVICE = "es"

def get_bedrock_client():
    return boto3.client('bedrock-runtime', region_name=AWS_REGION)

def get_aws_auth():
    session = boto3.Session()
    credentials = session.get_credentials().get_frozen_credentials()
    return AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        AWS_REGION,
        AWS_SERVICE,
        session_token=credentials.token
    )

def ensure_index_exists():
    awsauth = get_aws_auth()
    host = OPENSEARCH_ENDPOINT.replace("https://", "").replace("http://", "")
    client = OpenSearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )

    mapping = {
        "mappings": {
            "properties": {
                "vector_field": {
                    "type": "knn_vector",
                    "dimension": 1024
                },
                "content": {
                    "type": "text"
                }
            }
        }
    }

    if client.indices.exists(index=OPENSEARCH_INDEX):
        print(f"Index '{OPENSEARCH_INDEX}' đã tồn tại")
    else:
        client.indices.create(index=OPENSEARCH_INDEX, body=mapping)
        print(f"Đã tạo index '{OPENSEARCH_INDEX}' với mapping vector_field")

def get_vector_store():
    bedrock_client = get_bedrock_client()
    embeddings = BedrockEmbeddings(
        client=bedrock_client,
        model_id="cohere.embed-english-v3"
    )
    awsauth = get_aws_auth()
    vector_store = OpenSearchVectorSearch(
        opensearch_url=OPENSEARCH_ENDPOINT,
        index_name=OPENSEARCH_INDEX,
        embedding_function=embeddings,
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        vector_field="vector_field"
    )
    return vector_store

def split_text_into_chunks(text, chunk_size=1000, chunk_overlap=200):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    return splitter.split_text(text)

def index_document(text):
    ensure_index_exists()
    vector_store = get_vector_store()
    chunks = split_text_into_chunks(text)
    vector_store.add_texts(chunks)
    print(f"Đã index {len(chunks)} chunks vào OpenSearch")

