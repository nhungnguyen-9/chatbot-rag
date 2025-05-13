# RAG Chatbot on AWS

## Overview
A Retrieval-Augmented Generation (RAG) chatbot built on AWS, supporting document-based Q&A, conversation history, user
authentication, response streaming, and dynamic actions (web search, weather API).

### Features
- **Level 100**: RAG chatbot with Bedrock, OpenSearch, DynamoDB, Cognito, and S3.
- **Level 200**: Response streaming, latency monitoring, and AWS CDK deployment.
- **Level 300**: React Agent with LangGraph, Tavily search, and weather API integration.

## Setup Instructions
1. **Install dependencies**:
```bash
make install
```

### Configure environment:
- Update .env with your AWS credentials and API keys.

### Run the app:
```bash
make run
```

### Run tests:
```bash
make test
```

### Deploy infrastructure:
```bash
make deploy
```

## Test Cases

- See tests/test_queries.py for query tests.

- See tests/test_latency.py for latency tests.