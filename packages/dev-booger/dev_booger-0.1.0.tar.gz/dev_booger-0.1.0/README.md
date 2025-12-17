# dev-booger

Multi-port log aggregator with MCP integration for Claude Code.

Run multiple dev servers and aggregate their logs in one terminal with color-coded output.

## Installation

```bash
pip install dev-booger
# or
uv add dev-booger
# or (recommended for CLI tools)
pipx install dev-booger
```

## Usage

### Basic Usage

```bash
# Auto-discover and run servers on specified ports
booger 3000 8000 8501

# With explicit commands
booger -c "3000=npm run dev" -c "8000=uvicorn app:main --port 8000"
```

### MCP Mode (for Claude Code)

```bash
# Run as MCP server
booger --mcp
```

Add to `~/.claude.json`:
```json
{
  "mcpServers": {
    "booger": {
      "type": "stdio",
      "command": "booger",
      "args": ["--mcp"]
    }
  }
}
```

Then use MCP tools in Claude Code:
- `get_logs(port=3000)` - fetch logs from a port
- `search_logs("error")` - search all logs
- `clear_logs()` - clear log buffer

## Auto-Discovery

Booger automatically discovers what commands to run by checking:

1. `booger.json` - explicit port→command mapping
2. `docker-compose.yml` - service port mappings
3. `Dockerfile` - EXPOSE directives
4. `.env` files - PORT variables
5. `package.json` - npm scripts with port patterns
6. `pyproject.toml` - Python framework detection
7. `Procfile` - Heroku-style process definitions
8. `Makefile` - dev/run targets

### Framework Defaults

| Framework | Default Port |
|-----------|--------------|
| Next.js | 3000 |
| Vite | 5173 |
| FastAPI | 8000 |
| Flask | 5000 |
| Streamlit | 8501 |

## Configuration

Create a `booger.json` in your project:

```json
{
  "ports": {
    "3000": "npm run dev",
    "8000": "uvicorn app:main --port 8000 --reload",
    "8501": "streamlit run app.py"
  }
}
```

## Output

```
Booger - Multi-port log aggregator

  [3000] npm run dev (from: package.json, next)
  [8000] uvicorn app:main --port 8000 (from: booger.json)

Started port 3000
Started port 8000
Press Ctrl+C to stop all processes

[3000] - ready started server on 0.0.0.0:3000
[8000] INFO:     Application startup complete.
[8000] INFO:     127.0.0.1 - "GET /health" 200
[3000] - compiled successfully
```

## License

MIT
