"""File utilities for SwarmKit SDK."""

import base64
from pathlib import Path
from typing import Dict, Union


def _encode_files_for_transport(
    files: Dict[str, Union[str, bytes]]
) -> Dict[str, Dict[str, str]]:
    """Encode files dict for JSON-RPC transport.

    Handles both text (str) and binary (bytes) content with appropriate encoding.
    """
    result = {}
    for name, content in files.items():
        if isinstance(content, bytes):
            result[name] = {
                'data': base64.b64encode(content).decode('utf-8'),
                'encoding': 'base64'
            }
        else:
            result[name] = {'data': content, 'encoding': 'text'}
    return result


def read_local_dir(local_path: str, recursive: bool = False) -> Dict[str, bytes]:
    """Read files from a local directory into a dict for upload.

    Args:
        local_path: Path to local directory
        recursive: Include subdirectories (default: False)

    Returns:
        Dict mapping relative paths to file content as bytes
    """
    result: Dict[str, bytes] = {}
    root = Path(local_path)

    paths = root.rglob('*') if recursive else root.iterdir()

    for p in paths:
        if p.is_file():
            result[str(p.relative_to(root))] = p.read_bytes()

    return result
