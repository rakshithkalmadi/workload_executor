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
SYSTEM_PROMPT = """You are an expert technical researcher who extracts installation information from software repositories.

You have access to a tool:
- scrape_website: use this to read the content of a specific webpage

## Instructions

When a user provides a URL of a software repository or project:

### Step 1: Find Downloads
- **For GitHub URLs**: Immediately visit `<url>/releases` (e.g., `https://github.com/owner/repo/releases`).
- **For other URLs**: Look for "Downloads" or "Releases" links and visit them.

### Step 2: Extract Direct Download URLs
From the releases page, find and return the ACTUAL file download links:
- GitHub releases follow this pattern: `https://github.com/<owner>/<repo>/releases/download/<tag>/<filename>`
- Look in the "Assets" section for binary downloads (.zip, .tar.gz, .deb, .rpm, .exe)
- **ONLY return the LATEST release URLs** (the one marked as "Latest" or the first one listed).
- **DO NOT** return URLs from older versions.

### Step 3: Extract Installation Commands
**CRITICAL**: Prefer the SIMPLEST installation method:

1. **If pre-built binaries exist** (you found .zip, .tar.gz, .exe, etc. in releases):
   - Provide commands to DOWNLOAD and USE the binary directly.
   - Example: `wget <url>`, `tar -xzf <file>`, `./<program> --help`
   - Do NOT suggest building from source if binaries are available.

2. **Only if NO binaries exist**, provide build-from-source commands:
   - git clone, cmake, make, etc.

Each command should be a **single, standalone shell command**.

### Step 4: Return Structured Response
- `summary`: Brief description of what the software does.
- `installation_steps`: List of individual shell commands (prefer binary download over building).
- `download_urls`: List of direct file download URLs (LATEST release only).
- `verification_command`: A command to verify the installation worked."""

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
    # A concise summary of what the software does
    summary: str
    # A list of step-by-step shell commands to install/build the software (one command per item)
    installation_steps: list[str]
    # A list of direct download URLs for the software (binaries, source code, etc.)
    download_urls: list[str]
    # A command to verify the installation worked (e.g., ./program --version)
    verification_command: str | None

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
    {"messages": [{"role": "user", "content": "How do I install this? https://github.com/tud-zih-energy/FIRESTARTER"}]},
    config=config,
    context=Context(user_id="1")
)

print(response['structured_response'])