"""Result types for SwarmKit SDK."""

from dataclasses import dataclass


@dataclass
class ExecuteResult:
    """Execution result.

    Attributes:
        sandbox_id: Sandbox ID
        exit_code: Command exit code
        stdout: Standard output
        stderr: Standard error
    """
    sandbox_id: str
    exit_code: int
    stdout: str
    stderr: str
