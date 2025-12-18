import logging

import requests

from codemie_test_harness.tests.utils.credentials_manager import CredentialsManager

logger = logging.getLogger(__name__)

JIRA_PROJECT_KEYS = {"server": "EPMCDMETST", "cloud": "SCRUM"}


class JiraUtils:
    """Utility class for interacting with Jira API."""

    def __init__(self, is_cloud: bool = False):
        """
        Initialize Jira utilities with credentials from CredentialsManager.

        Args:
            is_cloud: Whether to use Jira Cloud or Jira Server credentials
        """
        self.is_cloud = is_cloud

        if is_cloud:
            self.jira_url = CredentialsManager.get_parameter("JIRA_CLOUD_URL")
            self.token = CredentialsManager.get_parameter("JIRA_CLOUD_TOKEN")
            self.email = CredentialsManager.get_parameter("JIRA_CLOUD_EMAIL")
            self.auth = (self.email, self.token)
            self.headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
            self.jira_api = "/rest/api/3"
            self.search_endpoint = "/search/jql"
            self.project_key = JIRA_PROJECT_KEYS["cloud"]
        else:
            self.jira_url = CredentialsManager.get_parameter("JIRA_URL")
            self.token = CredentialsManager.get_parameter("JIRA_TOKEN")
            self.email = None
            self.auth = None
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
            self.jira_api = "/rest/api/2"
            self.search_endpoint = "/search"
            self.project_key = JIRA_PROJECT_KEYS["server"]

    def delete_jira_item(self, issue_key: str):
        """
        Delete a Jira issue via Jira API.

        Args:
            issue_key: The Jira issue key (e.g., 'PROJ-123')
        """
        # Construct API endpoint
        endpoint = f"{self.jira_url}{self.jira_api}/issue/{issue_key}"

        try:
            logger.info(f"Deleting Jira issue: {issue_key}")
            requests.delete(
                url=endpoint,
                headers=self.headers,
                auth=self.auth,
                verify=True,
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Error deleting Jira issue {issue_key}: {str(e)}")

    def cleanup_jira_project(self, summary_prefix: str, project_key: str = None):
        """
        Clean up Jira issues in a project with summary starting with specified prefix.

        Args:
            project_key: The Jira project key (e.g., 'EPMCDMETST')
            summary_prefix: The prefix to filter issues by summary (e.g., autotest_entity_prefix)
        """
        # Construct JQL query to find all issues in the project
        # We'll filter by summary prefix in Python since JQL text search has limitations
        project_key = self.project_key if not project_key else project_key

        jql = f'project = "{project_key}"'

        try:
            # Search for issues matching the JQL
            search_endpoint = f"{self.jira_url}{self.jira_api}{self.search_endpoint}"
            params = {
                "jql": jql,
                "maxResults": 100,
                "fields": "key,summary",
            }

            logger.info(
                f"Searching for Jira issues in project {project_key} with summary starting with '{summary_prefix}'"
            )
            response = requests.get(
                url=search_endpoint,
                headers=self.headers,
                auth=self.auth,
                params=params,
                verify=True,
            )

            if response.status_code == 200:
                all_issues = response.json().get("issues", [])

                # Filter issues by summary prefix in Python
                issues_to_delete = [
                    issue
                    for issue in all_issues
                    if issue.get("fields", {})
                    .get("summary", "")
                    .startswith(summary_prefix)
                ]

                # Delete each issue
                for issue in issues_to_delete:
                    self.delete_jira_item(issue["key"])
            else:
                logger.error(
                    f"Failed to search for issues. Status: {response.status_code}, Response: {response.text}"
                )

        except requests.exceptions.RequestException as e:
            logger.error(
                f"Error during Jira cleanup for project {project_key}: {str(e)}"
            )
