"""
Common fixtures for codemie CLI tests.

Provides shared fixtures for configuration and setup.
"""

import json
import subprocess
from pathlib import Path

import pytest

from codemie_test_harness.tests import CredentialsManager
from codemie_test_harness.tests.enums.model_types import ModelTypes
from codemie_test_harness.tests.utils.logger_util import setup_logger

logger = setup_logger(__name__)


@pytest.fixture(scope="session")
def codemie_config_dir():
    """Get the .codemie config directory path using OS utilities."""
    home_dir = Path.home()
    config_dir = home_dir / ".codemie"
    return config_dir


@pytest.fixture(scope="session")
def config_file_path(codemie_config_dir):
    """Get the config.json file path."""
    return codemie_config_dir / "config.json"


@pytest.fixture(scope="session", params=["litellm", "sso"])
def provider(request):
    """Parametrize tests to run with both LiteLLM and SSO providers."""
    return request.param


@pytest.fixture(scope="session")
def config_data(provider):
    """Get the configuration data for codemie CLI based on provider."""
    base_config = {
        "version": 2,
        "activeProfile": "default",
        "profiles": {},
        "analytics": {
            "enabled": True,
            "target": "local",
            "localPath": "~/.codemie/analytics",
            "flushInterval": 5000,
            "maxBufferSize": 100,
        },
    }

    if provider == "litellm":
        base_config["profiles"]["default"] = {
            "name": "default",
            "provider": "litellm",
            "baseUrl": CredentialsManager.get_parameter("LITE_LLM_URL"),
            "apiKey": CredentialsManager.get_parameter("LITE_LLM_API_KEY"),
            "model": ModelTypes.CLAUDE_4_5_SONNET.value,
            "timeout": 300,
            "debug": False,
        }
    elif provider == "sso":
        base_config["profiles"]["default"] = {
            "name": "default",
            "provider": "ai-run-sso",
            "authMethod": "sso",
            "codeMieUrl": CredentialsManager.get_parameter("FRONTEND_URL"),
            "baseUrl": CredentialsManager.get_parameter("CODEMIE_API_DOMAIN"),
            "apiKey": "sso-authenticated",
            "model": ModelTypes.CLAUDE_4_5_SONNET.value,
            "timeout": 300,
            "debug": False,
        }

    return base_config


@pytest.fixture(scope="session")
def setup_codemie_base(codemie_config_dir, config_file_path, config_data, provider):
    """
    Set up base codemie CLI infrastructure.

    This fixture:
    1. Installs @codemieai/code npm package globally
    2. Creates .codemie directory
    3. Creates config.json file
    4. For SSO provider, authenticates using codemie auth login

    Note: Config file is not cleaned up to allow reuse across test runs.
    When extending tests for other LLMs, consider using unique profile names
    to avoid conflicts during parallel test execution.
    """
    # Step 1: Install @codemieai/code npm package globally
    logger.info(f"Installing @codemieai/code npm package for {provider} provider...")
    install_result = subprocess.run(
        ["npm", "install", "-g", "@codemieai/code"],
        capture_output=True,
        text=True,
        timeout=120,
    )

    if install_result.returncode != 0:
        pytest.fail(f"Failed to install @codemieai/code: {install_result.stderr}")

    logger.info(f"npm install output: {install_result.stdout}")

    # Step 2: Create .codemie directory if it doesn't exist
    logger.info(f"Creating config directory: {codemie_config_dir}")
    codemie_config_dir.mkdir(parents=True, exist_ok=True)

    # Step 3: Create config.json file
    logger.info(f"Creating config file for {provider}: {config_file_path}")
    with open(config_file_path, "w") as f:
        json.dump(config_data, f, indent=2)

    # Step 4: For SSO provider, run authentication
    if provider == "sso":
        logger.info(f"Authenticating with SSO for {provider} provider...")
        sso_url = CredentialsManager.get_parameter("FRONTEND_URL")
        auth_result = subprocess.run(
            ["codemie", "auth", "login", "--url", sso_url],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if auth_result.returncode != 0:
            logger.warning(
                f"SSO authentication returned non-zero: {auth_result.stderr}"
            )
        else:
            logger.info(f"SSO authentication successful: {auth_result.stdout}")

    logger.info(f"Base codemie CLI setup completed for {provider} provider")
