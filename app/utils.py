import PyPDF2
import time
import boto3
from .config import DYNAMODB_METRICS_TABLE

# Kết nối DynamoDB
dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-1")
metrics_table = dynamodb.Table(DYNAMODB_METRICS_TABLE)

def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return text

def count_tokens(text):
    return len(text.split())

def log_metrics(user_id, query, response, latency, token_count):
    try:
        metrics_table.put_item(
            Item={
                "user_id": user_id,
                "timestamp": str(time.time()),
                "query": query,
                "response": response,
                "latency": latency,
                "token_count": token_count
            }
        )
    except Exception as e:
        print(f"Failed to log metrics: {e}")
