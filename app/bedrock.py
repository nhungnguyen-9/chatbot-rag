import boto3
from botocore.config import Config
from .config import AWS_REGION

def get_bedrock_client():
    config = Config(
        retries={
            "max_attempts": 10,
            "mode": "adaptive"
        }
    )
    return boto3.client(
        service_name="bedrock-runtime",
        region_name=AWS_REGION,
        config=config
    )
