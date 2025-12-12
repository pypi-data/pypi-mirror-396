# Baicai Base: AI Agent Framework Foundation

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![LangGraph](https://img.shields.io/badge/Built%20with-LangGraph-green.svg)](https://github.com/langchain-ai/langgraph)

`Baicai Base` is the foundational framework for building intelligent AI agents for education using the LangGraph architecture. It provides a extensible foundation for creating multi-agent workflows that can collaborate, reason, and execute complex tasks.

## 🚀 Key Features

### 🤖 **Multi-Agent Architecture**
- **ReAct Pattern Implementation**: Built-in ReAct (Reasoning + Acting) agent framework
- **Modular Node System**: Extensible node-based architecture for custom agent behaviors
- **State Management**: Sophisticated state handling with memory persistence
- **Conditional Routing**: Intelligent routing logic with fail-fast and retry mechanisms

### 🔧 **Core Components**
- **Base Graph Framework**: Abstract base classes for building custom agent graphs
- **Code Execution Engine**: Safe code execution with debugging capabilities
- **LLM Integration**: Support for OpenAI-compatible APIs and Groq
- **Configuration Management**: Flexible configuration system with environment-based settings

### 🛠️ **Developer Tools**
- **Rich Logging**: Comprehensive logging with color-coded output
- **Graph Visualization**: Built-in Mermaid.js graph visualization
- **Code Interpreter**: Integrated code execution and debugging
- **Memory Management**: Persistent state and conversation memory

## 📋 Requirements

- **Python**: 3.10 or higher (tested up to 3.11)
- **Dependencies**: Managed via Poetry
- **LLM Access**: OpenAI API key or Groq API key

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/baicai.git
cd baicai/baicai_base
```

### 2. Install Poetry (if not already installed)

```bash
# macOS/Linux
curl -sSL https://install.python-poetry.org | python3 -

# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

### 3. Install Dependencies

```bash
poetry install
```

### 4. Set Up Environment

```bash
# Set up your API keys
export OPENAI_API_KEY="your-openai-api-key"
# or
export GROQ_API_KEY="your-groq-api-key"
```

## 🏗️ Architecture Overview

### Core Components

```
baicai_base/
├── agents/
│   ├── graphs/           # Graph implementations
│   │   ├── base_graph.py # Abstract base class
│   │   ├── react_coder_graph.py # ReAct pattern implementation
│   │   └── nodes/        # Node implementations
│   └── roles/            # Agent role definitions
├── configs/              # Configuration management
├── services/             # Core services (LLM, etc.)
└── utils/                # Utility functions and helpers
```


## 🚀 Quick Start

### Basic ReAct Agent Usage

```python
from baicai_base.agents.graphs import ReActCoder
from baicai_base.services import LLM

# Initialize LLM
llm_service = LLM()

# Create ReAct agent
agent = ReActCoder(
    graph_name="MyAgent",
    llm=llm_service.llm,
    need_helper=True
)

# Define a question for the AI model to predict
question = "code a simple function to calculate the sum of two numbers"

# Invoke the AI model with the question and get the results
results = agent.app.invoke({"messages": [("user", question)]}, agent.config)
```

See [react_coder_builder.ipynb](./docs/examples/react_coder_builder.ipynb) for more

## 📚 Documentation

### Core Concepts

- **[Agent Graphs](./docs/agent_graphs.md)**: Understanding the graph-based architecture
- **[Node System](./docs/nodes.md)**: Building custom nodes and behaviors
- **[State Management](./docs/state.md)**: Managing agent state and memory
- **[Configuration](./docs/configuration.md)**: Setting up and managing configurations

### API Reference

- **[BaseGraph](./docs/api/base_graph.md)**: Abstract base class for all agent graphs
- **[ReActCoder](./docs/api/react_coder.md)**: ReAct pattern implementation
- **[LLM Service](./docs/api/llm_service.md)**: Language model integration
- **[Node Classes](./docs/api/nodes.md)**: Available node types and interfaces


## 📄 License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT) - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Special thanks to:

- **[LangGraph Team](https://github.com/langchain-ai/langgraph)**: For the foundational graph framework
- **[LangChain Community](https://github.com/langchain-ai/langchain)**: For the excellent LLM integration tools
- **OpenAI & Groq**: For providing powerful language models
- **All Contributors**: For helping build and improve this framework

