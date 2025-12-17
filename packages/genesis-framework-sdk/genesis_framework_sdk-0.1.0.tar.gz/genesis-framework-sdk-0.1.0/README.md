# Genesis Framework

### The Operating System for Recursive Intelligence

Genesis is a dual-key AI framework that enables developers to build self-organizing agent swarms. Unlike traditional chatbots, Genesis agents can spawn child agents recursively to solve complex, multi-step problems in parallel.

## 🚀 Key Features

- **Infinite Recursion:** Agents can create sub-agents (Depth 1-10).
- **Live Observability:** Real-time graph visualization of agent hierarchy.
- **Dual-Key Security:** BYOK (Bring Your Own Key) for LLMs; Genesis handles orchestration.
- **Cost Control:** Granular token tracking per agent node.

## 🛠️ Quick Start

### 1. Installation
```bash
pip install genesis-framework
```

### 2. Run the Neural Core
```bash
# Start the Backend
uvicorn server.main:app --reload

# Start the Dashboard
cd docs && npm start
```

### 3. Initialize Swarm
```python
from genesis import GenesisClient

client = GenesisClient()
client.create_agent(name="Root_Node", objective="Analyze Market Trends")
```

## 📜 License

Proprietary Software. Copyright © 2025 Genesis Framework Inc.