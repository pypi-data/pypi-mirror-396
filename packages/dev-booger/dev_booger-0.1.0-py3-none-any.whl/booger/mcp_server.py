"""MCP server exposing log tools for Claude Code."""

from fastmcp import FastMCP

from .store import LogStore, store as default_store


def create_mcp_server(log_store: LogStore | None = None) -> FastMCP:
    """Create an MCP server with log tools."""

    store = log_store or default_store
    mcp = FastMCP(name="booger")

    @mcp.tool()
    def get_logs(
        port: int | None = None,
        limit: int = 100,
        level: str | None = None,
    ) -> list[dict]:
        """
        Get recent logs from all ports or a specific port.

        Args:
            port: Filter by port number (None for all ports)
            limit: Maximum number of logs to return (default 100)
            level: Filter by level: DEBUG, INFO, WARNING, ERROR

        Returns:
            List of log entries with port, message, level, timestamp
        """
        return store.get(port=port, limit=limit, level=level)

    @mcp.tool()
    def search_logs(
        pattern: str,
        port: int | None = None,
        limit: int = 100,
    ) -> list[dict]:
        """
        Search logs by regex pattern.

        Args:
            pattern: Regex pattern to search for (case-insensitive)
            port: Filter by port number (None for all ports)
            limit: Maximum number of results (default 100)

        Returns:
            List of matching log entries
        """
        return store.search(pattern=pattern, port=port, limit=limit)

    @mcp.tool()
    def clear_logs(port: int | None = None) -> str:
        """
        Clear logs from memory.

        Args:
            port: Clear only this port's logs (None for all)

        Returns:
            Confirmation message with count of cleared entries
        """
        count = store.clear(port=port)
        if port:
            return f"Cleared {count} log entries from port {port}"
        return f"Cleared {count} log entries from all ports"

    @mcp.tool()
    def get_log_stats() -> dict:
        """
        Get statistics about stored logs.

        Returns:
            Dict with ports, total entries, and entries per port
        """
        return store.stats()

    return mcp


# Default server instance
mcp = create_mcp_server()
