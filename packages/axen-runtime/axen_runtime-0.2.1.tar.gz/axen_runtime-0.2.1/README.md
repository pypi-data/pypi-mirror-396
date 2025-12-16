# Agent Platform - Universal Runtime & Hosting for AI Agents

**Deploy and share your AI agents instantly.** Transform any Python AI agent (CrewAI, LangGraph, OpenAI) into a production-ready streaming API with just one line of code, then deploy and share with one command.

## Features

✨ **One-Line Integration**: Wrap any agent with `serve()`
🚀 **Instant Deployment**: Deploy with `agent deploy` (< 1 second)
🔗 **Auto-Generated URLs**: Get shareable links instantly
💬 **Chat UI Included**: Beautiful Next.js frontend with expert review panel
🔄 **Real-time Streaming**: SSE-based token streaming
🎯 **Multi-Tenant**: Host unlimited agents on one server
🛡️ **Secure**: UUID-based isolation, timeout enforcement
🔌 **Framework Agnostic**: OpenAI, CrewAI, LangGraph, or plain Python

## Quick Start

### Option A: Deploy & Share (Recommended)

**1. Install CLI**

```bash
cd /Users/kazuma/Desktop/AXEN\ INC./dev/runtime-app
pip install -e ".[cli]"
```

**2. Initialize Your Agent**

```bash
mkdir my-agent
cd my-agent
python -m cli init --name my-agent
```

This creates:
- `agent.yaml` - Configuration file
- `main.py` - Sample agent code

**3. Implement Your Agent**

Edit `main.py`:

```python
from agent_runner import serve
from typing import List
from agent_runner.types import Message

def my_agent(messages: List[Message]):
    """Your agent logic here."""
    latest_message = messages[-1]["content"]

    # Your AI logic...
    response = f"Response to: {latest_message}"

    # Yield tokens for streaming
    for word in response.split():
        yield word + " "

# Register the agent
serve(my_agent)
```

**4. Deploy**

```bash
# Start the platform (first time only)
cd /Users/kazuma/Desktop/AXEN\ INC./dev/runtime-app
docker-compose up -d

# Deploy your agent
cd my-agent
python -m cli deploy
```

**Output:**
```
✅ Deployment successful!
📋 Deployment ID: 550e8400-e29b-41d4-a716-446655440000
🔗 Access your agent here:
   http://localhost:3000/chat/550e8400-e29b-41d4-a716-446655440000
```

**5. Share & Use**

Share the URL with anyone. They can:
- Chat with your agent via the web UI
- Integrate via API using the deployment_id

### Option B: Local Development (Docker)

For developing agents locally before deployment:

**1. Install SDK**

```bash
pip install -e .
```

**2. Write Your Agent**

```python
# main.py
from agent_runner import serve
from typing import List
from agent_runner.types import Message

def my_agent(messages: List[Message]):
    latest_message = messages[-1]["content"]
    yield f"Echo: {latest_message}"

serve(my_agent)
```

**3. Build & Run**

```bash
# Make build script executable
chmod +x sandbox/build.sh

# Build Docker images
./sandbox/build.sh

# Run the agent
docker run -p 8000:8000 agent-runtime:latest
```

**4. Test It**

```bash
curl -X POST http://localhost:8000/api/chat \
     -H "Content-Type: application/json" \
     -d '{"messages": [{"role": "user", "content": "Hello!"}]}'
```

## Deploy & Share

### CLI Commands

#### `agent init`

Initialize a new agent project:

```bash
python -m cli init [OPTIONS]
```

**Options:**
- `--name, -n TEXT`: Agent name (default: "my-agent")
- `--force, -f`: Overwrite existing files

**Example:**
```bash
python -m cli init --name awesome-chatbot
```

#### `agent deploy`

Deploy your agent to the platform:

```bash
python -m cli deploy [OPTIONS]
```

