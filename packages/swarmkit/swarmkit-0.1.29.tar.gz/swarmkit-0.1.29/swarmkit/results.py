"""Result types for SwarmKit SDK."""

from dataclasses import dataclass
from typing import Union


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


@dataclass
class OutputFile:
    """Output file metadata and content.

    Attributes:
        name: File name
        path: Full file path in sandbox
        content: File content (str for text, bytes for binary)
        size: File size in bytes
        modified_time: ISO timestamp of last modification
    """
    name: str
    path: str
    content: Union[str, bytes]
    size: int
    modified_time: str
