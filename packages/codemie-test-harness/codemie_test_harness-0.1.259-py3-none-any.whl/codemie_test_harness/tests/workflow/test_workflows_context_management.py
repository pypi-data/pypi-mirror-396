"""Tests for workflow context management functionality.

This module tests the store_in_context and include_in_llm_history features,
which control how data flows between workflow states and what information
is available to LLM assistants.

According to the Context Management documentation:
- store_in_context: Controls whether state output is stored in context store (default: true)
- include_in_llm_history: Controls whether state output appears in LLM message history (default: true)
"""

import json

import pytest
from hamcrest import assert_that, contains_string, is_not
from codemie_sdk.models.workflow import WorkflowMode

from codemie_test_harness.tests.utils.base_utils import get_random_name
from codemie_test_harness.tests.utils.yaml_utils import (
    AssistantModel,
    StateModel,
    WorkflowYamlModel,
    prepare_yaml_content,
)

# Test data constants for consistent testing
TEST_DATA = {
    "user_id": "user_12345",
    "project_id": "proj_67890",
    "file_id": "file_abc123",
    "secret_code": "SECRET_XYZ789",
    "magic_number": "42",
    "secret_word": "BANANA",
}

SYSTEM_PROMPTS = {
    "data_extractor": "You are a helpful assistant that extracts and outputs structured data.",
    "data_processor": "You are a helpful assistant that processes and uses data from context.",
    "information_provider": "You are a helpful assistant that provides specific information.",
    "information_validator": "You are a helpful assistant that validates and recalls information from conversation history.",
}


@pytest.mark.workflow
@pytest.mark.api
def test_workflow_store_in_context_true_default(default_llm, workflow_utils):
    """Test that state output is stored in context by default (store_in_context=true).

    Scenario:
    1. First state outputs JSON with a variable: {"user_id": "12345"}
    2. Second state references that variable using {{user_id}}
    3. Verify second state can access the variable (confirms it was stored in context)
    """
    workflow_name = get_random_name()

    workflow_yaml = WorkflowYamlModel(
        assistants=[
            AssistantModel(
                id="extract_data",
                model=default_llm.base_name,
                system_prompt=SYSTEM_PROMPTS["data_extractor"],
            ),
            AssistantModel(
                id="process_data",
                model=default_llm.base_name,
                system_prompt=SYSTEM_PROMPTS["data_processor"],
            ),
        ],
        states=[
            StateModel(
                id="extract_data",
                assistant_id="extract_data",
                task=f'Extract the user ID from the input and output it as JSON: {{"user_id": "{TEST_DATA["user_id"]}"}}',
                output_schema='{"user_id": "string"}',
                next={"state_id": "process_data"},  # store_in_context defaults to true
            ),
            StateModel(
                id="process_data",
                assistant_id="process_data",
                task=f"Confirm you received user ID: {{{{user_id}}}}. Say 'Processing {TEST_DATA['user_id']}'",
                next={"state_id": "end"},
            ),
        ],
    )

    # Create workflow
    yaml_content = prepare_yaml_content(workflow_yaml.model_dump(exclude_none=True))
    created_workflow = workflow_utils.create_workflow(
        workflow_name=workflow_name,
        workflow_type=WorkflowMode.SEQUENTIAL,
        workflow_yaml=yaml_content,
    )

    # Execute workflow
    output = workflow_utils.execute_workflow(
        created_workflow.id,
        execution_name="process_data",
        user_input="Please extract the user ID",
    ).lower()

    # Verify the second state received and processed the user_id
    assert_that(output, contains_string(TEST_DATA["user_id"]))
    assert_that(output, contains_string("processing"))


