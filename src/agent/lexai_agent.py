from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from loguru import logger
import os

from src.ssh.connection import SSHConnection
from src.utils.config import ConfigLoader

from src.agent.tools.ssh_tool import create_ssh_tool
from src.agent.tools.doc_tool import create_doc_tool
from src.agent.tools.scraper_tool import create_scraper_tool
from src.agent.llm_factory import LLMFactory

class LexAIAgent:
    def __init__(self, ssh_connection: SSHConnection, ai_provider: str = "openai", ai_model_name: str = None):
        self.ssh = ssh_connection
        self.ai_provider = ai_provider
        self.ai_model_name = ai_model_name
        
        self.llm = LLMFactory.create_llm(provider=self.ai_provider, model_name=self.ai_model_name)
        
        self.tools = [
            create_ssh_tool(self.ssh),
            create_doc_tool(),
            create_scraper_tool()
        ]
        self.agent_executor = self._create_agent()

    def _create_agent(self) -> AgentExecutor:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are LexAI, an expert DevOps AI agent capable of executing workloads on remote servers. "
                       "You have access to a remote server via SSH. "
                       "Your goal is to follow user instructions to deploy, run, and verify workloads. "
                       "If given a URL, you should SCRAPE the page to understand how to install and run the workload. "
                       "You must: \n"
                       "1. Identify installation steps (commands, dependencies).\n"
                       "2. Install them on the server.\n"
                       "3. Run the workload.\n"
                       "4. Verify the output to ensure it ran successfully.\n"
                       "Always verify the result of your commands."),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True) 

    def run(self, input_text: str):
        if not self.agent_executor:
            logger.warning("Agent executor not initialized yet.")
            return "Agent not ready."
        
        logger.info(f"Agent received input: {input_text}")
        return self.agent_executor.invoke({"input": input_text})
