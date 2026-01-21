# https://docs.langchain.com/oss/python/langchain/quickstart
# Build using this

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from dotenv import load_dotenv
load_dotenv()
def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

agent = create_agent(
    model=init_chat_model("google_genai:gemini-2.5-flash-lite"),
    tools=[get_weather],
    system_prompt="You are a helpful assistant",
)

# Run the agent
r = agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather in sf"}]}
)
print("\n".join([m.get("content") for m in r.get("messages") if m.get("role") == "assistant"]))