**Options:**
- `--api-url TEXT`: API server URL (default: http://localhost:8000)

**Example:**
```bash
python -m cli deploy --api-url https://api.axen.dev
```

### agent.yaml Configuration

The `agent.yaml` file configures your agent:

```yaml
# Basic Information
name: my-agent
description: A simple AI agent
version: 1.0.0

# Runtime Configuration
runtime:
  python_version: "3.11"
  entrypoint: main.py
  framework: auto  # auto, openai, crewai, langgraph, generic
  timeout: 300     # seconds

# Dependencies (optional)
dependencies:
  - openai==1.6.0
  - langchain==0.1.0

# Environment Variables (optional)
env:
  MODEL_NAME: gpt-4
```

### Deployment Process

When you run `agent deploy`:

1. ✅ **Validates** `agent.yaml` and `main.py`
2. 📦 **Packages** code into `project.zip` (excludes venv, .git, etc.)
3. 🚀 **Uploads** to server at `/api/deploy`
4. 🔑 **Generates** unique deployment_id (UUID)
5. 📁 **Extracts** to `uploads/{deployment_id}/`
6. 🔗 **Returns** shareable URL

**No Docker build = Instant deployment (< 1 second)**

### Accessing Deployed Agents

**Via Web UI:**
```
http://localhost:3000/chat/{deployment_id}
```

**Via API:**
```bash
curl -X POST http://localhost:8000/api/chat/{deployment_id} \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello"}]}'
```

## Examples

### Plain Python Generator

```python
from agent_runner import serve
from typing import List
from agent_runner.types import Message
import time

def my_simple_agent(messages: List[Message]):
    latest_message = messages[-1]["content"]
    for word in latest_message.split():
        yield word + " "
        time.sleep(0.1)

serve(my_simple_agent)
```

### OpenAI Streaming (with Full Conversation History)

```python
from agent_runner import serve
from agent_runner.types import Message
from openai import OpenAI
from typing import List
import os

def my_openai_agent(messages: List[Message]):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    # Pass full conversation history directly to OpenAI
    stream = client.chat.completions.create(
        model="gpt-4",
        messages=messages,  # Full history!
        stream=True
    )
    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

serve(my_openai_agent, framework="openai")
```

### CrewAI Multi-Agent

```python
from agent_runner import serve
from crewai import Agent, Task, Crew

def my_crew_agent(input_text: str):
    # Define agents
    researcher = Agent(role='Researcher', goal='Research topic')
    writer = Agent(role='Writer', goal='Write summary')

    # Create crew
    crew = Crew(agents=[researcher, writer], tasks=[...])
    result = crew.kickoff()

    for word in str(result).split():
        yield word + " "

serve(my_crew_agent, framework="crewai")
```

### LangGraph Workflow

```python
from agent_runner import serve
from langgraph.graph import StateGraph, END

def my_graph_agent(input_text: str):
    workflow = StateGraph(...)
    # Build graph...
    app = workflow.compile()

    for state in app.stream({"input": input_text}):
        yield state.get("output", "")

serve(my_graph_agent, framework="langgraph")
```

## Project Structure

```
runtime-app/
├── cli.py                       # Deployment CLI
├── templates/                   # CLI templates
│   ├── agent.yaml               # Agent config template
│   └── main.py                  # Sample agent code
├── uploads/                     # Deployed agents
│   └── {deployment_id}/         # One directory per deployment
│
├── agent_runner/                # Universal SDK
│   ├── __init__.py              # Public API
│   ├── sdk.py                   # Core serve() function
│   ├── types.py                 # Type definitions
│   ├── logger.py                # Logging
│   ├── exceptions.py            # Custom exceptions
│   ├── adapters/                # Framework adapters
│   │   ├── base.py
│   │   ├── generic_adapter.py
│   │   ├── openai_adapter.py
│   │   ├── crewai_adapter.py
│   │   └── langgraph_adapter.py
│   └── streaming/               # Async/sync bridge
│       └── normalizer.py
│
├── runtime/                     # FastAPI server
│   ├── server.py                # HTTP endpoints
│   ├── loader.py                # Dynamic agent loader
│   ├── config.py                # Configuration
│   ├── middleware.py            # Timeout, rate limiting
│   └── routers/
│       └── deploy.py            # Deployment API
│
├── frontend/                    # Next.js Chat UI
│   ├── app/
│   │   ├── page.tsx             # Main chat page
│   │   └── layout.tsx           # Root layout
│   ├── components/
│   │   ├── chat.tsx             # Chat interface (useChat)
│   │   ├── message.tsx          # Message bubbles
│   │   ├── review-panel.tsx     # Expert review panel
│   │   └── review-form.tsx      # Review form
│   └── lib/
│       ├── types.ts             # TypeScript types
│       └── utils.ts             # Utilities
│
├── sandbox/                     # Docker environment (legacy)
│   ├── Dockerfile.base          # Base image
│   ├── Dockerfile.runtime       # Runtime image
│   └── build.sh                 # Build script
│
├── examples/                    # Example implementations
│   ├── plain_generator_example/
│   ├── openai_example/
│   ├── crewai_example/
│   └── langgraph_example/
│
├── docker-compose.yml           # Local development
├── pyproject.toml               # SDK package definition
├── README.md                    # This file
└── DEPLOY.md                    # Detailed deployment guide
```

## API Endpoints

### POST /api/deploy

Deploy a new agent.

**Request:**
- `file`: Zip file containing agent code (multipart/form-data)
- `name`: Agent name (optional)

**Response:**
```json
{
  "deployment_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "my-agent",
  "status": "success",
  "message": "Agent 'my-agent' deployed successfully"
}
```

### POST /api/chat/{deployment_id}

Chat with a deployed agent (multi-tenant endpoint).

**Request:**
```json
{
  "messages": [
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi there!"},
    {"role": "user", "content": "How are you?"}
  ]
}
```

**Response (Server-Sent Events):**
```
data: Hello
data: there
data: !
data: [DONE]
```

### POST /api/chat

Chat with the default agent (single-tenant endpoint).

Same format as above, but uses the agent loaded at startup.

**Frontend Integration (Vercel AI SDK):**
```typescript
// app/page.tsx
import { useChat } from 'ai/react';

export default function Chat() {
  const { messages, input, handleInputChange, handleSubmit } = useChat({
    api: 'http://localhost:8000/api/chat/YOUR_DEPLOYMENT_ID',
  });

  return (
    <div>
      {messages.map(m => (
        <div key={m.id}>{m.role}: {m.content}</div>
      ))}
      <form onSubmit={handleSubmit}>
        <input value={input} onChange={handleInputChange} />
      </form>
    </div>
  );
}
```

### GET /api/deployments/{deployment_id}

Get information about a deployment.

**Response:**
```json
{
  "deployment_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "my-agent",
  "version": "1.0.0",
  "description": "A simple AI agent",
  "framework": "auto",
  "created_at": "1234567890.123"
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "agent_loaded": true,
  "uptime_seconds": 123.45
}
```

### GET /docs

Interactive API documentation (Swagger UI).

Visit `http://localhost:8000/docs` for the full API reference.

## Frontend Chat UI

The platform includes a modern Next.js chat interface with expert review capabilities.

### Running the Frontend

```bash
# Start backend first
docker-compose up -d

# Start frontend
cd frontend
npm install
npm run dev
```

Visit: `http://localhost:3000`

### Features

- **Real-time Streaming**: See agent responses token-by-token
- **Expert Review Panel**: Annotate and review agent responses
  - Star rating (1-5)
  - Correction input
  - Comment textarea
- **Responsive Design**: Works on desktop and mobile
- **Vercel AI SDK Integration**: Uses `useChat` hook

For detailed frontend documentation, see `frontend/README.md`.

## Configuration

### Environment Variables

```bash
# API Keys
export OPENAI_API_KEY="your-key-here"

# Server Configuration
export HOST="0.0.0.0"
export PORT="8000"
export LOG_LEVEL="INFO"

# Resource Limits
export MAX_EXECUTION_TIME="300"    # 5 minutes
export MAX_MEMORY="512m"
export MAX_CPU="1.0"

# Rate Limiting
export RATE_LIMIT_ENABLED="true"
export RATE_LIMIT_MAX_REQUESTS="100"
export RATE_LIMIT_WINDOW="60"      # seconds

# CLI Configuration
export AGENT_PLATFORM_URL="http://localhost:8000"
```

### Docker Compose

For local development:

```bash
# Create .env file
echo "OPENAI_API_KEY=your-key" > .env

# Run with docker-compose
docker-compose up
```

## SDK API Reference

### serve(handler, *, framework=None, config=None, timeout=300, chunk_size=1, debug=False)

Register an agent handler for serving.

**Parameters:**
- `handler` (Callable): Your agent function (sync/async generator)
- `framework` (str, optional): Framework hint ("auto", "crewai", "langgraph", "openai")
- `config` (dict, optional): Additional configuration
- `timeout` (int): Maximum execution time in seconds (default: 300)
- `chunk_size` (int): Tokens per chunk for batching (default: 1)
- `debug` (bool): Enable debug logging (default: False)

**Example:**
```python
serve(my_agent, framework="openai", timeout=600, debug=True)
```

### test_agent(messages, handler=None)

Test an agent locally without running the server.

**Parameters:**
- `messages` (List[Message]): Messages to test with
- `handler` (Callable, optional): Handler to test (uses registered if not provided)

**Returns:**
- Generator yielding tokens

**Example:**
```python
messages = [{"role": "user", "content": "Hello"}]
for token in test_agent(messages):
    print(token, end="")
```

## Architecture

### Hot-Loading System

The platform uses **hot-loading** for instant deployment:

1. Agent code uploaded as zip file
2. Extracted to `uploads/{deployment_id}/`
3. On first request, Python dynamically imports the agent
4. AgentRuntime instance cached for subsequent requests
5. **No Docker build** = deployment in < 1 second

### Multi-Tenant Design

- Single server handles unlimited agents
- Each agent gets unique UUID deployment_id
- Agents run in isolated namespaces
- Shared infrastructure (FastAPI, middleware, adapters)
- Independent execution contexts per request

### Security

- **UUID Validation**: Prevents directory traversal attacks
- **Path Resolution**: Ensures files stay within uploads directory
- **Timeout Enforcement**: Maximum 300s per request
- **Rate Limiting**: 100 requests/minute per IP
- **File Exclusions**: Auto-excludes .env, credentials from deployments

## Performance

### Deployment Speed
- **Hot-loading**: < 1 second (instant)
- **Docker build** (legacy): 15-30 seconds
- **Base image build** (one-time): 2-3 minutes

### Resource Limits
- **CPU**: 1 core per agent
- **Memory**: 512MB per agent
- **Execution timeout**: 5 minutes (configurable)
- **Rate limit**: 100 requests/minute (configurable)

### Streaming Latency
- **API latency**: p95 < 200ms
- **Token streaming**: p95 < 100ms
- **Agent caching**: First load ~100ms, cached < 10ms

## Troubleshooting

### CLI Issues

**"agent.yaml not found"**
```bash
# Run init first
python -m cli init --name my-agent
```

**"Cannot connect to API server"**
```bash
# Make sure backend is running
docker-compose up -d

# Check server status
curl http://localhost:8000/health
```

**"Invalid zip file"**
```bash
# Check for syntax errors
python -m py_compile main.py

# Try re-deploying
python -m cli deploy
```

### Runtime Issues

**"Agent handler not registered"**

Solution: Make sure `main.py` calls `serve(your_handler)`:
```python
serve(my_agent)  # Don't forget this!
```

**"Agent not found or failed to load"**

Check deployment exists:
```bash
ls -la uploads/{deployment_id}/
# Should show: agent.yaml, main.py
```

**Import errors**
```
ModuleNotFoundError: No module named 'crewai'
```

Solution: Add the module to `agent.yaml`:
```yaml
dependencies:
  - crewai>=0.1.0
```

**Timeout errors**
```
Agent execution timeout after 300s
```

Solution: Increase timeout in `agent.yaml`:
```yaml
runtime:
  timeout: 600
```

**Rate limit exceeded**
```
Rate limit exceeded: 100 requests per 60s
```

Solution: Adjust `RATE_LIMIT_MAX_REQUESTS` environment variable.

## Development

### Local Testing (Without Docker)

```python
# test_local.py
from agent_runner import serve, test_agent
from agent_runner.types import Message
from typing import List

def my_agent(messages: List[Message]):
    yield f"Echo: {messages[-1]['content']}"

serve(my_agent)

# Test it
messages = [{"role": "user", "content": "Hello World"}]
for token in test_agent(messages):
    print(token, end="", flush=True)
```

Run:
```bash
python test_local.py
```

### Running Full Stack Locally

```bash
# Terminal 1: Start backend
docker-compose up

# Terminal 2: Start frontend
cd frontend
npm run dev

# Terminal 3: Deploy an agent
cd examples/openai_example
python -m cli deploy
```

Visit:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- Docs: `http://localhost:8000/docs`

## Documentation

- **DEPLOY.md**: Detailed deployment guide
- **frontend/README.md**: Frontend documentation
- **CLAUDE.md**: Architecture and development guidelines
- **examples/**: Working examples for each framework

## Contributing

We welcome contributions! See `CLAUDE.md` for development guidelines.

## License

MIT License - See LICENSE file

## Support

- **Issues**: [GitHub Issues](https://github.com/axen/runtime-app/issues)
- **Documentation**: See `DEPLOY.md` and `examples/`
- **Architecture**: See `CLAUDE.md`

---

**Built with the Agent Platform SDK** - Deploy and share AI agents in one command.
