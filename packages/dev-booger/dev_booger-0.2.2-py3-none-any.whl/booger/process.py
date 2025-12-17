"""Process spawning and stdout/stderr capture."""

import asyncio
import os
import signal
from typing import Callable

from .store import LogStore


class ProcessManager:
    """Manages multiple child processes with log capture."""

    def __init__(self, store: LogStore):
        self.store = store
        self.processes: dict[int, asyncio.subprocess.Process] = {}
        self._shutdown_event = asyncio.Event()

    async def start_process(
        self,
        port: int,
        command: str,
        on_log: Callable[[int, str, str], None] | None = None,
    ) -> asyncio.subprocess.Process:
        """
        Start a process and capture its output.

        Args:
            port: Port number (used as identifier)
            command: Shell command to run
            on_log: Callback(port, message, stream) for each log line
        """
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        env["FORCE_COLOR"] = "1"

        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
            preexec_fn=os.setsid if hasattr(os, "setsid") else None,
        )

        self.processes[port] = proc

        # Start readers for stdout and stderr
        asyncio.create_task(
            self._read_stream(port, proc.stdout, "stdout", on_log),
            name=f"stdout-{port}",
        )
        asyncio.create_task(
            self._read_stream(port, proc.stderr, "stderr", on_log),
            name=f"stderr-{port}",
        )

        return proc

    async def _read_stream(
        self,
        port: int,
        stream: asyncio.StreamReader | None,
        stream_name: str,
        on_log: Callable[[int, str, str], None] | None,
    ):
        """Read lines from a stream and store them."""
        if stream is None:
            return

        while True:
            try:
                line = await stream.readline()
                if not line:
                    break

                message = line.decode("utf-8", errors="replace").rstrip()
                if not message:
                    continue

                # Store in log store
                self.store.add(port, message, stream=stream_name)

                # Callback for real-time output
                if on_log:
                    on_log(port, message, stream_name)

            except Exception:
                break

    async def stop_process(self, port: int, timeout: float = 5.0):
        """Stop a specific process gracefully."""
        proc = self.processes.get(port)
        if proc is None or proc.returncode is not None:
            return

        # Try SIGTERM first
        try:
            if hasattr(os, "killpg"):
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            else:
                proc.terminate()
        except (ProcessLookupError, OSError):
            return

        # Wait for graceful shutdown
        try:
            await asyncio.wait_for(proc.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            # Force kill
            try:
                if hasattr(os, "killpg"):
                    os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                else:
                    proc.kill()
            except (ProcessLookupError, OSError):
                pass

    async def stop_all(self, timeout: float = 5.0):
        """Stop all processes gracefully."""
        self._shutdown_event.set()

        tasks = [
            self.stop_process(port, timeout)
            for port in list(self.processes.keys())
        ]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def wait_all(self):
        """Wait for all processes to complete."""
        tasks = [
            proc.wait()
            for proc in self.processes.values()
            if proc.returncode is None
        ]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def is_running(self, port: int) -> bool:
        """Check if a process is still running."""
        proc = self.processes.get(port)
        return proc is not None and proc.returncode is None

    def get_status(self) -> dict[int, str]:
        """Get status of all processes."""
        return {
            port: "running" if self.is_running(port) else "stopped"
            for port in self.processes
        }
