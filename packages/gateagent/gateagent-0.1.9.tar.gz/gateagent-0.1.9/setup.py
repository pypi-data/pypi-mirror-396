from setuptools import setup, find_packages

setup(
    name="gateagent",
    version="0.1.0",
    description="Gateagent Python SDK for tracking agent-tool interactions",
    author="Gateagent",
    packages=find_packages(),
    install_requires=[
        "langchain-core", 
        "pydantic>=2.0.0",
        "requests",
    ],
    python_requires=">=3.9",
)
