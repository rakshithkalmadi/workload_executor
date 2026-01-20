# workload_executor

I need to build a AI Agent which is a workload executer which will run the workload and test if its capable of running. If its passes or fails you can send the result to the user.

This agent should be capable of going through the documentation of the workload and find out how to run it and what are all the options available for the workload and its feature and search and solve the issue if any error occurs while running the workload.

All those workloads run on a remove server or vm soo we need to connect to the server and run the workload via ssh. The configuration for the server is in the config folder.

I think we can use Langchain to build this agent.
