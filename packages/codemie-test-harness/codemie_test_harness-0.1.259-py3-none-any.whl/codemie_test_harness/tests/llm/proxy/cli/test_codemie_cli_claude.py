"""
Tests for codemie CLI tool installation and claude command execution.

This test suite verifies:
1. Installation of @codemieai/code npm package
2. Configuration file creation
3. Claude provider installation
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
def setup_claude_provider(setup_codemie_base):
    """
    Install claude provider.

    Depends on setup_codemie_base fixture from conftest.py.
    """
    logger.info("Installing claude provider...")
    claude_install_result = subprocess.run(
        ["codemie", "install", "claude"],
        capture_output=True,
        text=True,
        timeout=120,
    )

    if claude_install_result.returncode != 0:
        logger.warning(
            f"codemie install claude returned non-zero: {claude_install_result.stderr}"
        )

    logger.info(f"Claude install output: {claude_install_result.stdout}")


# Claude models from the enum
CLAUDE_MODELS = [
    ModelTypes.CLAUDE_SONNET_37_VERTEX,
    ModelTypes.CLAUDE_37_SONNET_V1,
    ModelTypes.CLAUDE_4_SONNET,
    ModelTypes.CLAUDE_4_5_SONNET,
    ModelTypes.CLAUDE_4_OPUS,
    ModelTypes.CLAUDE_4_1_OPUS,
    ModelTypes.CLAUDE_4_SONNET_1M,
    ModelTypes.CLAUDE_4_5_HAIKU,
]


@pytest.mark.proxy
@pytest.mark.api
@pytest.mark.not_for_parallel_run
@pytest.mark.parametrize("model", CLAUDE_MODELS, ids=lambda m: m.value)
@pytest.mark.skipif(
    EnvironmentResolver.is_sandbox(),
    reason="LiteLLM is not configured for sandbox environments",
)
def test_codemie_claude_execution(similarity_check, model):
    """
    Test codemie-claude command execution with different Claude models.
    """
    result = subprocess.run(
        ["codemie-claude", SIMPLE_GREETING_PROMPT, "--model", model.value],
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert_that(result.returncode, equal_to(0), f"{result.stderr}{result.stdout}")

    response = result.stdout.strip().split("\n")[-1]
    similarity_check.check_similarity(response, "Hello")
