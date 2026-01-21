from test import agent, Context, config, ResponseFormat
import json

response = agent.invoke(
    {"messages": [{"role": "user", "content": "How do I install this? https://github.com/tud-zih-energy/FIRESTARTER"}]},
    config=config,
    context=Context(user_id="1")
)

# Convert the Pydantic/dataclass object to dict/json for printing
result = response['structured_response']

# Pretty print the result
print(json.dumps(result.__dict__, indent=4))
