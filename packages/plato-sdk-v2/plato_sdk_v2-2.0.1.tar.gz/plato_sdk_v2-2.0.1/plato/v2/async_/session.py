"""Plato SDK v2 - Asynchronous Session Actor.

The Session class wraps a SessionSpec (from backend) with execution capabilities.
It acts like a Ray actor - the spec holds state, the class provides methods.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Any

import httpx

from plato._generated.api.v2.sessions import close as sessions_close
from plato._generated.api.v2.sessions import evaluate as sessions_evaluate
from plato._generated.api.v2.sessions import execute as sessions_execute
from plato._generated.api.v2.sessions import get_public_url as sessions_get_public_url
from plato._generated.api.v2.sessions import heartbeat as sessions_heartbeat
from plato._generated.api.v2.sessions import make as sessions_make
from plato._generated.api.v2.sessions import reset as sessions_reset
from plato._generated.api.v2.sessions import snapshot as sessions_snapshot
from plato._generated.api.v2.sessions import state as sessions_state
from plato._generated.api.v2.sessions import wait_for_ready as sessions_wait_for_ready
from plato._generated.models import (
    CreateSessionRequest,
    ExecuteCommandRequest,
    ResetSessionRequest,
    SessionContext,
    WaitForReadyResponse,
)
from plato.v2.async_.environment import Environment
from plato.v2.types import EnvFromArtifact, EnvFromResource, EnvFromSimulator
from plato.v2.utils.db_cleanup import DatabaseCleaner
from plato.v2.utils.models import (
    EnvironmentInfo,
    SessionCleanupResult,
)

logger = logging.getLogger(__name__)


class Session:
    """Actor wrapper for SessionSpec - provides async execution methods.

    The Session wraps a SessionSpec (which contains the runtime state) and adds
    methods to execute operations on the session. This is similar to a Ray actor
    pattern where the spec is the state and the class provides the interface.

    Usage:
        from plato.v2 import AsyncPlato, Env

        plato = AsyncPlato()
        session = await plato.from_envs(envs=[Env.simulator("espocrm")])

        # Operations execute against the backend
        await session.reset()
        state = await session.get_state()
        result = await session.execute("ls -la")

        await session.close()
        await plato.close()
    """

    def __init__(
        self,
        http_client: httpx.AsyncClient,
        api_key: str,
        context: SessionContext,
    ):
        """Initialize session actor.

        Args:
            http_client: Async HTTP client for API calls.
            api_key: API key for authentication.
            context: SessionContext from backend with session_id, envs, and task_public_id.
        """

        self._http = http_client
        self._api_key = api_key
        self._context = context
        self._closed = False
        self._heartbeat_task: asyncio.Task | None = None
        self._heartbeat_interval = 30
        self._envs: list[Environment] | None = None

    @property
    def session_id(self) -> str:
        """Get the session ID."""
        return self._context.session_id

    @property
    def task_public_id(self) -> str | None:
        """Get the task public ID if session was created from a task."""
        return self._context.task_public_id

    @classmethod
    async def from_envs(
        cls,
        http_client: httpx.AsyncClient,
        api_key: str,
        envs: list[EnvFromSimulator | EnvFromArtifact | EnvFromResource],
        *,
        timeout: int = 1800,
    ) -> Session:
        """Create a new session from environment configurations.

        Waits for all environments to be ready (RUNNING status) before returning.

        Args:
            http_client: The httpx async client.
            api_key: API key for authentication.
            envs: List of environment configurations (from Env.simulator() or Env.artifact()).
            timeout: VM timeout in seconds (default: 1800).

        Returns:
            A new Session instance with all environments ready.

        Raises:
            RuntimeError: If any environment fails to create or become ready.
            TimeoutError: If environments don't become ready within timeout.
            ValueError: If duplicate aliases are provided.
        """
        # Normalize aliases - auto-generate unique ones if not set, validate no duplicates
        seen_aliases: set[str] = set()
        for env in envs:
            if env.alias is not None:
                if env.alias in seen_aliases:
                    raise ValueError(f"Duplicate alias provided: '{env.alias}'")
                seen_aliases.add(env.alias)

        for env in envs:
            if env.alias is None:
                unique_alias = f"env-{uuid.uuid4().hex[:8]}"
                while unique_alias in seen_aliases:
                    unique_alias = f"env-{uuid.uuid4().hex[:8]}"
                env.alias = unique_alias
                seen_aliases.add(unique_alias)

        # Build request using generated model
        request_body = CreateSessionRequest(
            envs=envs,
            task_id=None,
            timeout=timeout,
            source="SDK",
        )

        # Use generated API function
        response = await sessions_make.asyncio(
            client=http_client,
            body=request_body,
            x_api_key=api_key,
        )

        # Check for any failures
        failures = [e for e in response.envs if not e.success]
        if failures:
            # Close the session immediately
            try:
                await sessions_close.asyncio(
                    client=http_client,
                    session_id=response.session_id,
                    x_api_key=api_key,
                )
            except Exception as close_err:
                logger.warning(f"Failed to close session after env creation failure: {close_err}")

            # Raise error with details
            failure_details = ", ".join([f"{e.alias}: {e.error}" for e in failures])
            raise RuntimeError(f"Failed to create environments: {failure_details}")

        logger.info(f"Session created: {response.session_id}, envs: {[e.alias for e in response.envs]}")

        # Wait for environments to be ready and get context
        try:
            ready_response = await sessions_wait_for_ready.asyncio(
                client=http_client,
                session_id=response.session_id,
                timeout=int(timeout),
                x_api_key=api_key,
            )
            logger.info(f"wait_for_ready returned ready={ready_response.ready}")
            context = cls._check_ready_response(ready_response, timeout)
        except (TimeoutError, RuntimeError):
            # Close session on failure
            try:
                await sessions_close.asyncio(
                    client=http_client,
                    session_id=response.session_id,
                    x_api_key=api_key,
                )
            except Exception as close_err:
                logger.warning(f"Failed to close session after ready timeout: {close_err}")
            raise

        logger.info(f"All environments in session {response.session_id} are ready")
        return cls(
            http_client=http_client,
            api_key=api_key,
            context=context,
        )

    @classmethod
    async def from_task(
        cls,
        http_client: httpx.AsyncClient,
        api_key: str,
        task_id: int,
        *,
        timeout: int = 1800,
    ) -> Session:
        """Create a new session from a task ID.

        Waits for all environments to be ready (RUNNING status) before returning.

        Args:
            http_client: The httpx async client.
            api_key: API key for authentication.
            task_id: Test case ID to create session from.
            timeout: VM timeout in seconds (default: 1800).

        Returns:
            A new Session instance with all environments ready.

        Raises:
            RuntimeError: If any environment fails to create or become ready.
            TimeoutError: If environments don't become ready within timeout.
        """
        # Build request using generated model
        request_body = CreateSessionRequest(
            envs=None,
            task_id=task_id,
            timeout=timeout,
            source="sdk",
        )

        # Use generated API function
        response = await sessions_make.asyncio(
            client=http_client,
            body=request_body,
            x_api_key=api_key,
        )

        # Check for any failures
        failures = [e for e in response.envs if not e.success]
        if failures:
            # Close the session immediately
            try:
                await sessions_close.asyncio(
                    client=http_client,
                    session_id=response.session_id,
                    x_api_key=api_key,
                )
            except Exception as close_err:
                logger.warning(f"Failed to close session after env creation failure: {close_err}")

            # Raise error with details
            failure_details = ", ".join([f"{e.alias}: {e.error}" for e in failures])
            raise RuntimeError(f"Failed to create environments: {failure_details}")

        # Wait for environments to be ready and get context
        try:
            ready_response = await sessions_wait_for_ready.asyncio(
                client=http_client,
                session_id=response.session_id,
                timeout=int(timeout),
                x_api_key=api_key,
            )
            context = cls._check_ready_response(ready_response, timeout)
        except (TimeoutError, RuntimeError):
            # Close session on failure
            try:
                await sessions_close.asyncio(
                    client=http_client,
                    session_id=response.session_id,
                    x_api_key=api_key,
                )
            except Exception as close_err:
                logger.warning(f"Failed to close session after ready timeout: {close_err}")
            raise

        logger.info(f"All environments in session {response.session_id} are ready")
        return cls(
            http_client=http_client,
            api_key=api_key,
            context=context,
        )

    @staticmethod
    def _check_ready_response(response: WaitForReadyResponse, timeout: float) -> SessionContext:
        """Check the wait_for_ready response and return the SessionContext.

        Args:
            response: WaitForReadyResponse from the API.
            timeout: Timeout value for error messages.

        Returns:
            SessionContext with environment details.

        Raises:
            TimeoutError: If environments didn't become ready.
            RuntimeError: If any environment failed or context is missing.
        """
        if not response.ready:
            errors = []
            if response.results:
                for job_id, result in response.results.items():
                    if not result.ready:
                        error = result.error or "Unknown error"
                        errors.append(f"{job_id}: {error}")

            if errors:
                raise RuntimeError(f"Environments failed to become ready: {', '.join(errors)}")
            else:
                raise TimeoutError(f"Environments did not become ready within {timeout} seconds")

        if not response.context:
            raise RuntimeError("Backend did not return session context")

        return response.context

    async def wait_until_ready(
        self,
        timeout: float = 300.0,
        poll_interval: float = 2.0,
    ) -> None:
        """Wait until all environments are ready (RUNNING status).

        Polls the backend wait_for_ready API until all environments are ready.

        Args:
            timeout: Maximum time to wait in seconds (default: 300).
            poll_interval: Time between polls in seconds (default: 2.0).

        Raises:
            TimeoutError: If environments don't become ready within timeout.
            RuntimeError: If any environment fails or is cancelled.
        """
        import time

        self._check_closed()

        start_time = time.time()
        while True:
            elapsed = time.time() - start_time
            remaining = timeout - elapsed
            if remaining <= 0:
                raise TimeoutError(f"Environments did not become ready within {timeout} seconds")

            response = await sessions_wait_for_ready.asyncio(
                client=self._http,
                session_id=self.session_id,
                timeout=int(min(poll_interval * 2, remaining)),
                x_api_key=self._api_key,
            )

            if response.ready and response.context:
                self._context = response.context
                self._envs = None  # Reset cached envs
                logger.info(f"All environments in session {self.session_id} are ready")
                return

            # Check for fatal errors
            if response.results:
                for job_id, result in response.results.items():
                    if result.error and "failed" in result.error.lower():
                        raise RuntimeError(f"Environment {job_id} failed: {result.error}")

            await asyncio.sleep(poll_interval)

    @property
    def envs(self) -> list[Environment]:
        """Get all environments in this session.

        Returns:
            List of Environment actor objects.
        """
        if self._envs is None:
            env_contexts = self._context.envs or []
            self._envs = [
                Environment(
                    session=self,
                    job_id=ctx.job_id,
                    alias=ctx.alias,
                    artifact_id=ctx.artifact_id,
                )
                for ctx in env_contexts
            ]
        return self._envs

    def get_env(self, alias: str) -> Environment | None:
        """Get an environment by alias.

        Args:
            alias: The environment alias.

        Returns:
            The Environment actor or None if not found.
        """
        for env in self.envs:
            if env.alias == alias:
                return env
        return None

    async def reset(self, **kwargs) -> dict[str, Any]:
        """Reset all environments in the session to initial state.

        Returns:
            Dict with results per job_id.
        """
        self._check_closed()

        request = ResetSessionRequest(**kwargs)
        response = await sessions_reset.asyncio(
            client=self._http,
            session_id=self.session_id,
            body=request,
            x_api_key=self._api_key,
        )

        return response.to_dict() if response else {}

    async def get_state(self) -> dict[str, Any]:
        """Get state from all environments in the session.

        Returns:
            Dict with state per job_id.
        """
        self._check_closed()

        response = await sessions_state.asyncio(
            client=self._http,
            session_id=self.session_id,
            x_api_key=self._api_key,
        )

        return response.to_dict() if response else {}

    async def execute(
        self,
        command: str,
        timeout: int = 30,
    ) -> dict[str, Any]:
        """Execute a command on all environments in the session.

        Args:
            command: Shell command to execute.
            timeout: Command timeout in seconds.

        Returns:
            Dict with execution results per job_id.
        """
        self._check_closed()

        request = ExecuteCommandRequest(
            command=command,
            timeout=timeout,
        )
        response = await sessions_execute.asyncio(
            client=self._http,
            session_id=self.session_id,
            body=request,
            x_api_key=self._api_key,
        )

        return response.to_dict() if response else {}

    async def evaluate(self, **kwargs) -> dict[str, Any]:
        """Evaluate the session against task criteria.

        Returns:
            Evaluation results.
        """
        self._check_closed()

        response = await sessions_evaluate.asyncio(
            client=self._http,
            session_id=self.session_id,
            x_api_key=self._api_key,
            **kwargs,
        )

        return response.to_dict() if response else {}

    async def snapshot(self) -> dict[str, Any]:
        """Create a snapshot of all environments in the session.

        Returns:
            Dict with snapshot info per job_id.
        """
        self._check_closed()

        response = await sessions_snapshot.asyncio(
            client=self._http,
            session_id=self.session_id,
            x_api_key=self._api_key,
        )

        return response.to_dict() if response else {}

    async def get_public_url(self, port: int | None = None) -> dict[str, str]:
        """Get public URLs for all environments in the session.

        Returns browser-accessible URLs in format: {job_id}--{port}.sims.plato.so

        Args:
            port: Port number for the URLs. If not specified, uses the default port.

        Returns:
            Dict mapping alias to public URL.
        """
        self._check_closed()

        response = await sessions_get_public_url.asyncio(
            client=self._http,
            session_id=self.session_id,
            port=port,
            x_api_key=self._api_key,
        )

        # Map job_id to alias for easier access
        urls = {}
        if response and response.results:
            for job_id, result in response.results.items():
                alias = next((env.alias for env in self.envs if env.job_id == job_id), job_id)
                url = result.url if hasattr(result, "url") else str(result)
                urls[alias] = url

        return urls

    async def cleanup_databases(self) -> SessionCleanupResult:
        """Clean up database audit logs for all environments.

        For each environment:
        1. Gets DB config from the environment's artifact
        2. Connects to each database via proxy tunnel
        3. Finds and truncates audit_log tables
        4. Calls get_state to clear in-memory mutation cache

        This should be called before snapshot() to ensure clean state.
        Environments and databases are cleaned up in parallel for efficiency.

        Returns:
            SessionCleanupResult with results for each environment.
        """
        self._check_closed()

        # Build EnvironmentInfo objects
        env_infos = [
            EnvironmentInfo(
                job_id=env.job_id,
                alias=env.alias,
                artifact_id=env.artifact_id,
                get_state_fn=env.get_state,
            )
            for env in self.envs
        ]

        cleaner = DatabaseCleaner()
        return await cleaner.cleanup_session(
            envs=env_infos,
            http_client=self._http,
            api_key=self._api_key,
        )

    async def heartbeat(self) -> dict[str, Any]:
        """Send heartbeat to keep all environments alive.

        Returns:
            Dict with heartbeat results per job_id.
        """
        self._check_closed()

        response = await sessions_heartbeat.asyncio(
            client=self._http,
            session_id=self.session_id,
            x_api_key=self._api_key,
        )

        return response.to_dict() if response else {}

    # Heartbeat management

    async def _heartbeat_loop(self) -> None:
        """Background task that periodically sends heartbeats."""
        try:
            while True:
                try:
                    await self.heartbeat()
                    logger.debug(f"Heartbeat sent for session {self.session_id}")
                except Exception as e:
                    logger.error(f"Heartbeat error for session {self.session_id}: {e}")
                await asyncio.sleep(self._heartbeat_interval)
        except asyncio.CancelledError:
            pass

    async def start_heartbeat(self) -> None:
        """Start the heartbeat background task."""
        await self.stop_heartbeat()
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    async def stop_heartbeat(self) -> None:
        """Stop the heartbeat background task."""
        if self._heartbeat_task and not self._heartbeat_task.done():
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
            self._heartbeat_task = None

    # Lifecycle

    async def close(self) -> None:
        """Close the session and all its environments."""
        if self._closed:
            return

        await self.stop_heartbeat()

        await sessions_close.asyncio(
            client=self._http,
            session_id=self.session_id,
            x_api_key=self._api_key,
        )

        self._closed = True

    def _check_closed(self) -> None:
        if self._closed:
            raise RuntimeError("Session is closed")

    def __repr__(self) -> str:
        env_count = len(self._context.envs) if self._context.envs else 0
        return f"Session(session_id={self.session_id!r}, envs={env_count})"
