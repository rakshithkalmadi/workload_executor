from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from loguru import logger
import os

from src.ssh.connection import SSHConnection
from src.utils.config import ConfigLoader

from src.agent.tools.ssh_tool import create_ssh_tool
from src.agent.tools.doc_tool import create_doc_tool

class LexAIAgent:
    def __init__(self, ssh_connection: SSHConnection):
        self.ssh = ssh_connection
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)
        self.tools = [
            create_ssh_tool(self.ssh),
            create_doc_tool()
        ]
        self.agent_executor = self._create_agent()

    def _create_agent(self) -> AgentExecutor:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are LexAI, an expert DevOps AI agent capable of executing workloads on remote servers. "
                       "You have access to a remote server via SSH. "
                       "Your goal is to follow user instructions to deploy, run, and verify workloads. "
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
