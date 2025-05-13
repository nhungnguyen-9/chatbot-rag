import boto3
from .config import AWS_REGION

def get_bedrock_client():
    return boto3.client(
        service_name="bedrock-runtime",
        region_name=AWS_REGION
    )