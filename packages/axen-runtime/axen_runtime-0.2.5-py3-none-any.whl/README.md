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

> 💡 **既存のAIエージェントプロジェクトをお持ちですか？**
>
> ⚠️ **重要**: 既に`main.py`などのコードがあるプロジェクトでは、`agent init`を使用すると**ファイルが上書きされます**。
>
> 既存プロジェクトの場合は、[移行ガイド (MIGRATION_GUIDE.md)](./MIGRATION_GUIDE.md) を参照してください。
> CrewAI、LangGraph、OpenAIなどの既存プロジェクトを5分でデプロイできます。

### Option A: 新規プロジェクトを作成してデプロイ

**新しくAIエージェントを作る場合はこちら**

**1. Install from PyPI**

```bash
pip install axen-runtime
```

**2. Initialize Your Agent**

```bash
# 新しいディレクトリを作成
mkdir my-agent
cd my-agent

# テンプレートを生成
agent init --name my-agent
```

This creates:
- `agent.yaml` - Configuration file
- `main.py` - Sample agent code (テンプレート)
- `.env.template` - Environment variables template

⚠️ **注意**: `agent init`は新しい`main.py`を作成します。既存のコードがある場合は実行しないでください。

**3. Add Your API Keys**

```bash
cp .env.template .env
# Edit .env and add your API keys
echo "OPENAI_API_KEY=sk-proj-your-key-here" >> .env

# Important: Add .env to .gitignore
echo ".env" >> .gitignore
```

**4. Implement Your Agent**

Edit `main.py`:

```python
from dotenv import load_dotenv
import os
load_dotenv()

from agent_runner import serve
from openai import OpenAI
from typing import List
from agent_runner.types import Message

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def my_agent(messages: List[Message]):
    """Your AI agent logic."""
    stream = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        stream=True
    )
    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

# Register the agent
serve(my_agent, framework="openai")
```

**5. Deploy to Production**

```bash
agent deploy
```

**Output:**
```
✅ Deployment successful!
📋 Deployment ID: 550e8400-e29b-41d4-a716-446655440000
🔗 Access your agent here:
   https://axen-runner.vercel.app/chat/550e8400-e29b-41d4-a716-446655440000
```

Your agent is now running on our production infrastructure at:
- **API**: `https://agent-runner-production-f78a.up.railway.app`
- **Frontend**: `https://axen-runner.vercel.app`

**6. Share & Use**

Share the URL with anyone. They can:
- **Chat via Web UI**: `https://axen-runner.vercel.app/chat/YOUR_DEPLOYMENT_ID`
- **Integrate via API**:

```bash
curl -X POST https://agent-runner-production-f78a.up.railway.app/api/chat/YOUR_DEPLOYMENT_ID \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello"}]}'
```

### Option B: 既存プロジェクトをデプロイ

**既にCrewAI、LangGraph、OpenAIなどのコードがある場合はこちら**

⚠️ **重要**: 既存プロジェクトでは`agent init`を使わないでください（ファイルが上書きされます）

**詳細な手順**: [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md)

**クイックガイド:**

```bash
# 1. 既存プロジェクトに移動
cd ~/my-existing-project

# 2. agent.yaml を手動作成（agent init は使わない！）
cat > agent.yaml << 'EOF'
name: my-agent
description: My existing AI agent
version: 1.0.0
runtime:
  entrypoint: main.py
  framework: langgraph  # または crewai, openai, generic
EOF

# 3. 既存の main.py に serve() を追加（3-5行）
# from agent_runner import serve
# def my_agent(messages):
#     # 既存のコードを呼び出す
#     result = your_existing_function(messages)
#     for word in str(result).split():
#         yield word + " "
# serve(my_agent, framework="langgraph")

# 4. .env を確認
echo "OPENAI_API_KEY=sk-proj-xxx" > .env
echo ".env" >> .gitignore

# 5. デプロイ
agent deploy
```

### Option C: Local Development

For developing agents locally before deploying to production:

**1. Clone & Install**

```bash
git clone https://github.com/AXEN-INC/Agent-Runner
cd runtime-app
pip install axen-runtime
```

**2. Start Local Server**

```bash
# Start backend with Docker
docker-compose up -d

# Check server is running
curl http://localhost:8000/health
```

**3. Initialize Your Agent**

```bash
mkdir my-agent
cd my-agent
agent init --name my-agent
```

**4. Deploy to Local Server**

```bash
agent deploy --api-url http://localhost:8000
```

**Output:**
```
✅ Deployment successful!
📋 Deployment ID: 550e8400-e29b-41d4-a716-446655440000
🔗 Access your agent here:
   http://localhost:3000/chat/550e8400-e29b-41d4-a716-446655440000
```

**5. Test Locally**

```bash
# Via API
curl -X POST http://localhost:8000/api/chat/YOUR_DEPLOYMENT_ID \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello"}]}'

# Via Frontend (if running)
cd frontend
npm install && npm run dev
# Visit http://localhost:3000
```

**When you're ready, deploy to production:**

```bash
# Deploy to production (omit --api-url)
agent deploy
```

## Deploy & Share

### CLI Commands

#### `agent init`

Initialize a new agent project:

```bash
agent init [OPTIONS]
```

**Options:**
- `--name, -n TEXT`: Agent name (default: "my-agent")
- `--force, -f`: Overwrite existing files

**Example:**
```bash
agent init --name awesome-chatbot
```

#### `agent deploy`

Deploy your agent to the platform:

