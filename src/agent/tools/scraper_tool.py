from langchain.tools import StructuredTool
from langchain.pydantic_v1 import BaseModel, Field
import requests
from bs4 import BeautifulSoup

class ScrapeWebPageInput(BaseModel):
    url: str = Field(description="The URL of the web page to scrape.")

def create_scraper_tool():
    
    def scrape_web_page(url: str) -> str:
        """Scrapes the text content from a web page."""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
                
            text = soup.get_text()
            
            # Break into lines and remove leading/trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # Drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text[:10000] # Limit output to avoid token limits
            
        except Exception as e:
            return f"Error scraping URL: {e}"

    return StructuredTool.from_function(
        func=scrape_web_page,
        name="scrape_web_page",
        description="Useful for reading content from a URL, such as a workload's documentation or installation instructions.",
        args_schema=ScrapeWebPageInput
    )
