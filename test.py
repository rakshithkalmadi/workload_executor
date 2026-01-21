from dataclasses import dataclass
from dotenv import load_dotenv
load_dotenv()
from langchain_core.tools import Tool

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool, ToolRuntime
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.structured_output import ToolStrategy
from langchain_community.document_loaders import WebBaseLoader

@tool
def scrape_website(url: str) -> str:
    """Scrape the content of a website given its URL."""
    loader = WebBaseLoader(url)
    docs = loader.load()
    return "\n\n".join([d.page_content for d in docs])

# Define system prompt
SYSTEM_PROMPT = """You are an expert researcher and summarizer.

You have access to a tool:
- scrape_website: use this to read the content of a specific webpage

When a user provides a URL, use the scrape_website tool to read its content.
Then, provide a concise summary of the website's content in the 'summary' field of your response.
Do not make up information. Only summarize what is present in the website content."""

# Define context schema
@dataclass
class Context:
    """Custom runtime context schema."""
    user_id: str

# Configure model
model = init_chat_model(
    "google_genai:gemini-2.5-flash-lite",
    temperature=0
)

# Define response format
@dataclass
class ResponseFormat:
    """Response schema for the agent."""
    # A summary of the website content
    summary: str
    # Key topics or points found on the page
    key_points: list[str]

# Set up memory
checkpointer = InMemorySaver()

# Create agent
agent = create_agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[scrape_website],
    context_schema=Context,
    response_format=ToolStrategy(ResponseFormat),
    checkpointer=checkpointer
)

# Run agent
# `thread_id` is a unique identifier for a given conversation.
config = {"configurable": {"thread_id": "1"}}

# Example: Summarize a website
# Note: Ensure you have a valid URL. We will use a safe example.
response = agent.invoke(
    {"messages": [{"role": "user", "content": "Summarize this website: https://github.com/tud-zih-energy/FIRESTARTER"}]},
    config=config,
    context=Context(user_id="1")
)

print(response['structured_response'])