"""
Simplified Windows persistent terminal using PowerShell subprocess.
No wexpect, no boot markers. Clean, minimal, and reliable.
"""

import os
import time
import random
import subprocess
from dataclasses import dataclass
from typing import Optional


@dataclass
class TerminalResult:
    command: str
    output: str
    return_code: int
    execution_time: float


class TerminalSessionError(Exception):
    pass


class PersistentTerminal:
    def __init__(self):
        self._proc: Optional[subprocess.Popen] = None
        self._working_directory: Optional[str] = None

    def start_session(self, working_dir: str) -> None:
        """Start a persistent PowerShell process."""
        if self._proc:
            self.close()

        working_dir = os.path.abspath(working_dir)
        if not os.path.exists(working_dir):
            raise TerminalSessionError(f"Working directory does not exist: {working_dir}")

        # Prefer pwsh if available
        ps_exe = "pwsh" if self._has_pwsh() else "powershell"

        try:
            self._proc = subprocess.Popen(
                [ps_exe, "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", "-"],
                cwd=working_dir,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                bufsize=1,  # line-buffered
            )
            self._working_directory = working_dir
        except Exception as e:
            raise TerminalSessionError(f"Failed to start PowerShell session: {e}")

    def _has_pwsh(self) -> bool:
        """Detect PowerShell 7 (pwsh) if present."""
        try:
            subprocess.run(["pwsh", "-v"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            return False

    def is_alive(self) -> bool:
        return self._proc is not None and self._proc.poll() is None

    def execute_command(self, command: str, timeout: int = 30) -> TerminalResult:
        """Execute a command and return its output and exit code."""
        if not self.is_alive():
            raise TerminalSessionError("No active PowerShell session.")

        start = time.time()
        salt = str(random.randint(100000, 999999))
        end_marker = f"__ORCH_END__{salt}"
        rc_marker = f"__ORCH_RC__{salt}"

        ps_script = (
            f"{command}\n"
            f"$code = if ($LASTEXITCODE) {{ $LASTEXITCODE }} elseif ($?) {{ 0 }} else {{ 1 }}\n"
            f"Write-Output '{rc_marker}:$code'\n"
            f"Write-Output '{end_marker}'\n"
        )

        try:
            assert self._proc.stdin and self._proc.stdout
            self._proc.stdin.write(ps_script)
            self._proc.stdin.flush()

            output_lines = []
            return_code = 0
            start_time = time.time()

            for line in self._proc.stdout:
                line = line.rstrip("\r\n")
                if line.startswith(rc_marker):
                    try:
                        return_code = int(line.split(":", 1)[1])
                    except Exception:
                        return_code = 0
                    continue
                if line == end_marker:
                    break
                output_lines.append(line)

                if time.time() - start_time > timeout:
                    raise TerminalSessionError(f"Command timed out after {timeout}s: {command}")

            output = "\n".join(output_lines).strip()
            elapsed = time.time() - start
            return TerminalResult(command, output, return_code, elapsed)

        except Exception as e:
            raise TerminalSessionError(f"Command execution failed: {e}")

    def restart_session(self, working_dir: Optional[str] = None) -> None:
        """Restart the PowerShell session."""
        if working_dir is None:
            working_dir = self._working_directory
        if not working_dir:
            raise TerminalSessionError("No working directory specified for restart")
        self.close()
        self.start_session(working_dir)

    def close(self) -> None:
        """Gracefully close the PowerShell session."""
        if self._proc:
            try:
                if self._proc.stdin:
                    self._proc.stdin.write("exit\n")
                    self._proc.stdin.flush()
            except Exception:
                pass
            try:
                self._proc.terminate()
            except Exception:
                pass
            try:
                self._proc.wait(timeout=2)
            except Exception:
                try:
                    self._proc.kill()
                except Exception:
                    pass
        self._proc = None

    def __del__(self):
        self.close()
