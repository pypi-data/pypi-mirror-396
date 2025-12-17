"""In-memory log storage with search capabilities and file persistence."""

import json
import re
import threading
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Literal


# Shared log file location
LOG_FILE = Path.home() / ".cache" / "booger" / "logs.jsonl"


LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "UNKNOWN"]


@dataclass
class LogEntry:
    """A single log entry."""
    port: int
    message: str
    level: LogLevel
    timestamp: datetime = field(default_factory=datetime.now)
    stream: Literal["stdout", "stderr"] = "stdout"

    def to_dict(self) -> dict:
        return {
            "port": self.port,
            "message": self.message,
            "level": self.level,
            "timestamp": self.timestamp.isoformat(),
            "stream": self.stream,
        }


class LogStore:
    """Thread-safe in-memory log storage with ring buffer per port and optional file persistence."""

    # Patterns to detect log levels
    LEVEL_PATTERNS = [
        (re.compile(r"\bDEBUG\b", re.IGNORECASE), "DEBUG"),
        (re.compile(r"\bINFO\b", re.IGNORECASE), "INFO"),
        (re.compile(r"\bWARN(?:ING)?\b", re.IGNORECASE), "WARNING"),
        (re.compile(r"\bERR(?:OR)?\b", re.IGNORECASE), "ERROR"),
    ]

    def __init__(self, max_lines_per_port: int = 5000, persist: bool = False):
        self.max_lines = max_lines_per_port
        self.logs: dict[int, deque[LogEntry]] = {}
        self._lock = threading.Lock()
        self.persist = persist

        # Create log directory if persisting
        if persist:
            LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    def _detect_level(self, message: str, stream: str) -> LogLevel:
        """Detect log level from message content."""
        # stderr defaults to ERROR unless we find another level
        default = "ERROR" if stream == "stderr" else "UNKNOWN"

        for pattern, level in self.LEVEL_PATTERNS:
            if pattern.search(message):
                return level
        return default

    def add(
        self,
        port: int,
        message: str,
        stream: Literal["stdout", "stderr"] = "stdout",
        level: LogLevel | None = None,
    ) -> LogEntry:
        """Add a log entry for a port."""
        if level is None:
            level = self._detect_level(message, stream)

        entry = LogEntry(
            port=port,
            message=message,
            level=level,
            stream=stream,
        )

        with self._lock:
            if port not in self.logs:
                self.logs[port] = deque(maxlen=self.max_lines)
            self.logs[port].append(entry)

        # Persist to file if enabled
        if self.persist:
            with open(LOG_FILE, "a") as f:
                f.write(json.dumps(entry.to_dict()) + "\n")

        return entry

    def get(
        self,
        port: int | None = None,
        limit: int = 100,
        level: LogLevel | None = None,
    ) -> list[dict]:
        """Get recent logs, optionally filtered by port and level."""
        with self._lock:
            if port is not None:
                entries = list(self.logs.get(port, []))
            else:
                # Merge all ports, sorted by timestamp
                all_entries = []
                for port_logs in self.logs.values():
                    all_entries.extend(port_logs)
                entries = sorted(all_entries, key=lambda e: e.timestamp)

        # Filter by level if specified
        if level:
            entries = [e for e in entries if e.level == level]

        # Return most recent entries
        return [e.to_dict() for e in entries[-limit:]]

    def search(
        self,
        pattern: str,
        port: int | None = None,
        limit: int = 100,
    ) -> list[dict]:
        """Search logs by regex pattern."""
        try:
            regex = re.compile(pattern, re.IGNORECASE)
        except re.error:
            # Fall back to literal search if invalid regex
            regex = re.compile(re.escape(pattern), re.IGNORECASE)

        with self._lock:
            if port is not None:
                entries = list(self.logs.get(port, []))
            else:
                all_entries = []
                for port_logs in self.logs.values():
                    all_entries.extend(port_logs)
                entries = sorted(all_entries, key=lambda e: e.timestamp)

        matches = [e for e in entries if regex.search(e.message)]
        return [e.to_dict() for e in matches[-limit:]]

    def clear(self, port: int | None = None) -> int:
        """Clear logs, optionally for a specific port. Returns count cleared."""
        with self._lock:
            if port is not None:
                count = len(self.logs.get(port, []))
                if port in self.logs:
                    self.logs[port].clear()
            else:
                count = sum(len(q) for q in self.logs.values())
                self.logs.clear()
                # Also clear the shared log file
                if LOG_FILE.exists():
                    LOG_FILE.unlink()
        return count

    @staticmethod
    def load_from_file(
        limit: int = 100,
        port: int | None = None,
        level: str | None = None,
    ) -> list[dict]:
        """
        Load logs from the shared log file.

        Used by MCP server to read logs written by CLI process.
        """
        if not LOG_FILE.exists():
            return []

        entries = []
        try:
            with open(LOG_FILE) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        # Filter by port
                        if port is not None and entry.get("port") != port:
                            continue
                        # Filter by level
                        if level is not None and entry.get("level") != level:
                            continue
                        entries.append(entry)
                    except json.JSONDecodeError:
                        continue
        except OSError:
            return []

        # Return most recent entries
        return entries[-limit:]

    @staticmethod
    def search_from_file(
        pattern: str,
        port: int | None = None,
        limit: int = 100,
    ) -> list[dict]:
        """Search logs from the shared log file by regex pattern."""
        if not LOG_FILE.exists():
            return []

        try:
            regex = re.compile(pattern, re.IGNORECASE)
        except re.error:
            regex = re.compile(re.escape(pattern), re.IGNORECASE)

        entries = []
        try:
            with open(LOG_FILE) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        if port is not None and entry.get("port") != port:
                            continue
                        if regex.search(entry.get("message", "")):
                            entries.append(entry)
                    except json.JSONDecodeError:
                        continue
        except OSError:
            return []

        return entries[-limit:]

    @staticmethod
    def clear_file(port: int | None = None) -> int:
        """Clear the shared log file. Returns count of entries cleared."""
        if not LOG_FILE.exists():
            return 0

        if port is None:
            # Clear entire file
            try:
                with open(LOG_FILE) as f:
                    count = sum(1 for _ in f)
                LOG_FILE.unlink()
                return count
            except OSError:
                return 0
        else:
            # Filter out entries for specific port
            try:
                with open(LOG_FILE) as f:
                    lines = f.readlines()

                remaining = []
                count = 0
                for line in lines:
                    try:
                        entry = json.loads(line.strip())
                        if entry.get("port") == port:
                            count += 1
                        else:
                            remaining.append(line)
                    except json.JSONDecodeError:
                        remaining.append(line)

                with open(LOG_FILE, "w") as f:
                    f.writelines(remaining)

                return count
            except OSError:
                return 0

    @staticmethod
    def file_stats() -> dict:
        """Get statistics about the shared log file."""
        if not LOG_FILE.exists():
            return {"ports": [], "total_entries": 0, "entries_per_port": {}}

        ports: dict[int, int] = {}
        total = 0

        try:
            with open(LOG_FILE) as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        port = entry.get("port")
                        if port is not None:
                            ports[port] = ports.get(port, 0) + 1
                            total += 1
                    except json.JSONDecodeError:
                        continue
        except OSError:
            pass

        return {
            "ports": list(ports.keys()),
            "total_entries": total,
            "entries_per_port": ports,
        }

    def get_ports(self) -> list[int]:
        """Get list of ports with logs."""
        with self._lock:
            return list(self.logs.keys())

    def stats(self) -> dict:
        """Get statistics about stored logs."""
        with self._lock:
            return {
                "ports": list(self.logs.keys()),
                "total_entries": sum(len(q) for q in self.logs.values()),
                "entries_per_port": {p: len(q) for p, q in self.logs.items()},
            }


# Global store instance
store = LogStore()
