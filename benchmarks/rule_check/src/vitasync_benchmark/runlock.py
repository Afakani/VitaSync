"""One benchmark at a time per machine.

Parallel runs share the GPU of the same Ollama server; that slowed generation
about fourfold and caused timeouts (2026-10-29). The lock file holds the PID of
the running benchmark; a lock whose process is gone is taken over.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

LOCK = Path(tempfile.gettempdir()) / "vitasync_rule_check.lock"


class RunLocked(Exception):
    """Another benchmark run is active on this machine."""


def _alive(pid: int) -> bool:
    if sys.platform == "win32":
        import ctypes
        handle = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not handle:
            return False
        code = ctypes.c_ulong()
        ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(code))
        ctypes.windll.kernel32.CloseHandle(handle)
        return code.value == 259  # STILL_ACTIVE
    try:
        os.kill(pid, 0)  # signal 0 only checks existence on POSIX
    except OSError:
        return False
    return True


class RunLock:
    def __init__(self, path: Path | None = None):
        self.path = path or LOCK

    def acquire(self) -> None:
        try:
            other = int(self.path.read_text(encoding="ascii").strip() or 0)
        except (FileNotFoundError, ValueError):
            other = 0
        # A lock left by this very process (e.g. an earlier call that failed) is not a second run.
        if other and other != os.getpid() and _alive(other):
            raise RunLocked(f"Es läuft bereits ein Benchmark (PID {other}). Läufe nacheinander starten; "
                            f"parallele Läufe teilen sich die GPU und verfälschen Zeiten und Timeouts.")
        self.path.write_text(str(os.getpid()), encoding="ascii")

    def release(self) -> None:
        try:
            if self.path.read_text(encoding="ascii").strip() == str(os.getpid()):
                self.path.unlink()
        except FileNotFoundError:
            pass
