"""Plato SDK v2 - Synchronous Session Actor.

The Session class wraps a SessionSpec (from backend) with execution capabilities.
It acts like a Ray actor - the spec holds state, the class provides methods.
"""

from __future__ import annotations

import logging
import threading
import uuid

import httpx
import tenacity

from plato._generated.api.v2.sessions import close as sessions_close
from plato._generated.api.v2.sessions import evaluate as sessions_evaluate
from plato._generated.api.v2.sessions import execute as sessions_execute
from plato._generated.api.v2.sessions import heartbeat as sessions_heartbeat
from plato._generated.api.v2.sessions import make as sessions_make
from plato._generated.api.v2.sessions import reset as sessions_reset
from plato._generated.api.v2.sessions import snapshot as sessions_snapshot
from plato._generated.api.v2.sessions import state as sessions_state
from plato._generated.api.v2.sessions import wait_for_ready as sessions_wait_for_ready
from plato._generated.models import (
    AppApiV2SchemasSessionCreateSnapshotResponse,
    AppApiV2SchemasSessionEvaluateResponse,
    AppApiV2SchemasSessionHeartbeatResponse,
    CreateSessionFromEnvs,
    CreateSessionFromTask,
    Envs,
    ExecuteCommandRequest,
    ExecuteCommandResponse,
    ResetSessionRequest,
    ResetSessionResponse,
    RunSessionSource,
    SessionContext,
    SessionStateResponse,
    WaitForReadyResponse,
)
from plato.v2.sync.environment import Environment
from plato.v2.types import EnvFromArtifact, EnvFromResource, EnvFromSimulator

logger = logging.getLogger(__name__)


