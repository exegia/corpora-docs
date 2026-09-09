# API Reference: cfabric_mcp

> Source: [https://context-fabric.ai/docs/api/cfabric_mcp](https://context-fabric.ai/docs/api/cfabric_mcp)

Context-Fabric MCP Server.

This package provides an MCP (Model Context Protocol) server that exposes Context-Fabric corpus operations to AI agents.

## Usage

```bash
# Run as CLI
cfabric-mcp
```

```python
# Or import and run programmatically
from cfabric_mcp import mcp
mcp.run(transport="stdio")
```

## Submodules

| Module | Description |
|--------|-------------|
| [cache](https://context-fabric.ai/docs/api/cfabric_mcp/cache) | Search result caching |
| [corpus_manager](https://context-fabric.ai/docs/api/cfabric_mcp/corpus_manager) | Corpus management for MCP server |
| [resources](https://context-fabric.ai/docs/api/cfabric_mcp/resources) | MCP resource definitions |
| [server](https://context-fabric.ai/docs/api/cfabric_mcp/server) | FastMCP server |
| [tools](https://context-fabric.ai/docs/api/cfabric_mcp/tools) | MCP tool implementations |
