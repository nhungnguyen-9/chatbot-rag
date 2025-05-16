import re
from langchain_aws import BedrockLLM
from langchain.agents import initialize_agent
from langchain.agents.agent_types import AgentType
from langchain_community.tools.tavily_search import TavilySearchResults
from .bedrock import get_bedrock_client
from .config import TAVILY_API_KEY, WEATHER_API_KEY
from .chat_memory import get_memory
from langchain.tools import Tool
import requests

def get_weather(city: str) -> str:
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}"
    response = requests.get(url)
    data = response.json()
    if "error" in data:
        return f"Could not get weather for {city}."
    return f"Current weather in {city}: {data['current']['condition']['text']}, {data['current']['temp_c']}°C"

def create_agent_executor(user_id: str):
    bedrock_client = get_bedrock_client()
    llm = BedrockLLM(
        client=bedrock_client,
        model_id="anthropic.claude-v2",
        model_kwargs={"max_tokens_to_sample": 500}
    )

    tavily_tool = TavilySearchResults(api_key=TAVILY_API_KEY, max_results=3)

    weather_tool = Tool(
        name="GetCurrentWeather",
        func=get_weather,
        description="Trả về thời tiết hiện tại theo tên thành phố. Ví dụ: 'Hanoi', 'New York'."
    )

    tools = [tavily_tool, weather_tool]

    agent_executor = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        memory=get_memory(user_id),
        verbose=True
    )

    return agent_executor

# Query with agent or direct weather call
def query_with_agent(user_id: str, query: str, streaming: bool = False):
    """
    Trả về kết quả chuỗi. Nếu là câu hỏi thời tiết thì gọi trực tiếp get_weather(city).
    Ngược lại gọi qua React Agent.
    """
    query_lower = query.lower()

    # Detect if it's a weather question like "what's the weather in Hanoi"
    match = re.search(r"(?:weather\s+(?:in|at)?\s*)([a-zA-Z\s]+)", query_lower)
    if match:
        city = match.group(1).strip().title()
        result = get_weather(city)
        yield result
    else:
        # Otherwise, use the agent
        agent = create_agent_executor(user_id)
        response = agent.run(query)
        yield response
