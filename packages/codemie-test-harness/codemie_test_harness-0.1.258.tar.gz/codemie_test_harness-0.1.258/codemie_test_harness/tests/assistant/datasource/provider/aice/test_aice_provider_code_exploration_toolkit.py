"""
E2E tests for AICE Provider CodeExplorationToolkit.

This test suite verifies the end-to-end functionality of creating a datasource provider,
indexing a CodeAnalysisToolkit datasource, creating a CodeExplorationToolkit datasource
that uses provider_toolkit_test_data the CodeAnalysisToolkit datasource, creating an assistant with the
CodeExplorationToolkit, and validating that the assistant uses the appropriate tools
to answer questions.
"""

import pytest
from codemie_sdk.models.assistant import ToolKitDetails, ToolDetails
from hamcrest import assert_that, is_not, empty

from codemie_test_harness.tests.enums.tools import CodeExplorationTools, Toolkit
from codemie_test_harness.tests.test_data.provider_toolkit_test_data import (
    code_exploration_toolkit_test_data,
)
from codemie_test_harness.tests.utils.base_utils import (
    assert_tool_triggered,
)
from codemie_test_harness.tests.utils.env_resolver import EnvironmentResolver


@pytest.mark.datasource
@pytest.mark.provider
@pytest.mark.aice
@pytest.mark.api
@pytest.mark.not_for_parallel_run
@pytest.mark.parametrize("question, expected_tool", code_exploration_toolkit_test_data)
@pytest.mark.skipif(
    EnvironmentResolver.is_sandbox(),
    reason="AICE is not configured for sandbox environments",
)
def test_code_exploration_toolkit(
    assistant_utils,
    provider_context,
    code_exploration_datasource,
    question,
    expected_tool,
):
    """
    Test for CodeExplorationToolkit with AICE provider.

    This test:
    1. Uses existing CodeExplorationToolkit from provider
    2. Creates a CodeAnalysisToolkit datasource (via fixture)
    3. Creates a CodeExplorationToolkit datasource that references the CodeAnalysisToolkit datasource
    4. Creates an assistant with the CodeExplorationToolkit
    5. Asks a question to verify the assistant uses the appropriate tool

    Args:
        assistant_utils: Utility for assistant operations
        provider_context: Provider context fixture
        code_exploration_datasource: Indexed datasource fixture
        question: Question to ask the assistant
        expected_tool: Expected tool to be triggered
    """

    # Create list of tools from CodeExplorationTools enum
    tools = [ToolDetails(name=tool.value) for tool in CodeExplorationTools]

    # Create toolkit details with configuration
    toolkit_details = ToolKitDetails(
        toolkit=Toolkit.CODE_EXPLORATION,
        tools=tools,
        is_external=True,  # Provider-based toolkit
    )

    # Create assistant with CodeExplorationToolkit
    system_prompt = """You are a code exploration assistant.
            Always use the tools available to you to provide accurate answers."""

    test_assistant = assistant_utils.create_assistant(
        system_prompt=system_prompt,
        toolkits=[toolkit_details],
        context=[provider_context(code_exploration_datasource)],
    )

    # Ask the assistant
    answer, triggered_tools = assistant_utils.ask_assistant(
        test_assistant, question, minimal_response=False
    )

    # Verify the expected tool was triggered
    assert_tool_triggered(expected_tool, triggered_tools)

    # Verify we got a non-empty response
    assert_that(answer, is_not(empty()), "Assistant should provide an answer.")
