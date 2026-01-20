from langchain.tools import BaseTool, StructuredTool, tool
from langchain.pydantic_v1 import BaseModel, Field
from typing import Optional, Type

from src.ssh.connection import SSHConnection

class RunCommandInput(BaseModel):
    command: str = Field(description="The shell command to execute on the remote server.")

def create_ssh_tool(ssh_connection: SSHConnection):
    
    def run_remote_command(command: str) -> str:
        """Executes a command on the remote server and returns the output (stdout + stderr)."""
        stdout, stderr, exit_code = ssh_connection.execute_command(command)
        
        output = f"Exit Code: {exit_code}\n"
        if stdout:
            output += f"STDOUT:\n{stdout}\n"
        if stderr:
            output += f"STDERR:\n{stderr}\n"
            
        return output

    return StructuredTool.from_function(
        func=run_remote_command,
        name="run_remote_command",
        description="Useful for executing shell commands on the remote server. Use this to install software, run workloads, or check system status.",
        args_schema=RunCommandInput
    )