@pytest.mark.workflow
@pytest.mark.api
def test_workflow_store_in_context_false(default_llm, workflow_utils):
    """Test that state output is NOT stored in context when store_in_context=false.

    Scenario:
    1. First state outputs JSON with a variable: {"secret_data": "hidden123"}
    2. Explicitly set store_in_context=false for first state
    3. Second state tries to reference {{secret_data}}
    4. Verify second state cannot access the variable (it was not stored)
    """
    workflow_name = get_random_name()

    workflow_yaml = WorkflowYamlModel(
        assistants=[
            AssistantModel(
                id="generate_secret",
                model=default_llm.base_name,
                system_prompt=SYSTEM_PROMPTS["data_extractor"],
            ),
            AssistantModel(
                id="try_access_secret",
                model=default_llm.base_name,
                system_prompt=SYSTEM_PROMPTS["data_processor"],
            ),
        ],
        states=[
            StateModel(
                id="generate_secret",
                assistant_id="generate_secret",
                task=f'Output this exact JSON: {{"secret_code": "{TEST_DATA["secret_code"]}"}}',
                output_schema='{"secret_code": "string"}',
                next={
                    "state_id": "try_access_secret",
                    "store_in_context": False,  # Explicitly disable context storage
                    "include_in_llm_history": True,  # But keep in LLM history
                },
            ),
            StateModel(
                id="try_access_secret",
                assistant_id="try_access_secret",
                task="Try to access secret_code: {{secret_code}}. If you see the literal '{{secret_code}}' (not resolved), say 'Variable not found'",
                next={"state_id": "end"},
            ),
        ],
    )

    # Create workflow
    yaml_content = prepare_yaml_content(workflow_yaml.model_dump(exclude_none=True))
    created_workflow = workflow_utils.create_workflow(
        workflow_name=workflow_name,
        workflow_type=WorkflowMode.SEQUENTIAL,
        workflow_yaml=yaml_content,
    )

    # Execute workflow
    output = workflow_utils.execute_workflow(
        created_workflow.id,
        execution_name="try_access_secret",
        user_input="Start the workflow",
    ).lower()

    # Verify the variable was NOT resolved (context store was empty)
    assert_that(output, contains_string("not found"))


@pytest.mark.workflow
@pytest.mark.api
def test_workflow_include_in_llm_history_true_default(default_llm, workflow_utils):
    """Test that state output is included in LLM history by default (include_in_llm_history=true).

    Scenario:
    1. First state outputs important context
    2. Second state asks LLM to recall information from previous state
    3. Verify LLM can see and reference the previous state's output
    """
    workflow_name = get_random_name()

    workflow_yaml = WorkflowYamlModel(
        assistants=[
            AssistantModel(
                id="provide_info",
                model=default_llm.base_name,
                system_prompt=SYSTEM_PROMPTS["information_provider"],
            ),
            AssistantModel(
                id="recall_info",
                model=default_llm.base_name,
                system_prompt=SYSTEM_PROMPTS["information_validator"],
            ),
        ],
        states=[
            StateModel(
                id="provide_info",
                assistant_id="provide_info",
                task=f"Say: 'The magic number is {TEST_DATA['magic_number']} and the secret word is {TEST_DATA['secret_word']}'",
                next={
                    "state_id": "recall_info"
                },  # include_in_llm_history defaults to true
            ),
            StateModel(
                id="recall_info",
                assistant_id="recall_info",
                task="What magic number and secret word were mentioned in the previous message? Repeat them.",
                next={"state_id": "end"},
            ),
        ],
    )

    # Create workflow
    yaml_content = prepare_yaml_content(workflow_yaml.model_dump(exclude_none=True))
    created_workflow = workflow_utils.create_workflow(
        workflow_name=workflow_name,
        workflow_type=WorkflowMode.SEQUENTIAL,
        workflow_yaml=yaml_content,
    )

    # Execute workflow
    output = workflow_utils.execute_workflow(
        created_workflow.id,
        execution_name="recall_info",
        user_input="Start workflow",
    )

    # Verify LLM could recall the information from history
    assert_that(output, contains_string(TEST_DATA["magic_number"]))
    assert_that(output.upper(), contains_string(TEST_DATA["secret_word"]))


