# Gateagent Python SDK

Track and analyze your AI agent's tool interactions with deep insights.

## Installation

```bash
pip install gateagent
```

### Example: Math Agent

Here is a complete example of how to use `gateagent` with a LangChain agent:

```python
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langsmith import traceable 
from gateagent import InteractionTracer

# 1. Initialize the Tracer
callbacks = [
    InteractionTracer(
        project_name="math-agent-playground",
        # tenant_id is derived from API Key on backend
        default_metadata={
            "agent": "math-agent-v1",
            "environment": "local",
        },
    )
]

# 2. Define Tools
@tool
def add_numbers(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

tools = [add_numbers]
tool_map = {t.name: t for t in tools}

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(tools)
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a math assistant."),
    ("human", "{input}"),
])
chain = prompt | llm

# 3. Use in execution (with @traceable or directly in config)
@traceable(run_type="chain", name="math-agent")
def run(input_text: str):
    response = chain.invoke(
        {"input": input_text},
        config={
            "callbacks": callbacks,
            "run_name": "math-agent-llm",
            "metadata": {"agent": "math-agent-v1"},
        },
    )
    
    if response.tool_calls:
        # Pass callbacks to tool execution logic
        tool_call = response.tool_calls[0]
        return tool_map[tool_call["name"]].invoke(
            tool_call["args"], 
            config={"callbacks": callbacks}
        )
    return response.content
```

## Configuration

Set your API key via environment variable:

```bash
export GATEAGENT_API_KEY="your-api-key"
```

Or pass it to the `Client` explicitly if needed (advanced usage).
