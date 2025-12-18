"""
Tests for codemie doctor command.

This test suite verifies:
1. codemie doctor command execution
2. Health check validation
3. Output contains expected information
"""

import subprocess

import pytest
from hamcrest import assert_that, equal_to, contains_string, matches_regexp

from codemie_test_harness.tests.utils.env_resolver import EnvironmentResolver
from codemie_test_harness.tests.utils.logger_util import setup_logger

logger = setup_logger(__name__)


@pytest.mark.proxy
@pytest.mark.api
@pytest.mark.not_for_parallel_run
@pytest.mark.skipif(
    EnvironmentResolver.is_sandbox(),
    reason="LiteLLM is not configured for sandbox environments",
)
def test_codemie_doctor_execution(setup_codemie_base, provider):
    """
    Test codemie doctor command execution and validate health check output.

    Tests both LiteLLM and SSO providers with provider-specific validations.
    """
    logger.info(f"Executing codemie doctor command for {provider} provider...")

    result = subprocess.run(
        ["codemie", "doctor"],
        capture_output=True,
        text=True,
        timeout=120,
    )

    logger.info(f"Command exit code: {result.returncode}")
    logger.info(f"STDOUT:\n{result.stdout}")
    if result.stderr:
        logger.warning(f"STDERR:\n{result.stderr}")

    # Verify command executed successfully
    assert_that(
        result.returncode,
        equal_to(0),
        f"codemie doctor should execute successfully: {result.stderr}",
    )

    stdout = result.stdout
    stderr = result.stderr

    # Verify Node.js check
    assert_that(
        stdout,
        contains_string("Node.js:"),
        "Output should contain Node.js version check",
    )
    assert_that(
        stdout,
        matches_regexp(r"✓ Version v\d+\.\d+\.\d+"),
        "Should show Node.js version",
    )

    # Verify npm check
    assert_that(
        stdout, contains_string("npm:"), "Output should contain npm version check"
    )
    assert_that(
        stdout, matches_regexp(r"✓ Version \d+\.\d+\.\d+"), "Should show npm version"
    )

    # Verify Python check
    assert_that(
        stdout, contains_string("Python:"), "Output should contain Python version check"
    )
    assert_that(
        stdout, matches_regexp(r"✓ Version \d+\.\d+\.\d+"), "Should show Python version"
    )

    # Verify Active Profile section
    assert_that(
        stdout,
        contains_string("Active Profile:"),
        "Output should contain Active Profile section",
    )
    assert_that(stdout, contains_string("✓ Provider:"), "Should show provider check")
    assert_that(stdout, contains_string("✓ Model:"), "Should show model check")

    # Provider-specific validations
    if provider == "litellm":
        logger.info("Validating LiteLLM provider-specific output...")

        # LiteLLM-specific checks
        assert_that(
            stdout,
            contains_string("✓ Base URL:"),
            "Should show base URL check for LiteLLM",
        )
        assert_that(
            stdout,
            contains_string("✓ API Key:"),
            "Should show API key check for LiteLLM",
        )

        # Verify credentials validation (appears in stderr)
        assert_that(
            stderr,
            contains_string("✔ Credentials validated"),
            "Should validate credentials for LiteLLM",
        )

        # Verify available models check (appears in stderr)
        assert_that(
            stderr,
            matches_regexp(r"✔ Found \d+ available models"),
            "Should show available models count for LiteLLM",
        )

        # Verify connectivity test
        assert_that(
            stdout,
            contains_string("Connectivity Test:"),
            "Output should contain connectivity test for LiteLLM",
        )
        assert_that(
            stdout,
            matches_regexp(r"✓ Response time: \d+ms"),
            "Should show response time for LiteLLM",
        )
        assert_that(
            stdout,
            contains_string("Provider is reachable"),
            "Should confirm provider reachability for LiteLLM",
        )

        # Verify model availability check
        assert_that(
            stdout,
            contains_string("is available"),
            "Should confirm configured model is available for LiteLLM",
        )

    elif provider == "sso":
        logger.info("Validating SSO provider-specific output...")

        # SSO-specific checks
        assert_that(
            stdout,
            contains_string("✓ CodeMie URL:"),
            "Should show CodeMie URL check for SSO",
        )

        # Verify SSO Configuration section
        assert_that(
            stdout,
            contains_string("SSO Configuration:"),
            "Output should contain SSO Configuration section",
        )
        assert_that(
            stdout,
            contains_string("✓ CodeMie server accessible"),
            "Should confirm CodeMie server is accessible",
        )
        assert_that(
            stdout,
            contains_string("✓ SSO credentials stored"),
            "Should confirm SSO credentials are stored",
        )
        assert_that(
            stdout,
            matches_regexp(r"✓ Session expires in: \d+ hour"),
            "Should show session expiration time",
        )
        assert_that(
            stdout,
            matches_regexp(r"✓ API access working \(\d+ models available\)"),
            "Should show API access status with model count",
        )

    # Verify Installed Agents section (common for both providers)
    assert_that(
        stdout,
        contains_string("Installed Agents:"),
        "Output should contain Installed Agents section",
    )

    # Verify success message (common for both providers)
    assert_that(
        stdout, contains_string("✓ All checks passed!"), "Should show success message"
    )

    logger.info(
        f"codemie doctor health check completed successfully for {provider} provider"
    )
