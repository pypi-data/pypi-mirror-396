"""Resource management and timeout utilities for tgwrap."""

import signal
import subprocess
import time
from contextlib import contextmanager
from typing import Generator, Optional


class ResourceTimeoutError(Exception):
    """Raised when an operation times out."""


@contextmanager
def timeout_handler(seconds: int) -> Generator[None, None, None]:
    """Context manager to handle operation timeouts."""
    def timeout_signal_handler(signum, frame):  # pylint: disable=unused-argument
        raise ResourceTimeoutError(f"Operation timed out after {seconds} seconds")

    # Set up signal handler
    old_handler = signal.signal(signal.SIGALRM, timeout_signal_handler)
    signal.alarm(seconds)

    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)


def run_with_timeout(
    command: list[str],
    timeout: int = 300,
    working_dir: Optional[str] = None,
    capture_output: bool = True
) -> subprocess.CompletedProcess:
    """Run a command with timeout and resource limits."""
    try:
        result = subprocess.run(
            command,
            timeout=timeout,
            cwd=working_dir,
            capture_output=capture_output,
            text=True,
            check=False
        )
        return result
    except subprocess.TimeoutExpired as e:
        raise ResourceTimeoutError(
            f"Command timed out after {timeout} seconds: {' '.join(command)}"
        ) from e


class ResourceMonitor:
    """Monitor system resources during command execution."""

    def __init__(self):
        self.start_time = None
        self.peak_memory = 0

    def start(self):
        """Start monitoring resources."""
        self.start_time = time.time()

    def stop(self) -> dict:
        """Stop monitoring and return resource usage."""
        if self.start_time is None:
            return {}

        duration = time.time() - self.start_time
        return {
            "duration_seconds": duration,
            "peak_memory_mb": self.peak_memory
        }

    @contextmanager
    def monitor(self) -> Generator[dict, None, None]:
        """Context manager for monitoring resource usage."""
        self.start()
        stats = {}
        try:
            yield stats
        finally:
            stats.update(self.stop())
