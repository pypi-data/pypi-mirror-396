"""Integration tests for Plato SDK v2 Multi-Simulator Session API.

This test creates a session with multiple simulators (signoz, gitea, kanboard),
retrieves public URLs, waits for user interaction, and captures state mutations.

Run with: pytest tests/test_v2_multisim_integration.py -v -s
"""

import asyncio
import json
import os

import pytest
from dotenv import load_dotenv

from plato.v2 import AsyncPlato, Env

load_dotenv()


# Skip if no API key is available
pytestmark = pytest.mark.skipif(
    not os.environ.get("PLATO_API_KEY"),
    reason="PLATO_API_KEY environment variable not set",
)


@pytest.mark.asyncio
async def test_multisim_session_with_mutations():
    """Test creating a session with multiple simulators and capturing mutations.

    This test:
    1. Creates environments (signoz, gitea, kanboard)
    2. Gets public URLs for browser access
    3. Waits 5 minutes for user to perform actions
    4. Retrieves state mutations from all environments
    """
    plato = AsyncPlato()
    session = None

    try:
        print("\n" + "=" * 60, flush=True)
        print("MULTISIM INTEGRATION TEST", flush=True)
        print("=" * 60, flush=True)

        # 1. Create session with multiple simulators
        print("\n[1/3] Creating session with signoz, gitea, and kanboard...", flush=True)
        session = await plato.sessions.create(
            envs=[
                Env.simulator("signoz", alias="signoz"),
                Env.simulator("gitea", dataset="blank", alias="gitea"),
                Env.simulator("kanboard", alias="kanboard"),
            ],
            timeout=600,  # 10 minutes timeout for environment creation
        )

        print(f"Session created: {session.session_id}", flush=True)
        print(f"Environments: {len(session.envs)}", flush=True)
        for env in session.envs:
            print(f"  - {env.alias}: job_id={env.job_id}", flush=True)

        # Start heartbeat to keep session alive
        await session.start_heartbeat()

        # 2. Get public URLs
        print("\n[2/3] Getting public URLs...", flush=True)
        public_urls = await session.get_public_url()

        print("\nPublic URLs (open in browser):", flush=True)
        print("-" * 40, flush=True)
        for alias, url in public_urls.items():
            print(f"  {alias}: {url}", flush=True)
        print("-" * 40, flush=True)

        # 3. Get state/mutations (no wait)
        print("\n[3/3] Retrieving state mutations...", flush=True)
        state = await session.get_state()

        print("\nState Mutations by Environment:", flush=True)
        print("=" * 60, flush=True)

        if "results" in state:
            for job_id, result in state["results"].items():
                # Find alias for this job
                alias = next((env.alias for env in session.envs if env.job_id == job_id), job_id)
                print(f"\n{alias} ({job_id}):", flush=True)
                print("-" * 40, flush=True)

                if isinstance(result, dict) and "state" in result:
                    env_state = result["state"]
                    # Pretty print the state (limit depth for readability)
                    print(json.dumps(env_state, indent=2, default=str)[:2000], flush=True)
                    if len(json.dumps(env_state, default=str)) > 2000:
                        print("... (truncated)", flush=True)
                else:
                    print(f"  Raw result: {result}", flush=True)
        else:
            print(f"Raw state response: {json.dumps(state, indent=2, default=str)}", flush=True)

        print("\n" + "=" * 60, flush=True)
        print("TEST COMPLETED SUCCESSFULLY", flush=True)
        print("=" * 60, flush=True)

        # Assertions
        assert session.session_id is not None
        assert len(session.envs) == 3

        # Verify all environments exist
        aliases = {env.alias for env in session.envs}
        assert "signoz" in aliases
        assert "gitea" in aliases
        assert "kanboard" in aliases

    except Exception as e:
        print(f"\nERROR: {e}", flush=True)
        raise

    finally:
        # Cleanup
        if session:
            print("\nClosing session...", flush=True)
            await session.close()
        await plato.close()
        print("Cleanup complete.", flush=True)


@pytest.mark.asyncio
async def test_multisim_quick_state_check():
    """Quick test to verify state retrieval works without waiting.

    Creates environments, immediately gets state, and closes.
    Useful for verifying the API integration works.
    """
    plato = AsyncPlato()
    session = None

    try:
        print("\n[Quick Test] Creating session with signoz and gitea...")
        session = await plato.sessions.create(
            envs=[
                Env.simulator("signoz", alias="signoz"),
                Env.simulator("gitea", dataset="blank", alias="gitea"),
            ],
            timeout=600,
        )

        print(f"Session created: {session.session_id}")

        # Get initial state (should be empty/baseline)
        print("Getting initial state...")
        initial_state = await session.get_state()
        print(f"Initial state keys: {list(initial_state.get('results', {}).keys())}")

        # Get public URLs
        public_urls = await session.get_public_url()
        print(f"Public URLs retrieved: {len(public_urls)} URLs")

        # Reset environments
        print("Resetting environments...")
        reset_result = await session.reset()
        print(f"Reset result: {reset_result is not None}")

        # Get state after reset
        print("Getting state after reset...")
        post_reset_state = await session.get_state()
        print(f"Post-reset state keys: {list(post_reset_state.get('results', {}).keys())}")

        assert session.session_id is not None
        assert len(session.envs) == 2

        print("[Quick Test] PASSED")

    finally:
        if session:
            await session.close()
        await plato.close()


@pytest.mark.asyncio
async def test_individual_env_operations():
    """Test operations on individual environments within a session."""
    plato = AsyncPlato()
    session = None

    try:
        print("\n[Individual Env Test] Creating session...")
        session = await plato.sessions.create(
            envs=[
                Env.simulator("gitea", dataset="blank", alias="gitea"),
                Env.simulator("kanboard", alias="kanboard"),
            ],
            timeout=600,
        )

        await session.start_heartbeat()

        print(f"Session created: {session.session_id}")

        # Get individual environments
        gitea_env = session.get_env("gitea")
        kanboard_env = session.get_env("kanboard")

        assert gitea_env is not None, "Gitea environment not found"
        assert kanboard_env is not None, "Kanboard environment not found"

        # Execute command on gitea
        print(f"\nExecuting command on gitea (job_id={gitea_env.job_id})...")
        exec_result = await gitea_env.execute("whoami")
        print(f"Gitea whoami result: {exec_result}")

        # Execute command on kanboard
        print(f"\nExecuting command on kanboard (job_id={kanboard_env.job_id})...")
        exec_result = await kanboard_env.execute("ls -la /app")
        print(f"Kanboard ls result: {exec_result}")

        # Get state from individual env
        print("\nGetting state from gitea...")
        gitea_state = await gitea_env.get_state()
        print(
            f"Gitea state keys: {list(gitea_state.get('state', {}).keys()) if 'state' in gitea_state else gitea_state}"
        )

        print("[Individual Env Test] PASSED")

    finally:
        if session:
            await session.close()
        await plato.close()


if __name__ == "__main__":
    # Run the main test directly
    asyncio.run(test_multisim_session_with_mutations())