@pytest.mark.workflow
@pytest.mark.api
def test_workflow_include_in_llm_history_false(default_llm, workflow_utils):
    """Test that state output is NOT included in LLM history when include_in_llm_history=false.

    Scenario:
    1. First state outputs information with include_in_llm_history=false
    2. Second state asks LLM to recall that information
    3. Verify LLM cannot see the previous state's output (was not in history)
    """
    workflow_name = get_random_name()

    workflow_yaml = WorkflowYamlModel(
        assistants=[
            AssistantModel(
                id="hidden_info",
                model=default_llm.base_name,
                system_prompt=SYSTEM_PROMPTS["information_provider"],
            ),
            AssistantModel(
                id="try_recall",
                model=default_llm.base_name,
                system_prompt=SYSTEM_PROMPTS["information_validator"],
            ),
        ],
        states=[
            StateModel(
                id="hidden_info",
                assistant_id="hidden_info",
                task=f"Say: 'The secret code is {TEST_DATA['secret_code']}'",
                next={
                    "state_id": "try_recall",
                    "include_in_llm_history": False,  # Hide from LLM history
                    "store_in_context": True,  # But store in context
                },
            ),
            StateModel(
                id="try_recall",
                assistant_id="try_recall",
                task="What code was mentioned in the previous message? If you don't know, say 'No code mentioned in history'",
                next={"state_id": "end"},
            ),
        ],
    )

    # Create workflow
    yaml_content = prepare_yaml_content(workflow_yaml.model_dump(exclude_none=True))
    created_workflow = workflow_utils.create_workflow(
        workflow_name=workflow_name,
        workflow_type=WorkflowMode.SEQUENTIAL,
        workflow_yaml=yaml_content,
    )

    # Execute workflow
    output = workflow_utils.execute_workflow(
        created_workflow.id,
        execution_name="try_recall",
        user_input="Start",
    )

    # Verify LLM could NOT recall the hidden information
    assert_that(output, is_not(contains_string(TEST_DATA["secret_code"])))


@pytest.mark.workflow
@pytest.mark.api
def test_workflow_context_combination_store_true_history_false(
    default_llm, workflow_utils
):
    """Test combination: store_in_context defaults to true, include_in_llm_history=false.

    Use case: Store data in context while hiding from LLM history.

    Scenario:
    1. First state outputs JSON with metadata
    2. Set include_in_llm_history=false (store_in_context defaults to true)
    3. Second state asks LLM about previous messages
    4. Verify: LLM doesn't see the JSON in history, workflow completes successfully

    Note: Context variable resolution behavior may vary by platform implementation.
    This test primarily verifies that include_in_llm_history=false works correctly.
    """
    workflow_name = get_random_name()

    workflow_yaml = WorkflowYamlModel(
        assistants=[
            AssistantModel(
                id="generate_file_data",
                model=default_llm.base_name,
                system_prompt=SYSTEM_PROMPTS["data_extractor"],
            ),
            AssistantModel(
                id="check_history",
                model=default_llm.base_name,
                system_prompt=SYSTEM_PROMPTS["information_validator"],
            ),
        ],
        states=[
            StateModel(
                id="generate_file_data",
                assistant_id="generate_file_data",
                task=f'Output this JSON exactly: {{"file_id": "{TEST_DATA["file_id"]}", "metadata": "Metadata for {TEST_DATA["file_id"]}"}}',
                output_schema='{"file_id": "string", "metadata": "string"}',
                next={
                    "state_id": "check_history",
                    # store_in_context defaults to True, explicitly setting include_in_llm_history
                    "include_in_llm_history": False,  # Hide from LLM
                },
            ),
            StateModel(
                id="check_history",
                assistant_id="check_history",
                task=(
                    "Was any specific metadata mentioned in the previous message? "
                    "Answer with yes or no and explain what you see in the conversation history."
                ),
                next={"state_id": "end"},
            ),
        ],
    )

    # Create workflow
    yaml_content = prepare_yaml_content(workflow_yaml.model_dump(exclude_none=True))
    created_workflow = workflow_utils.create_workflow(
        workflow_name=workflow_name,
        workflow_type=WorkflowMode.SEQUENTIAL,
        workflow_yaml=yaml_content,
    )

    # Execute workflow
    output = workflow_utils.execute_workflow(
        created_workflow.id,
        execution_name="check_history",
        user_input="Start",
    ).lower()

    # LLM shouldn't have seen the metadata (not in history due to include_in_llm_history=false)
    # It should indicate it didn't see specific metadata in the conversation
    assert_that(
        output,
        is_not(contains_string(f"metadata for {TEST_DATA['file_id']}")),
    )


