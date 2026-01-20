import click
import os
from dotenv import load_dotenv
from loguru import logger

from src.utils.config import ConfigLoader
from src.ssh.connection import SSHConnection
from src.agent.lexai_agent import LexAIAgent

# Load env vars
load_dotenv()

@click.group()
def cli():
    """LexAI - AI Workload Executor"""
    pass

@cli.command()
@click.option('--workload', help='The workload command or description to run')
def agent(workload):
    """Start the AI Agent to run a workload."""
    logger.info("Starting LexAI Agent...")
    
    # 1. Load Config
    try:
        config_loader = ConfigLoader()
        config_loader.load_config()
    except Exception as e:
        logger.error(f"Config error: {e}")
        return

    # 2. Setup SSH
    ssh = SSHConnection(
        host=config_loader.remote_ip,
        username=config_loader.username,
        key_path=config_loader.key_file
    )

    # 3. Initialize Agent
    try:
        lex_agent = LexAIAgent(
            ssh_connection=ssh,
            ai_provider=config_loader.ai_provider,
            ai_model_name=config_loader.ai_model_name
        )
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        return

    # 4. Run Workload
    if not workload:
        workload = click.prompt("Please enter the workload description or command to run")
    
    logger.info(f"Task: {workload}")
    try:
        result = lex_agent.run(workload)
        logger.success(f"Agent Execution Result:\n{result}")
    except Exception as e:
        logger.error(f"Agent execution failed: {e}")

@cli.command()
def check_connection():
    """Verify SSH connection to the server."""
    logger.info("Checking SSH connection...")
    try:
        config_loader = ConfigLoader()
        config_loader.load_config()
        
        ssh = SSHConnection(
            host=config_loader.remote_ip,
            username=config_loader.username,
            key_path=config_loader.key_file
        )
        ssh.connect()
        stdout, stderr, code = ssh.execute_command("echo 'Connection Successful'")
        if code == 0:
            logger.success(f"Connection Verified! Server returned: {stdout}")
        else:
            logger.error(f"Connection failed executing command. Code: {code}, Error: {stderr}")
        ssh.disconnect()
    except Exception as e:
        logger.error(f"Connection check failed: {e}")

if __name__ == '__main__':
    cli()
