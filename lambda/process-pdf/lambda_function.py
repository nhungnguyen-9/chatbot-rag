import os
import json
import io
from PyPDF2 import PdfReader
from langchain_community.vectorstores.opensearch_vector_search import OpenSearchVectorSearch
from langchain_aws import BedrockEmbeddings
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3

# Initialize S3 and Bedrock clients
s3_client = boto3.client('s3')
bedrock_client = boto3.client('bedrock-runtime', region_name='ap-southeast-1')

region = 'ap-southeast-1'
service = 'es'

def get_awsauth():
    session = boto3.Session()
    credentials = session.get_credentials().get_frozen_credentials()
    return AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        region,
        service,
        session_token=credentials.token
    )

def test_opensearch_connection():
    host = os.environ['OPENSEARCH_ENDPOINT'].replace("https://", "").replace("http://", "")
    awsauth = get_awsauth()

    client = OpenSearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )

    try:
        info = client.info()
        print("✅ Connected to OpenSearch. Cluster info:", info)
        return True, info
    except Exception as e:
        print("❌ Failed to connect to OpenSearch:", str(e))
        return False, str(e)

def ensure_index_exists(client, index_name):
    if not client.indices.exists(index=index_name):
        print(f"Index '{index_name}' not found. Creating it now...")
        client.indices.create(index=index_name)
    else:
        print(f"Index '{index_name}' already exists.")

def get_vector_store():
    embeddings = BedrockEmbeddings(
        client=bedrock_client,
        model_id="cohere.embed-english-v3"
    )
    return OpenSearchVectorSearch(
        opensearch_url=os.environ['OPENSEARCH_ENDPOINT'],
        index_name=os.environ['OPENSEARCH_INDEX'],
        embedding_function=embeddings.embed_query,
        http_auth=get_awsauth(),
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )

def split_text_into_chunks(text, chunk_size=1000, chunk_overlap=200):
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    return splitter.split_text(text)

def lambda_handler(event, context):
    try:
        # Test connection to OpenSearch first
        ok, result = test_opensearch_connection()
        if not ok:
            return {
                'statusCode': 403,
                'body': json.dumps(f'Failed to connect to OpenSearch: {result}')
            }

        # Get bucket and file key from event
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']
        file_name = os.path.basename(key)

        # Read PDF from S3
        response = s3_client.get_object(Bucket=bucket, Key=key)
        pdf_file = response['Body'].read()

        reader = PdfReader(io.BytesIO(pdf_file))
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text

        # Prepare OpenSearch client
        host = os.environ['OPENSEARCH_ENDPOINT'].replace("https://", "").replace("http://", "")
        index_name = os.environ['OPENSEARCH_INDEX']
        awsauth = get_awsauth()
        client = OpenSearch(
            hosts=[{'host': host, 'port': 443}],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )

        # Ensure index exists
        ensure_index_exists(client, index_name)

        # Embed and index document
        vector_store = get_vector_store()
        chunks = split_text_into_chunks(text)
        vector_store.add_texts(chunks)

        return {
            'statusCode': 200,
            'body': json.dumps(f'Successfully indexed {file_name} into OpenSearch')
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error processing file: {str(e)}')
        }
