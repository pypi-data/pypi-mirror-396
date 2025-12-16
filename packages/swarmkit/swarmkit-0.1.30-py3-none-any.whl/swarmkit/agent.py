"""Main SwarmKit class for Python SDK."""

import asyncio
from typing import Any, Callable, Dict, List, Optional, Union

from .bridge import BridgeManager, SandboxNotFoundError
from .config import AgentConfig, SandboxProvider, WorkspaceMode
from .results import ExecuteResult
from .utils import _encode_files_for_transport


class SwarmKit:
    """SwarmKit agent orchestrator.

    Provides a Pythonic interface to the TypeScript SwarmKit SDK via JSON-RPC bridge.

    Example:
        >>> from swarmkit import SwarmKit, AgentConfig, E2BProvider
        >>>
        >>> swarmkit = SwarmKit(
        ...     config=AgentConfig(
        ...         type='codex',
        ...         api_key='sk-...',
        ...         model='gpt-5-codex'
        ...     ),
        ...     sandbox=E2BProvider(api_key='...')
        ... )
        >>>
        >>> async with swarmkit:
        ...     result = await swarmkit.run(prompt='Analyze data.csv')
        ...     files = await swarmkit.get_output_files()
    """

    def __init__(
        self,
        config: AgentConfig,
        sandbox: SandboxProvider,
        working_directory: str = '/home/user/workspace',
        workspace_mode: WorkspaceMode = 'knowledge',
        system_prompt: Optional[str] = None,
        context: Optional[Dict[str, Union[str, bytes]]] = None,
        files: Optional[Dict[str, Union[str, bytes]]] = None,
        mcp_servers: Optional[Dict[str, Any]] = None,
        secrets: Optional[Dict[str, str]] = None,
        sandbox_id: Optional[str] = None,
        session_tag_prefix: Optional[str] = None,
    ):
        """Initialize SwarmKit.

        Args:
            config: Agent configuration
            sandbox: Sandbox provider configuration
            working_directory: Working directory in sandbox (default: /home/user/workspace)
            workspace_mode: Workspace setup mode - 'knowledge' (creates output/context/scripts/temp folders + default prompt)
                          or 'swe' (clean workspace for cloned repos) (default: 'knowledge')
            system_prompt: Custom system prompt (appended to default in 'knowledge' mode, sole prompt in 'swe' mode)
            context: Files to upload to context/ folder on first run - { "filename.txt": "content" }
            files: Files to upload to working directory on first run - { "scripts/run.sh": "content" }
            mcp_servers: MCP server configurations
            secrets: Environment variables for sandbox
            sandbox_id: Existing sandbox ID to reconnect to
            session_tag_prefix: Optional semantic label for observability log files (e.g., 'experiment-7')
        """
        self.config = config
        self.sandbox = sandbox
        self.working_directory = working_directory
        self.workspace_mode = workspace_mode
        self.system_prompt = system_prompt
        self.context = context
        self.files = files
        self.mcp_servers = mcp_servers
        self.secrets = secrets
        self.sandbox_id = sandbox_id
        self.session_tag_prefix = session_tag_prefix

        self.bridge = BridgeManager()
        self._initialized = False
        self._init_lock = asyncio.Lock()

    async def _ensure_initialized(self):
        """Ensure bridge is started and agent is initialized."""
        async with self._init_lock:
            if self._initialized:
                return

            await self.bridge.start()

            # Encode context and files for JSON-RPC transport
            context_json = _encode_files_for_transport(self.context) if self.context else None
            files_json = _encode_files_for_transport(self.files) if self.files else None

            # Always forward all events - callbacks are called synchronously when events arrive.
            # If no callbacks are registered, events are simply not dispatched (harmless).
            # This allows registering callbacks at any time before or after run().
            await self.bridge.call('initialize', {
                'agent_type': self.config.type,
                'api_key': self.config.api_key,
                'model': self.config.model,
                'reasoning_effort': self.config.reasoning_effort,
                'betas': self.config.betas,
                'sandbox_provider': {
                    'type': self.sandbox.type,
                    'config': self.sandbox.config,
                },
                'working_directory': self.working_directory,
                'workspace_mode': self.workspace_mode,
                'system_prompt': self.system_prompt,
                'context': context_json,
                'files': files_json,
                'mcp_servers': self.mcp_servers,
                'secrets': self.secrets,
                'sandbox_id': self.sandbox_id,
                'forward_stdout': True,
                'forward_stderr': True,
                'forward_content': True,
                'session_tag_prefix': self.session_tag_prefix,
            })

            self._initialized = True

    def on(self, event_type: str, callback: Callable[[Any], None]):
        """Register event callback.

        Args:
            event_type: Event type ('stdout' | 'stderr' | 'content')
            callback: Callback function invoked with the event payload
                      (str for stdout/stderr, dict for content)

        Example:
            >>> swarmkit.on('stdout', lambda data: print(data, end=''))
            >>> swarmkit.on('stderr', lambda data: print(f'[ERR] {data}', end=''))
            >>> swarmkit.on('content', lambda event: print(event['update']['sessionUpdate']))
        """
        self.bridge.on(event_type, callback)

    def _get_rpc_timeout_s(self, timeout_ms: Optional[int]) -> float:
        """Compute an RPC timeout aligned with sandbox execution timeout."""
        if timeout_ms is None:
            timeout_ms = getattr(self.sandbox, "timeout_ms", 3600000) or 3600000
        # Add small grace to allow bridge/agent cleanup after sandbox timeout.
        return timeout_ms / 1000.0 + 30.0

    async def run(
        self,
        prompt: str,
        timeout_ms: Optional[int] = None,
        background: bool = False,
    ) -> ExecuteResult:
        """Run AI-assisted task (agent decides and acts).

        Args:
            prompt: Task description
            timeout_ms: Optional timeout in milliseconds (default: 1 hour)
            background: Run in background (default: False). If True, returns immediately
                       while agent continues running.

        Returns:
            ExecuteResult with sandbox_id, exit_code, stdout, stderr

        Example:
            >>> result = await swarmkit.run(prompt='Analyze data and create report', timeout_ms=600000)
            >>> # Background execution
            >>> result = await swarmkit.run(prompt='Long task', background=True)
        """
        await self._ensure_initialized()

        params: Dict[str, Any] = {
            'prompt': prompt,
        }
        if timeout_ms is not None:
            params['timeout_ms'] = timeout_ms
        if background:
            params['background'] = background

        response = await self.bridge.call(
            'run',
            params,
            timeout_s=self._get_rpc_timeout_s(timeout_ms),
        )

        return ExecuteResult(
            sandbox_id=response['sandbox_id'],
            exit_code=response['exit_code'],
            stdout=response['stdout'],
            stderr=response['stderr'],
        )

    async def execute_command(
        self,
        command: str,
        timeout_ms: Optional[int] = None,
        background: bool = False,
    ) -> ExecuteResult:
        """Execute direct shell command.

        Args:
            command: Shell command to execute
            timeout_ms: Optional timeout in milliseconds (default: 1 hour)
            background: Run in background (default: False)

        Returns:
            ExecuteResult with sandbox_id, exit_code, stdout, stderr

        Example:
            >>> result = await swarmkit.execute_command(command='python script.py')
        """
        await self._ensure_initialized()

        response = await self.bridge.call(
            'execute_command',
            {
                'command': command,
                'timeout_ms': timeout_ms,
                'background': background,
            },
            timeout_s=self._get_rpc_timeout_s(timeout_ms),
        )

        return ExecuteResult(
            sandbox_id=response['sandbox_id'],
            exit_code=response['exit_code'],
            stdout=response['stdout'],
            stderr=response['stderr'],
        )

    async def upload_context(
        self,
        files: Dict[str, Union[str, bytes]],
    ):
        """Upload files to context/ folder (runtime - immediate upload).

        Args:
            files: Dict mapping filename to content - { "filename.txt": "content", "data.json": jsonStr }

        Example:
            >>> await swarmkit.upload_context({
            ...     'spec.json': json.dumps(spec),
            ...     'readme.txt': 'Project documentation...',
            ... })
        """
        await self._ensure_initialized()
        await self.bridge.call('upload_context', {
            'files': _encode_files_for_transport(files),
        })

    async def upload_files(
        self,
        files: Dict[str, Union[str, bytes]],
    ):
        """Upload files to working directory (runtime - immediate upload).

        Args:
            files: Dict mapping path to content - { "scripts/run.sh": "#!/bin/bash...", "data/input.csv": csvData }

        Example:
            >>> await swarmkit.upload_files({
            ...     'scripts/setup.sh': '#!/bin/bash\\necho hello',
            ...     'temp/cache.json': json.dumps(cache),
            ... })
        """
        await self._ensure_initialized()
        await self.bridge.call('upload_files', {
            'files': _encode_files_for_transport(files),
        })

    async def get_output_files(self, recursive: bool = False) -> Dict[str, Union[str, bytes]]:
        """Get files from output/ directory.

        Returns files modified after the last run() call as a dict.
        Keys are relative paths from output/ (e.g., "result.json", "subdir/data.csv").

        Args:
            recursive: Include files in subdirectories (default: False)

        Returns:
            Dict mapping filename/path to content (str for text, bytes for binary)

        Example:
            >>> files = await swarmkit.get_output_files()
            >>> for name, content in files.items():
            ...     with open(f'./downloads/{name}', 'wb') as f:
            ...         f.write(content if isinstance(content, bytes) else content.encode())
        """
        await self._ensure_initialized()

        response = await self.bridge.call('get_output_files', {'recursive': recursive})

        files: Dict[str, Union[str, bytes]] = {}
        for name, file_data in response.items():
            content = file_data['content']
            encoding = file_data.get('encoding')
            if encoding == 'base64':
                content = base64.b64decode(content)
            files[name] = content

        return files

    async def get_session(self) -> Optional[str]:
        """Get sandbox ID for reuse.

        Returns:
            Sandbox ID or None if not initialized

        Example:
            >>> sandbox_id = await swarmkit.get_session()
            >>> print(f'Sandbox ID: {sandbox_id}')
        """
        await self._ensure_initialized()
        return await self.bridge.call('get_session')

    async def set_session(self, session_id: str):
        """Change sandbox session.

        Args:
            session_id: New sandbox ID to connect to

        Example:
            >>> await swarmkit.set_session('existing-sandbox-id')
        """
        await self._ensure_initialized()
        await self.bridge.call('set_session', {
            'session_id': session_id,
        })

    async def pause(self):
        """Pause sandbox to save costs while preserving state.

        Example:
            >>> await swarmkit.pause()
        """
        await self._ensure_initialized()
        await self.bridge.call('pause')

    async def resume(self):
        """Resume paused sandbox.

        Example:
            >>> await swarmkit.resume()
        """
        await self._ensure_initialized()
        await self.bridge.call('resume')

    async def kill(self):
        """Terminate sandbox and release all resources.

        Example:
            >>> await swarmkit.kill()
        """
        await self._ensure_initialized()
        try:
            await self.bridge.call('kill')
        finally:
            # Always stop bridge even if RPC fails (e.g., sandbox already gone)
            await self.bridge.stop()
            self._initialized = False

    async def get_host(self, port: int) -> str:
        """Get public URL for sandbox port.

        Args:
            port: Port number to expose

        Returns:
            Public URL for the port

        Example:
            >>> url = await swarmkit.get_host(8000)
            >>> print(f'Server available at: {url}')
        """
        await self._ensure_initialized()
        response = await self.bridge.call('get_host', {
            'port': port,
        })
        return response['url']

    async def get_session_tag(self) -> Optional[str]:
        """Get the observability session tag.

        Returns the generated tag (e.g., 'my-prefix-a3f8b2c1') used for the
        log file in ~/.swarmkit/observability/sessions/

        Returns:
            Session tag or None if not initialized

        Example:
            >>> tag = await swarmkit.get_session_tag()
            >>> print(f'Log file tag: {tag}')
            'experiment-7-a3f8b2c1'
        """
        await self._ensure_initialized()
        return await self.bridge.call('get_session_tag')

    async def get_session_timestamp(self) -> Optional[str]:
        """Get the session start timestamp (ISO format).

        Returns:
            ISO timestamp when session was created or None if not initialized

        Example:
            >>> timestamp = await swarmkit.get_session_timestamp()
            >>> print(f'Session started: {timestamp}')
            '2025-01-15T10:30:45.123Z'
        """
        await self._ensure_initialized()
        return await self.bridge.call('get_session_timestamp')

    async def __aenter__(self):
        """Context manager entry."""
        try:
            await self._ensure_initialized()
            return self
        except Exception:
            # Cleanup bridge process if initialization fails
            await self.bridge.stop()
            raise

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup resources."""
        try:
            await self.kill()
        except Exception as e:
            import warnings
            warnings.warn(f"Error during cleanup: {e}", RuntimeWarning)
