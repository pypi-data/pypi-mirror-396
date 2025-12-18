import logging

import requests

from codemie_test_harness.tests.utils.credentials_manager import CredentialsManager

logger = logging.getLogger(__name__)

CONFLUENCE_SPACE_KEYS = {"server": "EPMCDMETST", "cloud": "CODEMIE"}


class ConfluenceUtils:
    """Utility class for interacting with Confluence API."""

    def __init__(self, is_cloud: bool = False):
        """
        Initialize Confluence utilities with credentials from CredentialsManager.

        Args:
            is_cloud: Whether to use Confluence Cloud or Confluence Server credentials
        """
        self.is_cloud = is_cloud

        if is_cloud:
            self.confluence_url = CredentialsManager.get_parameter(
                "CONFLUENCE_CLOUD_URL"
            )
            self.token = CredentialsManager.get_parameter("CONFLUENCE_CLOUD_TOKEN")
            self.email = CredentialsManager.get_parameter("CONFLUENCE_CLOUD_EMAIL")
            self.auth = (self.email, self.token)
            self.headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
            self.confluence_api = "/wiki/api/v2"
            self.pages_endpoint = "/pages"
            self.space_key = CONFLUENCE_SPACE_KEYS["cloud"]
        else:
            self.confluence_url = CredentialsManager.get_parameter("CONFLUENCE_URL")
            self.token = CredentialsManager.get_parameter("CONFLUENCE_TOKEN")
            self.email = None
            self.auth = None
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
            self.confluence_api = "/rest/api"
            self.pages_endpoint = "/content"
            self.space_key = CONFLUENCE_SPACE_KEYS["server"]

    def delete_confluence_page(self, page_id: str):
        """
        Delete a Confluence page via Confluence API.

        Args:
            page_id: The Confluence page ID
        """
        # Construct API endpoint
        endpoint = (
            f"{self.confluence_url}{self.confluence_api}{self.pages_endpoint}/{page_id}"
        )

        try:
            logger.info(f"Deleting Confluence page: {page_id}")
            requests.delete(
                url=endpoint,
                headers=self.headers,
                auth=self.auth,
                verify=True,
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Error deleting Confluence page {page_id}: {str(e)}")

    def cleanup_confluence_space(self, title_prefix: str, space_key: str = None):
        """
        Clean up Confluence pages in a space with title starting with specified prefix.

        Args:
            title_prefix: The prefix to filter pages by title (e.g., autotest_entity_prefix)
            space_key: The Confluence space key (e.g., 'TEST')
        """
        space_key = self.space_key if not space_key else space_key

        try:
            # Search for pages in the space
            search_endpoint = (
                f"{self.confluence_url}{self.confluence_api}{self.pages_endpoint}"
            )
            params = {
                "spaceKey": space_key,
                "type": "page",
                "limit": 100,
            }

            logger.info(
                f"Searching for Confluence pages in space {space_key} with title starting with '{title_prefix}'"
            )
            response = requests.get(
                url=search_endpoint,
                headers=self.headers,
                auth=self.auth,
                params=params,
                verify=True,
            )

            if response.status_code == 200:
                all_pages = response.json().get("results", [])

                # Filter pages by title prefix
                pages_to_delete = [
                    page
                    for page in all_pages
                    if page.get("title", "").startswith(title_prefix)
                ]

                # Delete each page
                for page in pages_to_delete:
                    self.delete_confluence_page(page["id"])
            else:
                logger.error(
                    f"Failed to search for pages. Status: {response.status_code}, Response: {response.text}"
                )

        except requests.exceptions.RequestException as e:
            logger.error(
                f"Error during Confluence cleanup for space {space_key}: {str(e)}"
            )
