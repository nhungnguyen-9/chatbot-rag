from langchain_aws import BedrockLLM
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import create_react_agent
from .bedrock import get_bedrock_client
from .config import TAVILY_API_KEY, WEATHER_API_KEY
import requests

# Custom weather tool
def get_weather(city: str) -> str:
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}"
    response = requests.get(url)
    data = response.json()
    if "error" in data:
        return f"Could not get weather for {city}."
    return f"Current weather in {city}: {data['current']['condition']['text']}, {data['current']['temp_c']}°C"

def create_agent_executor(user_id):
    bedrock_client = get_bedrock_client()
    llm = BedrockLLM(
        client=bedrock_client,
        model_id="anthropic.claude-v2",
        model_kwargs={"max_tokens_to_sample": 500}
    )

    # Initialize tools
    tavily_tool = TavilySearchResults(api_key=TAVILY_API_KEY, max_results=3)
    weather_tool = get_weather

    # Create the agent with LangGraph
    agent_executor = create_react_agent(
        llm=llm,
        tools=[tavily_tool, weather_tool],
        memory=get_memory(user_id)
    )

    return agent_executor