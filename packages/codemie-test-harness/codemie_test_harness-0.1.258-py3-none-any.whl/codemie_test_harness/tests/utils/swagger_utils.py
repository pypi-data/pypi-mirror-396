"""
Swagger/OpenAPI documentation endpoint utilities.

This module provides utilities for testing Swagger/OpenAPI documentation endpoints.
"""

import requests
from typing import Dict, Any

from codemie_test_harness.tests import API_DOMEN, VERIFY_SSL
from codemie_test_harness.tests.utils.base_utils import BaseUtils


class SwaggerUtils(BaseUtils):
    """Utilities for testing Swagger/OpenAPI documentation endpoints."""

    def __init__(self, client):
        super().__init__(client)
        self.swagger_url = f"{API_DOMEN}/docs"
        self.openapi_json_url = f"{API_DOMEN}/openapi.json"
        self._headers = {"Authorization": f"Bearer {client.token}"}

    def get_swagger_page(self, timeout: int = None) -> requests.Response:
        """
        Get the Swagger documentation HTML page.

        Args:
            timeout: Optional timeout in seconds for the request

        Returns:
            Response object from the Swagger endpoint
        """
        return requests.get(
            self.swagger_url,
            headers=self._headers,
            verify=VERIFY_SSL,
            timeout=timeout,
        )

    def get_openapi_json(self) -> requests.Response:
        """
        Get the OpenAPI JSON specification.

        Returns:
            Response object containing the OpenAPI JSON
        """
        return requests.get(
            self.openapi_json_url,
            headers=self._headers,
            verify=VERIFY_SSL,
        )

    @staticmethod
    def validate_swagger_page_content(response: requests.Response) -> bool:
        """
        Validate that the Swagger page contains expected keywords.

        Args:
            response: Response object from the Swagger endpoint

        Returns:
            True if any of the expected keywords are found in the response
        """
        content = response.text.lower()
        keywords = ["swagger", "openapi", "api", "docs"]
        return any(keyword in content for keyword in keywords)

    def get_openapi_spec(self) -> Dict[str, Any]:
        """
        Get the OpenAPI specification as a parsed JSON dictionary.

        Returns:
            Parsed OpenAPI specification dictionary
        """
        response = self.get_openapi_json()
        response.raise_for_status()
        return response.json()