class Session:
    """Actor wrapper for SessionSpec - provides execution methods.

    The Session wraps a SessionSpec (which contains the runtime state) and adds
    methods to execute operations on the session. This is similar to a Ray actor
    pattern where the spec is the state and the class provides the interface.

    Usage:
        from plato.v2 import Plato, Env

        plato = Plato()
        session = plato.from_envs(envs=[Env.simulator("espocrm")])

        # Operations execute against the backend
        session.reset()
        state = session.get_state()
        result = session.execute("ls -la")

        session.close()
        plato.close()
    """

    def __init__(
        self,
        http_client: httpx.Client,
        api_key: str,
        context: SessionContext,
    ):
        """Initialize session actor.

        Args:
            http_client: HTTP client for API calls.
            api_key: API key for authentication.
            context: SessionContext from backend with session_id, envs, and task_public_id.
        """

        self._http = http_client
        self._api_key = api_key
        self._context = context
        self._closed = False
        self._heartbeat_thread: threading.Thread | None = None
        self._heartbeat_stop = threading.Event()
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
    def from_envs(
        cls,
        http_client: httpx.Client,
        api_key: str,
        envs: list[EnvFromSimulator | EnvFromArtifact | EnvFromResource],
        *,
        timeout: int = 1800,
    ) -> Session:
        """Create a new session from environment configurations.

        Waits for all environments to be ready (RUNNING status) before returning.

        Args:
            http_client: The httpx client for making requests.
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
        request_body = CreateSessionFromEnvs(
            envs=[Envs(root=env) for env in envs],
            timeout=timeout,
            source=RunSessionSource.SDK,
        )

        # Use generated API function
        response = sessions_make.sync(
            client=http_client,
            body=request_body,
            x_api_key=api_key,
        )

        # Check for any failures
        failures = [e for e in response.envs if not e.success]
        if failures:
            # Close the session immediately
            try:
                sessions_close.sync(
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
            ready_response = sessions_wait_for_ready.sync(
                client=http_client,
                session_id=response.session_id,
                timeout=int(timeout),
                x_api_key=api_key,
            )
            context = cls._check_ready_response(ready_response, timeout)
        except (TimeoutError, RuntimeError):
            # Close session on failure
            try:
                sessions_close.sync(
                    client=http_client,
                    session_id=response.session_id,
                    x_api_key=api_key,
                )
            except Exception as close_err:
                logger.warning(f"Failed to close session after ready timeout: {close_err}")
            raise

        logger.info(f"All environments in session {response.session_id} are ready")
        session = cls(
            http_client=http_client,
            api_key=api_key,
            context=context,
        )
        session.start_heartbeat()
        return session

    @classmethod
    def from_task(
        cls,
        http_client: httpx.Client,
        api_key: str,
        task_id: str,
        *,
        timeout: int = 1800,
    ) -> Session:
        """Create a new session from a task public ID.

        Waits for all environments to be ready (RUNNING status) before returning.

        Args:
            http_client: The httpx client for making requests.
            api_key: API key for authentication.
            task_id: Task public ID to create session from.
            timeout: VM timeout in seconds (default: 1800).

        Returns:
            A new Session instance with all environments ready.

        Raises:
            RuntimeError: If any environment fails to create or become ready.
            TimeoutError: If environments don't become ready within timeout.
        """
        # Build request using generated model
        request_body = CreateSessionFromTask(
            task_id=task_id,
            timeout=timeout,
            source=RunSessionSource.SDK,
        )

        # Use generated API function
        response = sessions_make.sync(
            client=http_client,
            body=request_body,
            x_api_key=api_key,
        )

        # Check for any failures
        failures = [e for e in response.envs if not e.success]
        if failures:
            # Close the session immediately
            try:
                sessions_close.sync(
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
            ready_response = sessions_wait_for_ready.sync(
                client=http_client,
                session_id=response.session_id,
                timeout=int(timeout),
                x_api_key=api_key,
            )
            context = cls._check_ready_response(ready_response, timeout)
        except (TimeoutError, RuntimeError):
            # Close session on failure
            try:
                sessions_close.sync(
                    client=http_client,
                    session_id=response.session_id,
                    x_api_key=api_key,
                )
            except Exception as close_err:
                logger.warning(f"Failed to close session after ready timeout: {close_err}")
            raise

        logger.info(f"All environments in session {response.session_id} are ready")
        session = cls(
            http_client=http_client,
            api_key=api_key,
            context=context,
        )
        session.start_heartbeat()
        return session

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

    def wait_until_ready(
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
            RuntimeError: If any environment fails.
        """
        self._check_closed()

        class NotReadyError(Exception):
            pass

        @tenacity.retry(
            stop=tenacity.stop_after_delay(timeout),
            wait=tenacity.wait_fixed(poll_interval),
            retry=tenacity.retry_if_exception_type(NotReadyError),
            reraise=True,
        )
        def _poll_ready():
            response = sessions_wait_for_ready.sync(
                client=self._http,
                session_id=self.session_id,
                timeout=int(poll_interval * 2),
                x_api_key=self._api_key,
            )

            # Check for fatal errors
            if response.results:
                for job_id, result in response.results.items():
                    if result.error and "failed" in result.error.lower():
                        raise RuntimeError(f"Environment {job_id} failed: {result.error}")

            if response.ready and response.context:
                self._context = response.context
                self._envs = None  # Reset cached envs
                logger.info(f"All environments in session {self.session_id} are ready")
                return

            raise NotReadyError("Environments not ready yet")

        try:
            _poll_ready()
        except NotReadyError:
            raise TimeoutError(f"Environments did not become ready within {timeout} seconds")

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

    def reset(self, **kwargs) -> ResetSessionResponse:
        """Reset all environments in the session to initial state.

        Returns:
            ResetSessionResponse with results per job_id.
        """
        self._check_closed()

        request = ResetSessionRequest(**kwargs)
        return sessions_reset.sync(
            client=self._http,
            session_id=self.session_id,
            body=request,
            x_api_key=self._api_key,
        )

    def get_state(self) -> SessionStateResponse:
        """Get state from all environments in the session.

        Returns:
            SessionStateResponse with state per job_id.
        """
        self._check_closed()

        return sessions_state.sync(
            client=self._http,
            session_id=self.session_id,
            x_api_key=self._api_key,
        )

    def execute(
        self,
        command: str,
        timeout: int = 30,
    ) -> ExecuteCommandResponse:
        """Execute a command on all environments in the session.

        Args:
            command: Shell command to execute.
            timeout: Command timeout in seconds.

        Returns:
            ExecuteCommandResponse with execution results per job_id.
        """
        self._check_closed()

        request = ExecuteCommandRequest(
            command=command,
            timeout=timeout,
        )
        return sessions_execute.sync(
            client=self._http,
            session_id=self.session_id,
            body=request,
            x_api_key=self._api_key,
        )

    def evaluate(self, **kwargs) -> AppApiV2SchemasSessionEvaluateResponse:
        """Evaluate the session against task criteria.

        Returns:
            Evaluation results.
        """
        self._check_closed()

        return sessions_evaluate.sync(
            client=self._http,
            session_id=self.session_id,
            x_api_key=self._api_key,
            **kwargs,
        )

    def snapshot(self) -> AppApiV2SchemasSessionCreateSnapshotResponse:
        """Create a snapshot of all environments in the session.

        Returns:
            Snapshot response with info per job_id.
        """
        self._check_closed()

        return sessions_snapshot.sync(
            client=self._http,
            session_id=self.session_id,
            x_api_key=self._api_key,
        )

    def heartbeat(self) -> AppApiV2SchemasSessionHeartbeatResponse:
        """Send heartbeat to keep all environments alive.

        Returns:
            Heartbeat response with results per job_id.
        """
        self._check_closed()

        return sessions_heartbeat.sync(
            client=self._http,
            session_id=self.session_id,
            x_api_key=self._api_key,
        )

    # Heartbeat management

    def _heartbeat_loop(self) -> None:
        """Background thread that periodically sends heartbeats."""
        while not self._heartbeat_stop.wait(self._heartbeat_interval):
            try:
                self.heartbeat()
                logger.debug(f"Heartbeat sent for session {self.session_id}")
            except Exception as e:
                logger.error(f"Heartbeat error for session {self.session_id}: {e}")

    def start_heartbeat(self) -> None:
        """Start the heartbeat background thread."""
        self.stop_heartbeat()
        self._heartbeat_stop.clear()
        self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()

    def stop_heartbeat(self) -> None:
        """Stop the heartbeat background thread."""
        if self._heartbeat_thread and self._heartbeat_thread.is_alive():
            self._heartbeat_stop.set()
            self._heartbeat_thread.join(timeout=2)
            self._heartbeat_thread = None

    # Lifecycle

    def close(self) -> None:
        """Close the session and all its environments."""
        if self._closed:
            return

        self.stop_heartbeat()

        sessions_close.sync(
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
