"""Connection resilience helpers for the sshuttle command-line client."""
from __future__ import annotations

import shlex
import time
from dataclasses import dataclass
from typing import Callable, Sequence

from sshuttle.helpers import log


@dataclass(frozen=True)
class RetryPolicy:
    """Bounded exponential retry policy."""

    initial: float = 1.0
    maximum: float = 30.0

    def delay_after(self, failures: int) -> float:
        return min(self.maximum, self.initial * (2 ** max(0, failures - 1)))


def add_keepalives(ssh_cmd: str | None, interval: int, count: int) -> str | None:
    """Add OpenSSH liveness options to the default SSH command only.

    ``None`` is sshuttle's native spelling for the default ``ssh`` command.
    A user-supplied command is returned byte-for-byte unchanged.
    """
    if ssh_cmd is not None:
        return ssh_cmd
    return shlex.join([
        "ssh",
        "-o", f"ServerAliveInterval={interval}",
        "-o", f"ServerAliveCountMax={count}",
        "-o", "TCPKeepAlive=yes",
    ])


def run_with_retries(
    run_once: Callable[[], int],
    policy: RetryPolicy = RetryPolicy(),
    max_restarts: int | None = None,
    sleeper: Callable[[float], None] = time.sleep,
) -> int:
    """Run sshuttle, restarting it after abnormal exits.

    ``max_restarts`` counts failures, not total runs. A normal exit is returned
    immediately. Interrupts are deliberately not caught so the command-line
    layer can retain its existing KeyboardInterrupt handling.
    """
    failures = 0
    while True:
        returncode = run_once()
        if returncode == 0:
            return 0

        failures += 1
        log("sshuttle exited with status %d; reconnecting (attempt %d)" %
            (returncode, failures))
        if max_restarts is not None and failures > max_restarts:
            log("restart limit (%d) reached" % max_restarts)
            return returncode
        delay = policy.delay_after(failures)
        log("waiting %.1f seconds before reconnect" % delay)
        sleeper(delay)
