# Sentient CLI

The official CLI tool for the Sentient Web Platform - Deploy AI agents and MCP servers with zero friction.

## Installation

```bash
pip install sentient-cli
```

## Quick Start

1. **Authenticate with the platform:**
   ```bash
   sen auth login
   ```

2. **Initialize your project:**
   ```bash
   sen init
   ```

3. **Deploy your agent or MCP server:**
   ```bash
   sen push
   ```

## Commands

- `sen auth login` - Authenticate with Sentient Web Platform
- `sen init` - Initialize project for deployment
- `sen push` - Deploy project to platform
- `sen list` - List your deployments
- `sen logs <deployment-id>` - View deployment logs
- `sen delete <deployment-id>` - Delete a deployment

## Configuration

The CLI uses a `sentient.config.json` file in your project root to configure deployments:

```json
{
  "name": "my-agent",
  "description": "My AI agent",
  "type": "agent",
  "framework": "langchain",
  "visibility": "public",
  "runtime": "python",
  "buildCommand": "pip install -r requirements.txt",
  "startCommand": "python main.py",
  "port": 8000,
  "environment": {
    "PYTHONPATH": "."
  }
}
```

## Development

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src tests
isort src tests

# Type checking
mypy src
```