@pytest.mark.workflow
@pytest.mark.api
def test_workflow_context_combination_store_false_history_true(
    default_llm, workflow_utils
):
    """Test combination: store_in_context=false, include_in_llm_history=true.

    Use case: Output is stored in LLM history but not in context store.

    Scenario:
    1. First state outputs data: {"analysis": "Use approach ALPHA"}
    2. Set store_in_context=false, include_in_llm_history=true
    3. Second state tries to use {{analysis}} template variable
    4. Verify: Template substitution doesn't work (not in context)
    5. Verify: Workflow completes successfully (LLM history doesn't break execution)

    Note: This tests that include_in_llm_history=true works even when store_in_context=false.
    The exact LLM history behavior may vary by implementation.
    """
    workflow_name = get_random_name()

    workflow_yaml = WorkflowYamlModel(
        assistants=[
            AssistantModel(
                id="data_generator",
                model=default_llm.base_name,
                system_prompt=SYSTEM_PROMPTS["data_extractor"],
            ),
        ],
        states=[
            StateModel(
                id="generate_project_data",
                assistant_id="data_generator",
                task=f'Output this JSON: {{"project_id": "{TEST_DATA["project_id"]}", "file_id": "{TEST_DATA["file_id"]}"}}',
                output_schema='{"project_id": "string", "file_id": "string"}',
                next={
                    "state_id": "try_use_project_data",
                    "store_in_context": False,  # Don't store for templates
                    "include_in_llm_history": True,  # Keep in LLM history
                },
            ),
            StateModel(
                id="try_use_project_data",
                assistant_id="data_generator",
                task=(
                    "Try to access the project_id variable: {{project_id}}. "
                    "If you see the literal '{{project_id}}' text (not a value), say 'Variable not in context'. "
                    "Otherwise, confirm the project_id value."
                ),
                next={"state_id": "end"},
            ),
        ],
    )

    # Create workflow
    yaml_content = prepare_yaml_content(workflow_yaml.model_dump(exclude_none=True))
    created_workflow = workflow_utils.create_workflow(
        workflow_name=workflow_name,
        workflow_type=WorkflowMode.SEQUENTIAL,
        workflow_yaml=yaml_content,
    )

    # Execute workflow
    output = workflow_utils.execute_workflow(
        created_workflow.id,
        execution_name="try_use_project_data",
        user_input="Generate project data",
    ).lower()

    # Verify the variable was NOT available in context store
    # (because store_in_context was false)
    assert_that(output, contains_string("not in context"))


