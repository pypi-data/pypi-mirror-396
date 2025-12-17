import json
import os
import subprocess
import tempfile
from orchestral.tools.base.tool import BaseTool
from orchestral.tools.base.field_utils import RuntimeField, StateField


class RunPythonTool(BaseTool):
    """Execute Python code quickly for calculations and data processing. Always uses temporary files.

    Available packages: numpy, pandas, matplotlib, scipy, requests, pillow (PIL), json, os, sys, math, datetime, random
    Remember to use print() to see output - only printed results are returned.

    Example: print(np.mean([1,2,3,4,5])) or df = pd.DataFrame({'a': [1,2,3]}); print(df.describe())"""

    # Runtime fields - provided by LLM
    code: str | None = RuntimeField(description="The Python code to execute. Use print() to see output - only printed results are returned")
    timeout: int | str = RuntimeField(default=10, description="Maximum execution time in seconds")

    # State fields - internal configuration
    base_directory: str = StateField(default="./", description="Working directory for script execution")

    def _run(self) -> str:
        """Execute Python code and return structured output."""
        if self.code is None:
            return self.format_error(
                error="Missing Parameter",
                reason="Code parameter is required",
                suggestion="Provide valid Python code to execute"
            )

        # Coerce timeout to int if it's a string (some LLMs send it as string)
        if isinstance(self.timeout, str):
            try:
                self.timeout = int(self.timeout)
            except ValueError:
                return self.format_error(
                    error="Invalid Parameter",
                    reason=f"timeout must be a number, got: {self.timeout}",
                    suggestion="Provide timeout as an integer"
                )

        # Always use a temporary file for quick execution
        temp_file = tempfile.NamedTemporaryFile(suffix=".py", delete=False)
        temp_file_path = temp_file.name
        temp_file.close()  # Close it so we can write to it later

        try:
            # Write the Python script
            with open(temp_file_path, "w", encoding="utf-8") as file:
                file.write(self.code)

            # Run the script
            result = subprocess.run(
                ['python', temp_file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=self.timeout,
                cwd=self.base_directory
            )

            # Prepare structured response and return as a string
            response = {
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "return_code": result.returncode
            }

            return json.dumps(response, ensure_ascii=False)

        except subprocess.TimeoutExpired:
            return json.dumps({
                "stdout": "",
                "stderr": f"Script timed out after {self.timeout} seconds",
                "return_code": 1
            }, ensure_ascii=False)

        except Exception as e:
            return json.dumps({
                "stdout": "",
                "stderr": f"An error occurred while running the script: {e}",
                "return_code": 1
            }, ensure_ascii=False)

        finally:
            # Always clean up the temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)