```bash
agent deploy [OPTIONS]
```

**Options:**
- `--api-url TEXT`: API server URL (default: production Railway server)

**Examples:**
```bash
# Deploy to production (default)
agent deploy

# Deploy to local development server
agent deploy --api-url http://localhost:8000

# Deploy to custom server
agent deploy --api-url https://your-custom-server.com
```

**Environment Variables:**
- `AGENT_PLATFORM_URL`: Override default API URL
- `AGENT_PLATFORM_FRONTEND_URL`: Override default frontend URL

```bash
# Configure custom URLs
export AGENT_PLATFORM_URL="https://your-api.com"
export AGENT_PLATFORM_FRONTEND_URL="https://your-frontend.com"
agent deploy
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

## Environment Variables

Your agent can use environment variables for API keys and configuration. The platform automatically loads `.env` files from your agent directory.

### Using `.env` Files

1. **Create a `.env` file** in your agent directory:

```bash
# .env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
MODEL_NAME=gpt-4
TEMPERATURE=0.7
```

2. **Use `python-dotenv` in your agent code**:

```python
# main.py
from dotenv import load_dotenv
import os

# Load environment variables (works both locally and on server)
load_dotenv()

from openai import OpenAI
from agent_runner import serve

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def my_agent(messages):
    # Your agent logic using the API key
    response = client.chat.completions.create(
        model=os.getenv("MODEL_NAME", "gpt-4"),
        messages=messages
    )
    yield response.choices[0].message.content

serve(my_agent)
```

3. **Add `.env` to your `.gitignore`**:

```bash
echo ".env" >> .gitignore
```

4. **Deploy your agent**:

```bash
agent deploy
```

Your `.env` file will be included in the deployment and loaded automatically on the server.

### Security Best Practices

⚠️ **Important:**
- **Always add `.env` to `.gitignore`** to prevent committing secrets to Git
- Use different API keys for development vs. production
- Rotate API keys regularly
- Never hardcode API keys in your code

### Supported Environment Variables

The platform loads `.env` files automatically, so you can use any environment variable:

- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic Claude API key
- `GOOGLE_API_KEY` - Google Gemini API key
- Custom variables - Any variable you define

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

#### User Agent Configuration (.env file)

These are included in your agent deployment:

```bash
# .env (in your agent directory)
OPENAI_API_KEY=sk-proj-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
MODEL_NAME=gpt-4
TEMPERATURE=0.7
```

#### CLI Configuration

```bash
# Override deployment targets
export AGENT_PLATFORM_URL="https://agent-runner-production-f78a.up.railway.app"  # Default
export AGENT_PLATFORM_FRONTEND_URL="https://axen-runner.vercel.app"  # Default

# For local development
export AGENT_PLATFORM_URL="http://localhost:8000"
```

#### Server Configuration (for self-hosting)

```bash
# Server Configuration
export HOST="0.0.0.0"
export PORT="8000"
export LOG_LEVEL="INFO"

# CORS (for frontend integration)
export CORS_ORIGINS="http://localhost:3000,https://your-frontend.vercel.app"

# Resource Limits
export MAX_EXECUTION_TIME="300"    # 5 minutes
export MAX_MEMORY="512m"
export MAX_CPU="1.0"

# Rate Limiting
export RATE_LIMIT_ENABLED="true"
export RATE_LIMIT_MAX_REQUESTS="100"
export RATE_LIMIT_WINDOW="60"      # seconds
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
agent init --name my-agent
```

**"Cannot connect to API server"**
```bash
# For production deployment, check service status
curl https://agent-runner-production-f78a.up.railway.app/health

# For local development, make sure backend is running
docker-compose up -d
curl http://localhost:8000/health
```

**"Invalid zip file"**
```bash
# Check for syntax errors
python -m py_compile main.py

# Try re-deploying
agent deploy

# For local testing
agent deploy --api-url http://localhost:8000
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
npm install
npm run dev

# Terminal 3: Deploy an agent to local server
agent init --name test-agent
# Edit main.py and .env
agent deploy --api-url http://localhost:8000
```

Visit:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

## Documentation

- **DEPLOY.md**: Detailed deployment guide
- **frontend/README.md**: Frontend documentation
- **CLAUDE.md**: Architecture and development guidelines
- **examples/**: Working examples for each framework

## Troubleshooting

デプロイ時にエラーが発生した場合は、[トラブルシューティングガイド (TROUBLESHOOTING.md)](./TROUBLESHOOTING.md) を参照してください。

よくあるエラーと解決方法：
- **`Directory 'xxx' does not exist`** - StaticFilesの相対パス問題
- **`No module named 'xxx'`** - requirements.txtに依存関係を追加
- **`Permission denied`** - ファイル書き込み先をデプロイメントディレクトリ内に変更
- **`Agent handler not registered`** - main.pyでserve()を呼ぶ
- **`Deployment failed: 502`** - Railwayのデプロイ完了を待つ

詳細な解決方法は [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) を参照してください。

## Contributing

We welcome contributions! See `CLAUDE.md` for development guidelines.

## License

MIT License - See LICENSE file

## Support

- **Issues**: [GitHub Issues](https://github.com/axen/runtime-app/issues)
- **Troubleshooting**: [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
- **Migration Guide**: [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md)
- **Documentation**: See `DEPLOY.md` and `examples/`
- **Architecture**: See `CLAUDE.md`

---

**Built with the Agent Platform SDK** - Deploy and share AI agents in one command.
