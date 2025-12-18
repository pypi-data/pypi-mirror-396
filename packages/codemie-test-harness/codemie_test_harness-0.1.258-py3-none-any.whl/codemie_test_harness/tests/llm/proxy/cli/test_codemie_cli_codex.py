"""
Tests for codemie CLI tool installation and codex command execution.

This test suite verifies:
1. Installation of @codemieai/code npm package
2. Configuration file creation
3. Codex provider installation
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
def setup_codex_provider(setup_codemie_base):
    """
    Install codex provider.

    Depends on setup_codemie_base fixture from conftest.py.
    """
    logger.info("Installing codex provider...")
    codex_install_result = subprocess.run(
        ["codemie", "install", "codex"],
        capture_output=True,
        text=True,
        timeout=120,
    )

    if codex_install_result.returncode != 0:
        logger.warning(
            f"codemie install codex returned non-zero: {codex_install_result.stderr}"
        )

    logger.info(f"Codex install output: {codex_install_result.stdout}")


# OpenAI Codex models from the enum
CODEX_MODELS = [
    ModelTypes.GPT_41,
    ModelTypes.GPT_41_MINI,
    ModelTypes.GPT_4o_2024_08_06,
    ModelTypes.GPT_4o_2024_11_20,
    ModelTypes.GPT_4o_MINI,
    ModelTypes.O3_MINI,
    ModelTypes.O3_2025_04_16,
    ModelTypes.O4_MINI_2025_04_16,
    ModelTypes.O1,
    ModelTypes.GPT_5_2025_08_07,
    ModelTypes.GPT_5_NANO_2025_08_07,
    ModelTypes.GPT_5_MINI_2025_08_07,
]


# @pytest.mark.proxy
# @pytest.mark.api
# @pytest.mark.not_for_parallel_run
@pytest.mark.parametrize("model", CODEX_MODELS, ids=lambda m: m.value)
@pytest.mark.skipif(
    EnvironmentResolver.is_sandbox(),
    reason="LiteLLM is not configured for sandbox environments",
)
def test_codemie_codex_execution(similarity_check, model):
    """
    Test codemie-codex command execution with different OpenAI models.
    """
    result = subprocess.run(
        ["codemie-codex", SIMPLE_GREETING_PROMPT, "--model", model.value],
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert_that(result.returncode, equal_to(0), f"{result.stderr}{result.stdout}")

    response = result.stdout.strip().split("\n")[-1]
    similarity_check.check_similarity(response, "Hello")
