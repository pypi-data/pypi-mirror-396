"""
Tests for codemie CLI tool installation and gemini command execution.

This test suite verifies:
1. Installation of @codemieai/code npm package
2. Configuration file creation
3. Gemini provider installation
4. Command execution and response validation
"""

import subprocess

import pytest
from hamcrest import assert_that, equal_to

from codemie_test_harness.tests.enums.model_types import ModelTypes
from codemie_test_harness.tests.llm.assistants.test_llm import SIMPLE_GREETING_PROMPT
from codemie_test_harness.tests.utils.env_resolver import EnvironmentResolver
from codemie_test_harness.tests.utils.logger_util import setup_logger

logger = setup_logger(__name__)


@pytest.fixture(scope="session", autouse=True)
def setup_gemini_provider(setup_codemie_base):
    """
    Install gemini provider.

    Depends on setup_codemie_base fixture from conftest.py.
    """
    logger.info("Installing gemini provider...")
    gemini_install_result = subprocess.run(
        ["codemie", "install", "gemini"],
        capture_output=True,
        text=True,
        timeout=120,
    )

    if gemini_install_result.returncode != 0:
        logger.warning(
            f"codemie install gemini returned non-zero: {gemini_install_result.stderr}"
        )

    logger.info(f"Gemini install output: {gemini_install_result.stdout}")


# Gemini models from the enum
GEMINI_MODELS = [
    ModelTypes.GEMINI_25_FLASH,
    ModelTypes.GEMINI_25_PRO,
    ModelTypes.GEMINI_3_PRO,
]


@pytest.mark.proxy
@pytest.mark.api
@pytest.mark.not_for_parallel_run
@pytest.mark.parametrize("model", GEMINI_MODELS, ids=lambda m: m.value)
@pytest.mark.skipif(
    EnvironmentResolver.is_sandbox(),
    reason="LiteLLM is not configured for sandbox environments",
)
def test_codemie_gemini_execution(similarity_check, model):
    """
    Test codemie-gemini command execution with different Gemini models.
    """
    result = subprocess.run(
        ["codemie-gemini", SIMPLE_GREETING_PROMPT, "--model", model.value],
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert_that(result.returncode, equal_to(0), f"{result.stderr}{result.stdout}")

    response = result.stdout.strip().split("\n")[-1]
    similarity_check.check_similarity(response, "Hello")
