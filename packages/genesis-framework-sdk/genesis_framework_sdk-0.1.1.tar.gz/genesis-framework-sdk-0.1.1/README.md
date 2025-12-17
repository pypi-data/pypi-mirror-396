# Genesis Framework

**The OS for Recursive Agentic Intelligence**

[![PyPI version](https://img.shields.io/pypi/v/genesis-framework-sdk.svg)](https://pypi.org/project/genesis-framework-sdk/)
[![Python versions](https://img.shields.io/pypi/pyversions/genesis-framework-sdk.svg)](https://pypi.org/project/genesis-framework-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📦 Installation

```bash
pip install genesis-framework-sdk
```

## 🚀 Quick Start

Get started with Genesis in seconds:

```python
from genesis import Genesis

# Initialize the Genesis client
client = Genesis(api_key="your-openai-api-key")

# Create your first swarm
result = client.create_swarm(
    goal="Analyze market trends for renewable energy sector",
    depth=3,
    name="Market_Analysis_Swarm"
)
```

## ✨ Features

- **Recursive Intelligence:** Agents can create sub-agents recursively to solve complex, multi-step problems in parallel
- **Swarm Architecture:** Self-organizing agent networks that collaborate to achieve objectives
- **Serverless Core:** Scalable infrastructure that handles orchestration automatically

## 🔑 API Keys

Genesis requires an OpenAI API key for operation. Simply pass your API key when initializing the client, and Genesis handles the rest securely.

## 📄 License

MIT License - See [LICENSE](LICENSE) for more details.