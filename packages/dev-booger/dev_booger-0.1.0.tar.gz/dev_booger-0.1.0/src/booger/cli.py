"""CLI entry point for booger."""

import asyncio
import signal
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.text import Text

from .discovery import DiscoveryResult, discover_command
from .mcp_server import create_mcp_server
from .process import ProcessManager
from .store import LogStore


console = Console()

# Color map for different ports (cycles through)
PORT_COLORS = [
    "cyan",
    "green",
    "yellow",
    "magenta",
    "blue",
    "red",
]


def get_port_color(port: int, ports: list[int]) -> str:
    """Get a consistent color for a port."""
    try:
        idx = ports.index(port)
    except ValueError:
        idx = port
    return PORT_COLORS[idx % len(PORT_COLORS)]


@click.command()
@click.argument("ports", nargs=-1, type=int, required=False)
@click.option(
    "--mcp",
    is_flag=True,
    help="Run in MCP server mode (stdio transport for Claude Code)",
)
@click.option(
    "-c", "--command",
    multiple=True,
    help="Explicit command mapping: -c 8501='uvicorn app:main --port 8501'",
)
def main(ports: tuple[int, ...], mcp: bool, command: tuple[str, ...]):
    """
    Aggregate logs from multiple dev servers.

    Usage:
        booger 8501 8080 3000    # Auto-discover commands from booger.json/package.json
        booger --mcp             # Run as MCP server for Claude Code

    Examples:
        booger 8501 8080         # Run servers on ports 8501 and 8080
        booger -c 8501='uvicorn app:main --port 8501' -c 3000='npm run dev'
    """
    if mcp:
        run_mcp_server()
        return

    if not ports and not command:
        console.print("[red]Error:[/red] Specify ports or use --mcp mode")
        console.print("\nUsage: booger 8501 8080 3000")
        console.print("       booger --mcp")
        sys.exit(1)

    # Parse explicit commands
    explicit_commands: dict[int, str] = {}
    for cmd_spec in command:
        if "=" in cmd_spec:
            port_str, cmd = cmd_spec.split("=", 1)
            try:
                explicit_commands[int(port_str)] = cmd
            except ValueError:
                console.print(f"[red]Error:[/red] Invalid port in: {cmd_spec}")
                sys.exit(1)

    asyncio.run(run_aggregator(list(ports), explicit_commands))


def run_mcp_server():
    """Run in MCP server mode for Claude Code integration."""
    from .mcp_server import mcp
    mcp.run()


async def run_aggregator(ports: list[int], explicit_commands: dict[int, str]):
    """Run the log aggregator with the specified ports."""
    store = LogStore()
    manager = ProcessManager(store)
    cwd = Path.cwd()

    # Discover or use explicit commands
    port_results: dict[int, DiscoveryResult] = {}
    missing_ports: list[int] = []

    for port in ports:
        if port in explicit_commands:
            port_results[port] = DiscoveryResult(
                command=explicit_commands[port],
                source="command line",
                confidence="explicit",
            )
        else:
            result = discover_command(port, cwd)
            if result:
                port_results[port] = result
            else:
                missing_ports.append(port)

    # Add any explicit commands for ports not in the ports list
    for port, cmd in explicit_commands.items():
        if port not in port_results:
            port_results[port] = DiscoveryResult(
                command=cmd,
                source="command line",
                confidence="explicit",
            )
            ports.append(port)

    if missing_ports:
        console.print(f"[red]Error:[/red] Could not discover commands for ports: {missing_ports}")
        console.print("\nCreate a booger.json file:")
        console.print('  {"ports": {"' + str(missing_ports[0]) + '": "your-command-here"}}')
        console.print("\nOr use explicit commands:")
        console.print(f"  booger -c {missing_ports[0]}='your-command-here'")
        sys.exit(1)

    # Print startup info
    console.print("[bold]Booger[/bold] - Multi-port log aggregator\n")
    all_ports = sorted(port_results.keys())
    for port in all_ports:
        result = port_results[port]
        color = get_port_color(port, all_ports)
        source_info = f"[dim](from: {result.source})[/dim]"
        if result.framework:
            source_info = f"[dim](from: {result.source}, {result.framework})[/dim]"
        console.print(f"  [{color}][{port}][/{color}] {result.command} {source_info}")
    console.print()

    # Setup signal handlers
    loop = asyncio.get_event_loop()
    shutdown_event = asyncio.Event()

    def handle_signal():
        console.print("\n[yellow]Shutting down...[/yellow]")
        shutdown_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, handle_signal)

    # Log callback for real-time output
    def on_log(port: int, message: str, stream: str):
        color = get_port_color(port, all_ports)
        prefix = Text(f"[{port}] ", style=color)
        console.print(prefix, message, highlight=False)

    # Start all processes
    for port, result in port_results.items():
        try:
            await manager.start_process(port, result.command, on_log)
            console.print(f"[green]Started[/green] port {port}")
        except Exception as e:
            console.print(f"[red]Failed to start port {port}:[/red] {e}")

    console.print("[dim]Press Ctrl+C to stop all processes[/dim]\n")

    # Wait for shutdown or all processes to exit
    try:
        while not shutdown_event.is_set():
            # Check if all processes have exited
            if not any(manager.is_running(p) for p in port_results):
                console.print("[yellow]All processes have exited[/yellow]")
                break
            await asyncio.sleep(0.5)
    except asyncio.CancelledError:
        pass

    # Cleanup
    await manager.stop_all()
    console.print("[green]All processes stopped[/green]")


if __name__ == "__main__":
    main()
