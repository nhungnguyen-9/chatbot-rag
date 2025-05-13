from aws_cdk import Stack
from aws_cdk import aws_s3 as s3
from constructs import Construct

class S3Stack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.bucket = s3.Bucket(
            self, "RagChatbotBucket",
            bucket_name="rag-chatbot-documents",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED
        )