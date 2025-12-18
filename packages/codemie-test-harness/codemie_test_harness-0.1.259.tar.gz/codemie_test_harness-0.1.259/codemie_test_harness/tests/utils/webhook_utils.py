from typing import Any, Dict

from codemie_test_harness.tests.utils.base_utils import BaseUtils


class WebhookUtils(BaseUtils):
    """Utility class for webhook operations in CodeMie test harness."""

    def trigger_webhook(self, webhook_id: str, data: Dict[str, Any] = None):
        return self.client.webhook.trigger(webhook_id, data)
