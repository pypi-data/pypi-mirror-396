"""In-memory log storage with search capabilities."""

import re
import threading
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


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
    """Thread-safe in-memory log storage with ring buffer per port."""

    # Patterns to detect log levels
    LEVEL_PATTERNS = [
        (re.compile(r"\bDEBUG\b", re.IGNORECASE), "DEBUG"),
        (re.compile(r"\bINFO\b", re.IGNORECASE), "INFO"),
        (re.compile(r"\bWARN(?:ING)?\b", re.IGNORECASE), "WARNING"),
        (re.compile(r"\bERR(?:OR)?\b", re.IGNORECASE), "ERROR"),
    ]

    def __init__(self, max_lines_per_port: int = 5000):
        self.max_lines = max_lines_per_port
        self.logs: dict[int, deque[LogEntry]] = {}
        self._lock = threading.Lock()

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
        return count

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
