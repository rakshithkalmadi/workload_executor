from langchain.tools import StructuredTool
from langchain.pydantic_v1 import BaseModel, Field
import os

class ReadDocInput(BaseModel):
    file_path: str = Field(description="The path to the documentation file to read.")

def create_doc_tool():
    
    def read_documentation(file_path: str) -> str:
        """Reads the content of a documentation file."""
        if not os.path.exists(file_path):
            return f"Error: File not found at {file_path}"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            return f"Error reading file: {e}"

    return StructuredTool.from_function(
        func=read_documentation,
        name="read_documentation",
        description="Useful for reading workload documentation (README.md, etc.) to understand how to run a workload.",
        args_schema=ReadDocInput
    )
