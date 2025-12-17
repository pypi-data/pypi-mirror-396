"""MCP server exposing log tools for Claude Code."""

from fastmcp import FastMCP

from .store import LogStore


def create_mcp_server() -> FastMCP:
    """Create an MCP server with log tools that read from the shared log file."""

    mcp = FastMCP(name="booger")

    @mcp.tool()
    def get_logs(
        port: int | None = None,
        limit: int = 100,
        level: str | None = None,
    ) -> list[dict]:
        """
        Get recent logs from all ports or a specific port.

        Reads from the shared log file written by `booger <ports>` CLI.

        Args:
            port: Filter by port number (None for all ports)
            limit: Maximum number of logs to return (default 100)
            level: Filter by level: DEBUG, INFO, WARNING, ERROR

        Returns:
            List of log entries with port, message, level, timestamp
        """
        return LogStore.load_from_file(limit=limit, port=port, level=level)

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
        return LogStore.search_from_file(pattern=pattern, port=port, limit=limit)

    @mcp.tool()
    def clear_logs(port: int | None = None) -> str:
        """
        Clear logs from the shared log file.

        Args:
            port: Clear only this port's logs (None for all)

        Returns:
            Confirmation message with count of cleared entries
        """
        count = LogStore.clear_file(port=port)
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
        return LogStore.file_stats()

    return mcp


# Default server instance
mcp = create_mcp_server()
