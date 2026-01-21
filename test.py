from dataclasses import dataclass
from dotenv import load_dotenv
load_dotenv()
from langchain_core.tools import Tool
import requests
import re

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

@tool
def get_github_releases(repo_url: str) -> str:
    """
    Get release information from a GitHub repository including exact download URLs.
    Use this for GitHub repos to get accurate asset download links.
    
    Args:
        repo_url: GitHub repository URL (e.g., https://github.com/owner/repo)
    
    Returns:
        JSON-like string with latest release info including asset download URLs.
    """
    # Extract owner/repo from URL
    match = re.search(r'github\.com/([^/]+)/([^/]+)', repo_url)
    if not match:
        return "Error: Invalid GitHub URL"
    
    owner, repo = match.groups()
    repo = repo.rstrip('.git')
    
    # Fetch latest release from GitHub API
    api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    try:
        response = requests.get(api_url, timeout=10)
        if response.status_code == 404:
            return f"No releases found for {owner}/{repo}"
        response.raise_for_status()
        data = response.json()
        
        # Extract relevant info
        result = {
            "tag": data.get("tag_name", ""),
            "name": data.get("name", ""),
            "assets": []
        }
        
        for asset in data.get("assets", []):
            result["assets"].append({
                "name": asset["name"],
                "download_url": asset["browser_download_url"],
                "size_mb": round(asset["size"] / 1024 / 1024, 2)
            })
        
        # Also include source archives
        result["source_tarball"] = data.get("tarball_url", "")
        result["source_zipball"] = data.get("zipball_url", "")
        
        return str(result)
    except Exception as e:
        return f"Error fetching releases: {e}"

# Define system prompt
SYSTEM_PROMPT = """You are an expert technical researcher who extracts installation information from software repositories.

You have access to tools:
- get_github_releases: Use this for GitHub repos to get ACCURATE download URLs from the latest release
- scrape_website: Use this to read README or other documentation pages

## Instructions

When a user provides a URL of a software repository or project:

### Step 1: Get Release Information
- **For GitHub URLs**: Use `get_github_releases` tool FIRST. This gives you exact download URLs.
- **For other URLs**: Use `scrape_website` to find release/download information.

### Step 2: Extract Download URLs
From the `get_github_releases` output:
- Look at the "assets" list for pre-built binaries
- Use the "download_url" field EXACTLY as returned - do not modify it
- **Prefer Linux binaries**: files with "Linux", "linux", ".tar.gz" (not Windows .exe or macOS .dmg)
- If no assets exist, the source_tarball URL can be used for building from source

### Step 3: Extract Installation Commands
**CRITICAL**: Prefer the SIMPLEST installation method:

1. **If Linux pre-built binaries exist** (from assets):
   - `wget <exact_download_url_from_assets>`
   - `tar -xzf <exact_filename>` (extracts to current directory)
   - `ls` to see what was extracted
   - Run the binary directly: `./FIRESTARTER --help` or similar
   - NOTE: Do NOT assume a subdirectory is created - many tars extract files directly

2. **If NO Linux binaries exist**, provide build-from-source commands.

### Step 4: Return Structured Response
- `summary`: Brief description of what the software does.
- `installation_steps`: List of individual shell commands.
- `download_urls`: EXACT URLs from the get_github_releases output.
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
    tools=[get_github_releases, scrape_website],
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

result = response['structured_response']
print(result)

# Execute on remote VM (uncomment to run)
from ssh_executor import execute_response
success = execute_response(result)
print(f"\nRemote execution {'succeeded' if success else 'failed'}")