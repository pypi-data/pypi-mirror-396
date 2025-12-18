"""
E2E tests for AICE Provider CodeAnalysisToolkit.

This test suite verifies the end-to-end functionality of creating a datasource provider,
indexing a datasource with the CodeAnalysisToolkit, creating an assistant with the toolkit,
and validating that the assistant uses the appropriate tools to answer questions.
"""

import pytest
from codemie_sdk.models.assistant import ToolKitDetails, ToolDetails
from hamcrest import assert_that, is_not, empty

from codemie_test_harness.tests.enums.tools import CodeAnalysisTools, Toolkit
from codemie_test_harness.tests.test_data.provider_toolkit_test_data import (
    code_analysis_toolkit_toolkit_test_data,
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
@pytest.mark.parametrize(
    "question, expected_tool", code_analysis_toolkit_toolkit_test_data
)
@pytest.mark.skipif(
    EnvironmentResolver.is_sandbox(),
    reason="AICE is not configured for sandbox environments",
)
def test_code_analysis_toolkit(
    assistant_utils,
    provider_context,
    code_analysis_datasource,
    question,
    expected_tool,
):
    """
    Test for CodeAnalysisToolkit with AICE provider.

    This test:
    1. Uses existing CodeAnalysisToolkit from provider
    2. Indexes a datasource (via fixture)
    3. Creates an assistant with the CodeAnalysisToolkit
    4. Asks a question to verify the assistant uses the appropriate tool

    Args:
        assistant_utils: Utility for assistant operations
        provider_context: Provider context fixture
        code_analysis_datasource: Indexed datasource fixture
        question: Question to ask the assistant
        expected_tool: Expected tool to be triggered
    """

    # Create list of tools from CodeAnalysisTools enum
    tools = [ToolDetails(name=tool.value) for tool in CodeAnalysisTools]

    # Create toolkit details with configuration
    toolkit_details = ToolKitDetails(
        toolkit=Toolkit.CODE_ANALYSIS,
        tools=tools,
        is_external=True,  # Provider-based toolkit
    )

    # Create assistant with CodeAnalysisToolkit
    system_prompt = """You are a code analysis assistant.
            Always use the tools available to you to provide accurate answers."""

    test_assistant = assistant_utils.create_assistant(
        system_prompt=system_prompt,
        toolkits=[toolkit_details],
        context=[provider_context(code_analysis_datasource)],
    )

    # Ask the assistant
    answer, triggered_tools = assistant_utils.ask_assistant(
        test_assistant, question, minimal_response=False
    )

    # Verify the expected tool was triggered
    assert_tool_triggered(expected_tool, triggered_tools)

    # Verify we got a non-empty response
    assert_that(answer, is_not(empty()), "Assistant should provide an answer.")
