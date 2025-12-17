"""
Windows persistent terminal implementation using wexpect with robust
per-command sentinels instead of relying on the shell prompt.
"""
# THIS ONE IS NOT CURRENTLY WORKING AND TENDS TO HANG WHEN USED.
import os
import time
import random
from dataclasses import dataclass
from typing import Optional

try:
    import wexpect
except ImportError:
    raise ImportError(
        "wexpect is required for persistent terminal sessions on Windows. "
        "Install it with: pip install wexpect"
    )


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
        self._session: Optional[wexpect.spawn] = None
        self._working_directory: Optional[str] = None
        # Keep a simple prompt for health checks only
        self._prompt_marker = "ORCHTERM_READY>"
        # $G expands to >
        self._prompt_cmd = f'prompt {self._prompt_marker[:-1]}$G'

    def start_session(self, working_dir: str) -> None:
        if self._session:
            self.close()

        working_dir = os.path.abspath(working_dir)
        if not os.path.exists(working_dir):
            raise TerminalSessionError(f"Working directory does not exist: {working_dir}")

        try:
            # Start quiet, persistent cmd with UTF-8 code page and deterministic prompt
            # /Q = turn echo off, /K = run and remain
            self._session = wexpect.spawn(
                'cmd.exe /Q /K',
                cwd=working_dir,
                timeout=30,
                encoding='utf-8',
                codec_errors='replace',
            )
            # Reduce timing issues on some consoles
            self._session.delaybeforesend = 0.05

            # Force UTF-8 to avoid mojibake in expect
            self._session.sendline('chcp 65001>nul')
            # Deterministic prompt for health checks
            self._session.sendline(self._prompt_cmd)

            # Move into target directory
            self._session.sendline(f'cd /d "{working_dir}"')

            # Nudge to a clean prompt
            self._session.sendline('')
            # Do a quick health check wait
            self._expect_prompt(timeout=10)

            self._working_directory = working_dir

        except (wexpect.EOF, wexpect.TIMEOUT, wexpect.wexpect_error) as e:
            raise TerminalSessionError(f"Failed to start terminal session: {e}")

    def _expect_prompt(self, timeout: int) -> None:
        # Use exact match to avoid regex surprises on Windows shells
        self._session.expect_exact(self._prompt_marker, timeout=timeout)
        # Drain residual buffer if any
        try:
            self._session.read_nonblocking(size=1000, timeout=0.05)
        except Exception:
            pass

    def is_alive(self) -> bool:
        if not self._session or not self._session.isalive():
            return False
        try:
            self._session.sendline('')
            self._session.expect_exact(self._prompt_marker, timeout=3)
            return True
        except (wexpect.EOF, wexpect.TIMEOUT):
            return False

    def execute_command(self, command: str, timeout: int = 30) -> TerminalResult:
        if not self._session:
            raise TerminalSessionError("No active session. Call start_session() first.")
        if not self.is_alive():
            raise TerminalSessionError("Session is not responsive. Restart required.")

        start_time = time.time()

        # Unique per-command sentinels
        salt = f"{random.randint(100000, 999999)}"
        end_token = f"__ORCH_END__{salt}"
        rc_token = f"__ORCH_RC__{salt}"

        # We chain the user command, then echo the errorlevel and an end marker.
        # Using & ensures the last RHS exit code is the user command's exit code.
        sentinel_cmd = (
            f'({command}) & echo {rc_token}:%ERRORLEVEL% & echo {end_token}'
        )

        try:
            self._session.sendline(sentinel_cmd)

            # Read until the unique end marker is seen, with a hard timeout
            # Use exact matching to avoid regex pitfalls
            self._session.expect_exact(end_token, timeout=timeout)

            # Everything prior to the end token is in before
            chunk = self._session.before or ""
            # Now wait for the prompt again to return to idle state
            # Give a small bounded wait so we never hang indefinitely here
            try:
                self._session.expect_exact(self._prompt_marker, timeout=5)
            except wexpect.TIMEOUT:
                # Not fatal; we already captured the output and rc marker
                pass

            # Normalize and clean output
            text = chunk.replace('\r\n', '\n').replace('\r', '\n')

            # Extract return code line
            return_code = 0
            output_lines = []
            for ln in text.split('\n'):
                s = ln.strip()
                if s.startswith(rc_token + ":"):
                    try:
                        return_code = int(s.split(":", 1)[1])
                    except Exception:
                        return_code = 0
                    continue
                # Skip empty and prompt echoes
                if not s or s == self._prompt_marker:
                    continue
                output_lines.append(ln)

            output = '\n'.join(output_lines).strip()

            execution_time = time.time() - start_time
            return TerminalResult(
                command=command,
                output=output,
                return_code=return_code,
                execution_time=execution_time,
            )

        except wexpect.TIMEOUT:
            execution_time = time.time() - start_time
            raise TerminalSessionError(
                f"Command timed out after {timeout}s: {command}\n"
                f"Partial output: {(self._session.before or '')[:500]}"
            )
        except wexpect.EOF:
            raise TerminalSessionError(f"Session terminated unexpectedly during command: {command}")

    def restart_session(self, working_dir: Optional[str] = None) -> None:
        if working_dir is None:
            working_dir = self._working_directory
        if working_dir is None:
            raise TerminalSessionError("No working directory specified for restart")
        self.close()
        self.start_session(working_dir)

    def close(self) -> None:
        if self._session:
            try:
                if self._session.isalive():
                    self._session.sendline('exit')
                    self._session.expect(wexpect.EOF, timeout=3)
            except (wexpect.TIMEOUT, wexpect.EOF):
                pass
            finally:
                self._session.close()
                self._session = None

    def __del__(self):
        self.close()
