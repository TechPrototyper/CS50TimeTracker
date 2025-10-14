#!/usr/bin/env python3
"""
SITR Server Manager

Manages uvicorn server lifecycle (start, stop, status).
Platform-independent implementation using subprocess and PID files.
"""
import os
import sys
import time
import signal
import subprocess
from pathlib import Path
from typing import Optional, Tuple
import psutil  # For cross-platform process management


class ServerManager:
    """Manages SITR API server lifecycle."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8000):
        """
        Initialize server manager.

        Args:
            host: Server host address
            port: Server port number
        """
        self.host = host
        self.port = port
        self.sitr_dir = Path.home() / ".sitr"
        self.pid_file = self.sitr_dir / "server.pid"
        self.log_file = self.sitr_dir / "server.log"

        # Ensure .sitr directory exists
        self.sitr_dir.mkdir(exist_ok=True)

    def is_running(self) -> bool:
        """
        Check if server is running.

        Returns:
            True if server is running, False otherwise
        """
        # Method 1: Check PID file
        pid = self._read_pid()
        if pid is not None:
            if self._is_process_alive(pid):
                # Verify it's actually our server
                if self._is_sitr_server(pid):
                    return True
            # PID file exists but process is dead, clean up
            self._cleanup_pid_file()

        # Method 2: Try health check
        return self._check_health()

    def start(self, background: bool = True) -> Tuple[bool, str]:
        """
        Start the API server.

        Args:
            background: Run server in background

        Returns:
            Tuple of (success, message)
        """
        if self.is_running():
            return False, "Server is already running"

        try:
            # Get path to sitr_api.py
            api_file = Path(__file__).parent / "sitr_api.py"
            if not api_file.exists():
                return False, f"API file not found: {api_file}"

            # Get Python executable from current environment
            python_exe = sys.executable

            # Build command
            cmd = [
                python_exe,
                "-m", "uvicorn",
                "sitr_api:app",
                "--host", self.host,
                "--port", str(self.port)
            ]

            if background:
                # Start in background
                with open(self.log_file, 'w') as log:
                    process = subprocess.Popen(
                        cmd,
                        stdout=log,
                        stderr=subprocess.STDOUT,
                        cwd=Path(__file__).parent,
                        start_new_session=True  # Detach from terminal
                    )

                # Save PID
                self._write_pid(process.pid)

                # Wait a moment and check if it started
                time.sleep(1)
                if self.is_running():
                    return True, (
                        f"Server started on {self.host}:{self.port} "
                        f"(PID: {process.pid})"
                    )
                else:
                    return False, "Server failed to start (check logs)"
            else:
                # Run in foreground
                process = subprocess.run(
                    cmd,
                    cwd=Path(__file__).parent
                )
                return True, "Server stopped"

        except Exception as e:
            return False, f"Failed to start server: {e}"

    def stop(self) -> Tuple[bool, str]:
        """
        Stop the API server.

        Returns:
            Tuple of (success, message)
        """
        if not self.is_running():
            self._cleanup_pid_file()
            return False, "Server is not running"

        pid = self._read_pid()
        if pid is None:
            return False, "Could not read PID file"

        try:
            # Try graceful shutdown first
            if sys.platform == "win32":
                os.kill(pid, signal.CTRL_C_EVENT)
            else:
                os.kill(pid, signal.SIGTERM)

            # Wait for process to terminate
            for _ in range(10):  # Wait up to 5 seconds
                if not self._is_process_alive(pid):
                    self._cleanup_pid_file()
                    return True, f"Server stopped (PID: {pid})"
                time.sleep(0.5)

            # Force kill if still alive
            if self._is_process_alive(pid):
                os.kill(pid, signal.SIGKILL)
                time.sleep(0.5)
                self._cleanup_pid_file()
                return True, f"Server force-stopped (PID: {pid})"

            self._cleanup_pid_file()
            return True, f"Server stopped (PID: {pid})"

        except ProcessLookupError:
            self._cleanup_pid_file()
            return True, "Server was not running"
        except PermissionError:
            return False, "Permission denied to stop server"
        except Exception as e:
            return False, f"Failed to stop server: {e}"

    def status(self) -> Tuple[bool, str]:
        """
        Get server status.

        Returns:
            Tuple of (is_running, status_message)
        """
        if self.is_running():
            pid = self._read_pid()
            return True, (
                f"Server is running on {self.host}:{self.port} "
                f"(PID: {pid})"
            )
        else:
            return False, "Server is not running"

    def restart(self) -> Tuple[bool, str]:
        """
        Restart the server.

        Returns:
            Tuple of (success, message)
        """
        # Stop if running
        if self.is_running():
            success, msg = self.stop()
            if not success:
                return False, f"Failed to stop server: {msg}"

        # Start server
        return self.start()

    def get_logs(self, lines: int = 50) -> str:
        """
        Get server log tail.

        Args:
            lines: Number of lines to return

        Returns:
            Log content
        """
        if not self.log_file.exists():
            return "No logs available"

        try:
            with open(self.log_file, 'r') as f:
                all_lines = f.readlines()
                return "".join(all_lines[-lines:])
        except IOError:
            return "Could not read log file"

    # Private helper methods

    def _read_pid(self) -> Optional[int]:
        """Read PID from file."""
        if not self.pid_file.exists():
            return None

        try:
            pid = int(self.pid_file.read_text().strip())
            return pid
        except (ValueError, IOError):
            return None

    def _write_pid(self, pid: int):
        """Write PID to file."""
        try:
            self.pid_file.write_text(str(pid))
        except IOError as e:
            print(f"Warning: Could not write PID file: {e}")

    def _cleanup_pid_file(self):
        """Remove PID file."""
        try:
            if self.pid_file.exists():
                self.pid_file.unlink()
        except IOError:
            pass

    def _is_process_alive(self, pid: int) -> bool:
        """Check if process with PID is alive."""
        try:
            # Use psutil for cross-platform process check
            return psutil.pid_exists(pid)
        except Exception:
            # Fallback to os.kill(pid, 0)
            try:
                os.kill(pid, 0)
                return True
            except (OSError, ProcessLookupError):
                return False

    def _is_sitr_server(self, pid: int) -> bool:
        """Check if process is actually our server."""
        try:
            proc = psutil.Process(pid)
            cmdline = " ".join(proc.cmdline())
            return "sitr_api" in cmdline or "uvicorn" in cmdline
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False

    def _check_health(self) -> bool:
        """Check server health via HTTP."""
        try:
            import requests
            response = requests.get(
                f"http://{self.host}:{self.port}/health",
                timeout=2
            )
            return response.status_code == 200
        except Exception:
            return False


# Singleton instance
_server_manager: Optional[ServerManager] = None


def get_server_manager(
    host: str = "127.0.0.1",
    port: int = 8000
) -> ServerManager:
    """Get singleton server manager instance."""
    global _server_manager
    if _server_manager is None:
        _server_manager = ServerManager(host, port)
    return _server_manager
