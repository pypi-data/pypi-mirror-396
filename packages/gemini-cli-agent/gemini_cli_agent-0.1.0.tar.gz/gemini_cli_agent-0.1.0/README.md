# Gemini Agent

Python wrapper for [Google's Gemini CLI](https://github.com/google-gemini/gemini-cli) agentic capabilities.

## Installation

```bash
pip install gemini-agent            # client only
pip install gemini-agent[core]      # + direct CLI usage
pip install gemini-agent[server]    # + REST API service
```

**Requirements:** Node.js 18+ and `npm install -g @google/gemini-cli`

## Quick Start

```bash
export GEMINI_API_KEY=your_key
```

```python
from gemini_agent.core import GeminiAgent

agent = GeminiAgent()
result = agent.run("Create a Python CLI that lists files")

print(result.response)        # Gemini's response
print(result.modified_files)  # {"cli.py": "import os..."}
```

## Usage

### Direct CLI Wrapper

```python
from gemini_agent.core import GeminiAgent

agent = GeminiAgent(
    model="gemini-2.5-flash",  # optional
    sandbox=True,              # isolated execution
)

result = agent.run(
    "Build a REST API with FastAPI",
    mcp_servers=["filesystem"],
    files={"spec.txt": "..."},
)

# result.success, result.response, result.modified_files
```

### Python Client (Remote)

```python
from gemini_agent.client import GeminiAgentClient

async with GeminiAgentClient("http://localhost:8000") as client:
    result = await client.run("Create a hello world script")
    print(result.modified_files)
```

### REST API

```bash
podman-compose up -d --build

# Submit task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a fibonacci function"}'

# Get result
curl http://localhost:8000/tasks/{task_id}
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/tasks` | Submit task |
| `GET` | `/tasks/{id}` | Get result |
| `DELETE` | `/tasks/{id}` | Cancel task |
| `GET` | `/health` | Health check |
| `GET` | `/mcp/servers` | List MCP servers |
| `POST` | `/mcp/servers` | Add MCP server |

## Configuration

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | API key (required) |
| `GEMINI_MODEL` | Model override |
| `GEMINI_TIMEOUT` | Timeout in seconds (default: 300) |
| `REDIS_URL` | Redis URL for server mode |

## License

MIT
