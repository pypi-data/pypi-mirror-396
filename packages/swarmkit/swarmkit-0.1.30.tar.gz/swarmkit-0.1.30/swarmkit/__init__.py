"""SwarmKit Python SDK - Pythonic wrapper around the TypeScript SwarmKit SDK."""

from .agent import SwarmKit
from .config import (
    AgentConfig,
    E2BProvider,
    SandboxProvider,
    AgentType,
    WorkspaceMode,
    ReasoningEffort,
)
from .results import ExecuteResult
from .utils import read_local_dir
from .bridge import (
    SandboxNotFoundError,
    BridgeConnectionError,
    BridgeBuildError,
)

__version__ = '0.1.30'

__all__ = [
    # Main class
    'SwarmKit',

    # Configuration
    'AgentConfig',
    'E2BProvider',
    'SandboxProvider',
    'AgentType',
    'WorkspaceMode',
    'ReasoningEffort',

    # Results
    'ExecuteResult',

    # Utilities
    'read_local_dir',

    # Exceptions
    'SandboxNotFoundError',
    'BridgeConnectionError',
    'BridgeBuildError',
]
