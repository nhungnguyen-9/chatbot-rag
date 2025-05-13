import time
from langchain.chains import ConversationalRetrievalChain
from langchain_aws import BedrockLLM
from langchain.vectorstores import OpenSearchVectorSearch
from .bedrock import get_bedrock_client
from .chat_memory import get_memory
from .vector_store import get_vector_store
from .utils import count_tokens, log_metrics
from .react_agent import create_agent_executor

def create_rag_chain(user_id, streaming=False):
    bedrock_client = get_bedrock_client()
    llm = BedrockLLM(
        client=bedrock_client,
        model_id="anthropic.claude-v2",
        model_kwargs={"max_tokens_to_sample": 500},
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
    else:
        result = rag_chain({"question": user_query})
        response = result["answer"]
        sources = result["source_documents"]
        yield response, sources

    latency = time.time() - start_time
    token_count = count_tokens(response)
    log_metrics(user_id, user_query, response, latency, token_count)

def query_with_agent(user_id, user_query, streaming=False):
    agent_executor = create_agent_executor(user_id)
    if streaming:
        response = ""
        for chunk in agent_executor.stream({"input": user_query}):
            response += chunk.get("output", "")
            yield chunk.get("output", "")
    else:
        result = agent_executor.invoke({"input": user_query})
        yield result["output"]