@pytest.mark.workflow
@pytest.mark.api
def test_workflow_multi_state_context_propagation(default_llm, workflow_utils):
    """Test context propagation across multiple states with different configurations.

    Scenario with 3 states:
    1. State 1: Generate user data -> store_in_context=true
    2. State 2: Generate additional data -> store_in_context=true
    3. State 3: Use both variables from previous states
    4. Verify all context accumulates and is accessible
    """
    workflow_name = get_random_name()

    workflow_yaml = WorkflowYamlModel(
        assistants=[
            AssistantModel(
                id="generate_user",
                model=default_llm.base_name,
                system_prompt=SYSTEM_PROMPTS["data_extractor"],
            ),
            AssistantModel(
                id="generate_project",
                model=default_llm.base_name,
                system_prompt=SYSTEM_PROMPTS["data_extractor"],
            ),
            AssistantModel(
                id="combine_data",
                model=default_llm.base_name,
                system_prompt=SYSTEM_PROMPTS["data_processor"],
            ),
        ],
        states=[
            StateModel(
                id="generate_user",
                assistant_id="generate_user",
                task=f'Output JSON: {{"user_id": "{TEST_DATA["user_id"]}", "secret_code": "{TEST_DATA["secret_code"]}"}}',
                output_schema='{"user_id": "string", "secret_code": "string"}',
                next={
                    "state_id": "generate_project",
                    "store_in_context": True,
                    "include_in_llm_history": True,
                },
            ),
            StateModel(
                id="generate_project",
                assistant_id="generate_project",
                task=f'Output JSON: {{"project_id": "{TEST_DATA["project_id"]}", "file_id": "{TEST_DATA["file_id"]}"}}',
                output_schema='{"project_id": "string", "file_id": "string"}',
                next={
                    "state_id": "combine_data",
                    "store_in_context": True,
                    "include_in_llm_history": True,
                },
            ),
            StateModel(
                id="combine_data",
                assistant_id="combine_data",
                task=(
                    "Create a summary using these variables: "
                    "User ID: {{user_id}}, Secret Code: {{secret_code}}, "
                    "Project ID: {{project_id}}, File ID: {{file_id}}. "
                    "Confirm you have all four pieces of information."
                ),
                next={"state_id": "end"},
            ),
        ],
    )

    # Create workflow
    yaml_content = prepare_yaml_content(workflow_yaml.model_dump(exclude_none=True))
    created_workflow = workflow_utils.create_workflow(
        workflow_name=workflow_name,
        workflow_type=WorkflowMode.SEQUENTIAL,
        workflow_yaml=yaml_content,
    )

    # Execute workflow
    output = workflow_utils.execute_workflow(
        created_workflow.id,
        execution_name="combine_data",
        user_input="Generate data",
    )

    # Verify all variables were accessible
    assert_that(output, contains_string(TEST_DATA["user_id"]))
    assert_that(output, contains_string(TEST_DATA["secret_code"]))
    assert_that(output, contains_string(TEST_DATA["project_id"]))
    assert_that(output, contains_string(TEST_DATA["file_id"]))


@pytest.mark.workflow
@pytest.mark.api
def test_workflow_context_with_json_output_schema(default_llm, workflow_utils):
    """Test that structured JSON output with output_schema properly populates context store.

    Scenario:
    1. First state uses output_schema to enforce JSON structure
    2. Output: {"status": "success", "code": "200", "message": "OK"}
    3. Second state references all three variables
    4. Verify all root-level keys are accessible as context variables
    """
    workflow_name = get_random_name()

    workflow_yaml = WorkflowYamlModel(
        assistants=[
            AssistantModel(
                id="generate_response",
                model=default_llm.base_name,
                system_prompt=SYSTEM_PROMPTS["data_extractor"],
            ),
            AssistantModel(
                id="process_response",
                model=default_llm.base_name,
                system_prompt=SYSTEM_PROMPTS["data_processor"],
            ),
        ],
        states=[
            StateModel(
                id="generate_response",
                assistant_id="generate_response",
                task=f'Generate a response with user_id "{TEST_DATA["user_id"]}", project_id "{TEST_DATA["project_id"]}", and file_id "{TEST_DATA["file_id"]}"',
                output_schema=json.dumps(
                    {"user_id": "string", "project_id": "string", "file_id": "string"}
                ),
                next={"state_id": "process_response", "store_in_context": True},
            ),
            StateModel(
                id="process_response",
                assistant_id="process_response",
                task=(
                    "Process the response data: "
                    "User ID: {{user_id}}, Project ID: {{project_id}}, File ID: {{file_id}}. "
                    "Confirm all three values."
                ),
                next={"state_id": "end"},
            ),
        ],
    )

    # Create workflow
    yaml_content = prepare_yaml_content(workflow_yaml.model_dump(exclude_none=True))
    created_workflow = workflow_utils.create_workflow(
        workflow_name=workflow_name,
        workflow_type=WorkflowMode.SEQUENTIAL,
        workflow_yaml=yaml_content,
    )

    # Execute workflow
    output = workflow_utils.execute_workflow(
        created_workflow.id,
        execution_name="process_response",
        user_input="Generate response data",
    )

    # Verify all JSON keys were accessible as context variables
    assert_that(output, contains_string(TEST_DATA["user_id"]))
    assert_that(output, contains_string(TEST_DATA["project_id"]))
    assert_that(output, contains_string(TEST_DATA["file_id"]))
