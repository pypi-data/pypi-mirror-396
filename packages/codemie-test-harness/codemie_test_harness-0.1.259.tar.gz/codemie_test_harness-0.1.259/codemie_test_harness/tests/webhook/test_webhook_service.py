"""Webhook integration tests for CodeMie.

This module contains tests for webhook functionality including:
- Basic webhook operations with different resource types (assistant, workflow, datasource)
- Error handling and validation
- Webhook triggering verification
"""

import pytest

from codemie_sdk.models.workflow import ExecutionStatus
from hamcrest import (
    assert_that,
    equal_to,
    greater_than,
    has_length,
    has_item,
)
from codemie_test_harness.tests.utils.base_utils import get_random_name, wait_for_entity
from codemie_test_harness.tests.ui.test_data.datasource_test_data import (
    DataSourceStatus,
)


@pytest.mark.webhook
@pytest.mark.api
class TestWebhookBasicOperations:
    """Basic webhook operations tests - verify webhook creation and triggering for different resource types."""

    def test_webhook_with_assistant(
        self, assistant, webhook_integration, webhook_utils, conversation_utils
    ):
        """Test webhook can be created with assistant and triggers conversation creation."""
        webhook_id = get_random_name()
        message = f"Test message for {webhook_id}"

        # Create assistant
        assistant = assistant()

        # Create webhook integration
        webhook_integration(webhook_id, "assistant", assistant.id)

        # Trigger webhook
        response = webhook_utils.trigger_webhook(webhook_id, data=message)
        assert_that(response.status_code, equal_to(200))
        assert_that(
            response.json()["message"], equal_to("Webhook invoked successfully")
        )

        # Wait for conversation
        conversation = wait_for_entity(
            lambda: conversation_utils.list_conversations(),
            entity_name=f'"{message}"',
        )

        # Verify conversation details
        assert_that(conversation.name.strip('"'), equal_to(message))
        assert_that(conversation.initial_assistant_id, equal_to(assistant.id))
        assert_that(conversation.assistant_ids, has_item(assistant.id))

    def test_webhook_with_workflow(
        self,
        workflow_with_virtual_assistant,
        default_llm,
        webhook_integration,
        webhook_utils,
        workflow_utils,
    ):
        """Test webhook can be created with workflow and triggers workflow execution."""
        webhook_id = get_random_name()
        message = f"Test message for {webhook_id}"

        # Create a simple workflow
        workflow = workflow_with_virtual_assistant(webhook_id)

        # Create webhook integration
        webhook_integration(webhook_id, "workflow", workflow.id)

        # Trigger webhook
        response = webhook_utils.trigger_webhook(webhook_id, data=message)
        assert_that(response.status_code, equal_to(200))
        assert_that(
            response.json()["message"], equal_to("Webhook invoked successfully")
        )

        # Verify workflow execution was created
        executions = workflow_utils.get_executions(workflow)
        assert_that(
            executions,
            has_length(greater_than(0)),
            "Workflow execution should be created",
        )

        # Verify execution details
        execution = executions[0]

        assert_that(execution.prompt.strip('""'), equal_to(message))
        assert_that(execution.workflow_id, equal_to(workflow.id))
        assert_that(execution.status, equal_to(ExecutionStatus.IN_PROGRESS))

    @pytest.mark.parametrize(
        "datasource_fixture",
        [
            "jira_datasource",
            "confluence_datasource",
            "code_datasource",
        ],
    )
    def test_webhook_with_datasource(
        self,
        request,
        datasource_fixture,
        webhook_integration,
        webhook_utils,
        datasource_utils,
    ):
        """Test webhook can be created with datasource and triggers successfully.

        This test verifies webhook works with datasource as the resource type.
        After triggering the webhook, it verifies that datasource indexing is in progress.

        Test is parametrized to work with different datasource types:
        - jira_datasource
        - confluence_datasource
        - code_datasource
        """

        # Get the datasource from the fixture
        datasource = request.getfixturevalue(datasource_fixture)

        # Create webhook integration with datasource
        webhook_id = get_random_name()
        webhook_integration(webhook_id, "datasource", datasource.id)

        # Trigger webhook
        response = webhook_utils.trigger_webhook(webhook_id)
        assert_that(response.status_code, equal_to(200))
        assert_that(
            response.json()["message"], equal_to("Webhook invoked successfully")
        )

        # Verify datasource exists and check its status (indexing should be in progress)
        triggered_datasource = datasource_utils.get_datasource(datasource.id)

        assert_that(triggered_datasource.id, equal_to(datasource.id))
        assert_that(triggered_datasource.name, equal_to(datasource.name))
        assert_that(triggered_datasource.status, DataSourceStatus.FETCHING)


@pytest.mark.webhook
@pytest.mark.api
class TestWebhookErrorHandling:
    """Tests for webhook error handling - invalid IDs and disabled webhooks."""

    def test_webhook_trigger_with_invalid_id(self, webhook_utils):
        """Test that triggering webhook with invalid ID returns error."""
        invalid_webhook_id = "non_existent_webhook_" + get_random_name()

        response = webhook_utils.trigger_webhook(invalid_webhook_id)

        # Should return error status code
        assert_that(response.status_code, equal_to(500))
        assert_that(response.json()["detail"], equal_to("Webhook processing failed"))

    def test_webhook_trigger_with_disabled_webhook(
        self, assistant, webhook_integration, webhook_utils, conversation_utils
    ):
        """Test that disabled webhook cannot be triggered."""
        assistant = assistant()
        webhook_id = get_random_name()
        message = f"Test message for {webhook_id}"

        # Create webhook in disabled state
        webhook_integration(webhook_id, "assistant", assistant.id, is_enabled=False)

        # Try to trigger disabled webhook
        response = webhook_utils.trigger_webhook(webhook_id, data=message)

        # Should return error status code (not 200) for disabled webhook
        assert_that(response.status_code, equal_to(500))
        assert_that(response.json()["detail"], equal_to("Webhook processing failed"))

        conversations = conversation_utils.get_conversation_by_assistant_id(
            assistant.id
        )
        assert_that(len(conversations), equal_to(0))

    def test_webhook_invalid_resource_id(self, webhook_integration, webhook_utils):
        """Test webhook with invalid resource ID."""
        webhook_id = get_random_name()
        message = f"Test message for {webhook_id}"
        invalid_resource_id = "invalid_resource_" + get_random_name()

        # Create webhook with invalid resource ID
        webhook_integration(webhook_id, "assistant", invalid_resource_id)

        # Trigger webhook - should handle gracefully
        response = webhook_utils.trigger_webhook(webhook_id, data=message)

        assert_that(response.status_code, equal_to(500))
        assert_that(response.json()["detail"], equal_to("Webhook processing failed"))

    def test_webhook_with_file_datasource(
        self,
        request,
        file_datasource,
        webhook_integration,
        webhook_utils,
        datasource_utils,
    ):
        """Test webhook with unsupported datasource type."""

        # Create webhook integration with datasource
        webhook_id = get_random_name()
        webhook_integration(webhook_id, "datasource", file_datasource.id)

        # Trigger webhook
        response = webhook_utils.trigger_webhook(webhook_id)
        assert_that(response.status_code, equal_to(403))
        assert_that(
            response.json()["detail"],
            equal_to(
                "Datasource type 'knowledge_base_file' is not supported via webhook."
            ),
        )
