import time
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from langchain.chains import ConversationalRetrievalChain
from langchain_aws import ChatBedrock 

from .bedrock import get_bedrock_client
from .chat_memory import get_memory
from .vector_store import get_vector_store
from .utils import count_tokens, log_metrics
from .react_agent import create_agent_executor

def create_rag_chain(user_id, streaming=False):
    bedrock_client = boto3.client(
        "bedrock-runtime",
        region_name="ap-southeast-1",
        config=Config(retries={"max_attempts": 10, "mode": "adaptive"})
    )

    llm = ChatBedrock(
        client=bedrock_client,
        model_id="anthropic.claude-3-haiku-20240307-v1:0",
        model_kwargs={"max_tokens": 500},
        streaming=streaming
    )

    vector_store = get_vector_store()
    memory = get_memory(user_id)

    rag_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
        memory=memory,
        return_source_documents=True
    )

    return rag_chain

def query_rag_chain(rag_chain, user_id, user_query, streaming=False):
    start_time = time.time()

    if streaming:
        response = ""
        for chunk in rag_chain.stream({"question": user_query}):
            response += chunk.get("answer", "")
            yield chunk.get("answer", "")
        latency = time.time() - start_time
        token_count = count_tokens(response)
        log_metrics(user_id, user_query, response, latency, token_count)

    else:
        result = rag_chain.invoke({"question": user_query})  # Dùng invoke không gọi trực tiếp
        response = result["answer"]
        sources = result.get("source_documents", [])

        latency = time.time() - start_time
        token_count = count_tokens(response)
        log_metrics(user_id, user_query, response, latency, token_count)

        return response, sources

def query_with_agent(user_id, user_query, streaming=False):
    agent_executor = create_agent_executor(user_id)
    retries = 3
    backoff = 1

    for attempt in range(retries):
        try:
            if streaming:
                response = ""
                for chunk in agent_executor.stream({"input": user_query}):
                    response += chunk.get("output", "")
                    yield chunk.get("output", "")
                return
            else:
                result = agent_executor.invoke({"input": user_query})["output"]
                return result
        except ClientError as e:
            if e.response['Error']['Code'] == 'ThrottlingException' and attempt < retries - 1:
                print(f"ThrottlingException on attempt {attempt + 1}, waiting {backoff} seconds")
                time.sleep(backoff)
                backoff *= 2
                continue
            raise
