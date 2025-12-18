import time
from time import sleep

from codemie_test_harness.tests.utils.credentials_manager import CredentialsManager

from codemie_sdk.exceptions import ApiError
from codemie_sdk.models.datasource import (
    DataSource,
    CodeDataSourceRequest,
    ConfluenceDataSourceRequest,
    JiraDataSourceRequest,
    GoogleDataSourceRequest,
    FileDataSourceRequest,
    UpdateCodeDataSourceRequest,
    UpdateGoogleDataSourceRequest,
    UpdateFileDataSourceRequest,
    CodeDataSourceType,
    UpdateConfluenceDataSourceRequest,
    UpdateJiraDataSourceRequest,
    CodeExplorationDataSourceRequest,
    CodeAnalysisDataSourceRequest,
)
from codemie_sdk.models.datasource import DataSourceStatus
from codemie_test_harness.tests import PROJECT
from codemie_test_harness.tests.utils.base_utils import (
    BaseUtils,
    get_random_name,
    wait_for_entity,
)


class DataSourceUtils(BaseUtils):
    def create_code_datasource(self, **kwargs):
        create_request_params = {
            "project_name": kwargs.get("project_name", PROJECT),
            "link": kwargs.get("link"),
            "branch": kwargs.get("branch"),
            "index_type": CodeDataSourceType.CODE,
            "embeddings_model": kwargs.get("embeddings_model"),
            "setting_id": kwargs.get("setting_id"),
            "description": kwargs.get("description", get_random_name()),
            "project_space_visible": kwargs.get("project_space_visible", False),
            "name": kwargs.get("name", get_random_name()),
        }

        create_datasource_request = CodeDataSourceRequest(**create_request_params)

        self.client.datasources.create(create_datasource_request)

        datasource = wait_for_entity(
            lambda: self.client.datasources.list(per_page=200),
            entity_name=create_datasource_request.name,
        )

        return self.wait_for_indexing(datasource.id)

    def update_code_datasource(self, datasource_id, **kwargs):
        datasource = self.get_datasource(datasource_id)

        update_request_params = {
            "project_name": datasource.project_name,
            "link": kwargs.get("link", datasource.code.link),
            "branch": kwargs.get("branch", datasource.code.branch),
            "index_type": CodeDataSourceType.CODE,
            "embeddings_model": kwargs.get(
                "embeddings_model", datasource.embeddings_model
            ),
            "setting_id": kwargs.get("setting_id", datasource.setting_id),
            "description": kwargs.get("description", datasource.description),
            "name": datasource.name,
            "project_space_visible": kwargs.get(
                "project_space_visible", datasource.shared_with_project
            ),
            "full_reindex": kwargs.get("full_reindex", False),
            "skip_reindex": kwargs.get("skip_reindex", True),
            "incremental_reindex": kwargs.get("incremental_reindex", False),
        }

        update_datasource_request = UpdateCodeDataSourceRequest(**update_request_params)

        self.client.datasources.update(datasource.id, update_datasource_request)

        return self.wait_for_indexing(datasource.id)

    def create_gitlab_datasource(self, **kwargs):
        return self.create_code_datasource(
            name=kwargs.get("name", get_random_name()),
            link=kwargs.get("link", CredentialsManager.get_parameter("GITLAB_PROJECT")),
            branch=kwargs.get("branch", "main"),
            setting_id=kwargs.get("setting_id"),
            embeddings_model=kwargs.get("embeddings_model"),
            project_name=kwargs.get("project_name", PROJECT),
        )

    def create_github_datasource(self, **kwargs):
        return self.create_code_datasource(
            name=kwargs.get("name", get_random_name()),
            link=kwargs.get("link", CredentialsManager.get_parameter("GITHUB_PROJECT")),
            branch=kwargs.get("branch", "master"),
            setting_id=kwargs.get("setting_id"),
            embeddings_model=kwargs.get("embeddings_model"),
        )

    def update_gitlab_datasource(self, datasource_id, **kwargs):
        return self.update_code_datasource(datasource_id, **kwargs)

    def create_google_doc_datasource(self, **kwargs):
        datasource_name = kwargs.get("name", get_random_name())

        create_request_params = {
            "name": datasource_name,
            "project_name": PROJECT,
            "description": kwargs.get("description", get_random_name()),
            "google_doc": kwargs.get("google_doc"),
            "shared_with_project": kwargs.get("shared_with_project", False),
        }

        create_datasource_request = GoogleDataSourceRequest(**create_request_params)
        self.client.datasources.create(create_datasource_request)

        datasource = wait_for_entity(
            lambda: self.client.datasources.list(per_page=200),
            entity_name=datasource_name,
        )

        return self.wait_for_indexing(datasource.id)

    def update_google_doc_datasource(self, datasource_id, **kwargs):
        datasource = self.get_datasource(datasource_id)

        update_request_params = {
            "name": kwargs.get("name", datasource.name),
            "project_name": datasource.project_name,
            "description": kwargs.get("description", datasource.description),
            "google_doc": kwargs.get("google_doc", datasource.google_doc_link),
            "full_reindex": kwargs.get("full_reindex", False),
            "skip_reindex": kwargs.get("skip_reindex", True),
            "incremental_reindex": kwargs.get("incremental_reindex", False),
        }

        update_datasource_request = UpdateGoogleDataSourceRequest(
            **update_request_params
        )
        self.client.datasources.update(datasource_id, update_datasource_request)

        return self.wait_for_indexing(datasource_id)

    def create_file_datasource(self, **kwargs):
        datasource_name = kwargs.get("name", get_random_name())

        create_request_params = {
            "name": datasource_name,
            "project_name": PROJECT,
            "description": kwargs.get("description", get_random_name()),
            "shared_with_project": kwargs.get("shared_with_project", False),
            "embeddings_model": kwargs.get("embeddings_model"),
            "csv_separator": kwargs.get("csv_separator", ";"),
            "csv_start_row": kwargs.get("csv_start_row", 1),
            "csv_rows_per_document": kwargs.get("csv_rows_per_document", 1000),
        }
        files = kwargs.get("files")

        create_datasource_request = FileDataSourceRequest(**create_request_params)

        self.client.datasources.create_file_datasource(create_datasource_request, files)

        datasource = wait_for_entity(
            lambda: self.client.datasources.list(per_page=200),
            entity_name=datasource_name,
        )

        return self.wait_for_indexing(datasource.id)

    def update_file_datasource(self, datasource_id, **kwargs) -> DataSource:
        datasource = self.get_datasource(datasource_id)

        update_request_params = {
            "name": datasource.name,
            "project_name": datasource.project_name,
            "description": kwargs.get("description", datasource.description),
            "project_space_visible": kwargs.get(
                "project_space_visible", datasource.shared_with_project
            ),
            "full_reindex": kwargs.get("full_reindex", False),
            "skip_reindex": kwargs.get("skip_reindex", True),
            "incremental_reindex": kwargs.get("incremental_reindex", False),
            "embeddings_model": kwargs.get(
                "embeddings_model", datasource.embeddings_model
            ),
        }

        update_datasource_request = UpdateFileDataSourceRequest(**update_request_params)
        self.client.datasources.update(datasource_id, update_datasource_request)

        return self.wait_for_indexing(datasource_id)

    def wait_for_indexing(
        self,
        datasource_id: str,
        timeout: int = int(CredentialsManager.get_parameter("DEFAULT_TIMEOUT", "120")),
        pool_interval: int = 3,
    ) -> DataSource:
        start_time = time.time()
        while time.time() - start_time < timeout:
            sleep(pool_interval)
            datasource = self.client.datasources.get(datasource_id)
            if datasource.status == DataSourceStatus.COMPLETED:
                return datasource
            elif datasource.status == DataSourceStatus.FAILED:
                raise ApiError(f"Datasource {datasource_id} indexing failed")
        raise TimeoutError("Datasource was not indexed within the timeout period.")

    def wait_for_update_date_change(
        self,
        datasource_id: str,
        timeout: int = 80,
        pool_interval: int = 3,
    ) -> DataSource:
        """Wait for datasource update_date to become greater than created_date.

        This method polls the datasource and waits until the update_date is greater
        than the created_date, indicating that the datasource has been updated/re-indexed.

        Args:
            datasource_id: The ID of the datasource to monitor
            timeout: Maximum time to wait in seconds (default from DEFAULT_TIMEOUT)
            pool_interval: Time between polling attempts in seconds (default 3)

        Returns:
            DataSource: The updated datasource object with update_date > created_date

        Raises:
            TimeoutError: If update_date doesn't change within the timeout period
        """
        start_time = time.time()

        # Get initial datasource state
        datasource = self.client.datasources.get(datasource_id)
        created_date = datasource.created_date

        while time.time() - start_time < timeout:
            sleep(pool_interval)
            datasource = self.client.datasources.get(datasource_id)

            # Check if update_date is greater than created_date
            if datasource.update_date and datasource.update_date > created_date:
                return datasource

        raise TimeoutError(
            f"Datasource {datasource_id} update_date did not change within the timeout period. "
            f"Created: {created_date}, Last checked update: {datasource.update_date}"
        )

    def get_datasource(self, datasource_id):
        return self.client.datasources.get(datasource_id)

    def create_confluence_datasource(self, **kwargs):
        name = kwargs.get("name", get_random_name())
        create_request_params = {
            "name": name,
            "project_name": kwargs.get("project_name", PROJECT),
            "description": kwargs.get("description", get_random_name()),
            "cql": kwargs.get("cql", CredentialsManager.confluence_cql()),
            "project_space_visible": kwargs.get("project_space_visible", False),
            "setting_id": kwargs.get("setting_id"),
        }

        create_datasource_request = ConfluenceDataSourceRequest(**create_request_params)
        self.client.datasources.create(create_datasource_request)
        datasource = wait_for_entity(
            lambda: self.client.datasources.list(per_page=200),
            entity_name=name,
        )

        return self.wait_for_indexing(datasource.id)

    def update_confluence_datasource(self, datasource_id, **kwargs):
        datasource = self.get_datasource(datasource_id)

        update_request_params = {
            "name": kwargs.get("name", datasource.name),
            "project_name": datasource.project_name,
            "description": kwargs.get("description", datasource.description),
            "cql": kwargs.get("cql", datasource.confluence.cql),
            "full_reindex": kwargs.get("full_reindex", False),
            "skip_reindex": kwargs.get("skip_reindex", True),
            "incremental_reindex": kwargs.get("incremental_reindex", False),
            "setting_id": kwargs.get("setting_id", datasource.setting_id),
            "project_space_visible": kwargs.get(
                "project_space_visible", datasource.shared_with_project
            ),
        }

        update_datasource_request = UpdateConfluenceDataSourceRequest(
            **update_request_params
        )
        self.client.datasources.update(datasource_id, update_datasource_request)

        return self.wait_for_indexing(datasource_id)

    def create_jira_datasource(self, **kwargs):
        name = kwargs.get("name", get_random_name())
        create_request_params = {
            "name": name,
            "project_name": kwargs.get("project_name", PROJECT),
            "description": kwargs.get("description", get_random_name()),
            "jql": kwargs.get("jql", CredentialsManager.jira_jql()),
            "project_space_visible": kwargs.get("project_space_visible", False),
            "setting_id": kwargs.get("setting_id"),
        }

        create_datasource_request = JiraDataSourceRequest(**create_request_params)
        self.client.datasources.create(create_datasource_request)
        datasource = wait_for_entity(
            lambda: self.client.datasources.list(per_page=200),
            entity_name=name,
        )

        return self.wait_for_indexing(datasource.id)

    def update_jira_datasource(self, datasource_id, **kwargs):
        datasource = self.get_datasource(datasource_id)

        update_request_params = {
            "name": kwargs.get("name", datasource.name),
            "project_name": datasource.project_name,
            "description": kwargs.get("description", datasource.description),
            "jql": kwargs.get("jql", datasource.jira.jql),
            "full_reindex": kwargs.get("full_reindex", False),
            "skip_reindex": kwargs.get("skip_reindex", True),
            "incremental_reindex": kwargs.get("incremental_reindex", False),
            "setting_id": kwargs.get("setting_id", datasource.setting_id),
            "project_space_visible": kwargs.get(
                "project_space_visible", datasource.shared_with_project
            ),
        }

        update_datasource_request = UpdateJiraDataSourceRequest(**update_request_params)
        self.client.datasources.update(datasource_id, update_datasource_request)

        return self.wait_for_indexing(datasource_id)

    def delete_datasource(self, datasource):
        return self.client.datasources.delete(datasource.id)

    def create_code_analysis_datasource(
        self,
        toolkit_id: str,
        provider_name: str,
        repository_url: str,
        access_token: str,
        branch: str = "main",
        datasource_root: str = ".",
        analyzer: str = None,
        name: str = None,
        description: str = None,
        project_name: str = None,
        project_space_visible: bool = False,
    ) -> DataSource:
        """
        Create a provider-based datasource and wait for it to complete indexing.

        Args:
            toolkit_id: ID of the provider toolkit
            provider_name: Name of the provider
            repository_url: Git repository URL to index
            access_token: Access token for the repository
            branch: Branch (default: "main")
            datasource_root: Root directory to analyze (default: ".")
            analyzer: Code analyzer type (e.g., "Java", "Python")
            name: Datasource name (auto-generated if not provided)
            description: Datasource description (auto-generated if not provided)
            project_name: Project name (defaults to PROJECT)
            project_space_visible: Whether datasource is visible to project (default: False)

        Returns:
            DataSource: The indexed datasource object

        Raises:
            TimeoutError: If datasource indexing doesn't complete within timeout
            ApiError: If datasource creation or indexing fails
        """
        datasource_name = name if name else get_random_name()

        create_request_params = {
            "name": datasource_name,
            "description": description if description else get_random_name(),
            "project_name": project_name if project_name else PROJECT,
            "project_space_visible": project_space_visible,
            "branch": branch,
            "api_url": repository_url,
            "access_token": access_token,
            "datasource_root": datasource_root,
        }

        if analyzer:
            create_request_params["analyzer"] = analyzer

        create_datasource_request = CodeAnalysisDataSourceRequest(
            **create_request_params
        )

        # Create the datasource using the SDK
        self.client.datasources.create_provider_datasource(
            toolkit_id=toolkit_id,
            provider_name=provider_name,
            request=create_datasource_request,
        )

        # Wait for the datasource to appear in the list
        datasource = wait_for_entity(
            lambda: self.client.datasources.list(per_page=200),
            entity_name=datasource_name,
        )

        # Wait for indexing to complete
        return self.wait_for_indexing(datasource.id)

    def create_code_exploration_datasource(
        self,
        toolkit_id: str,
        provider_name: str,
        code_analysis_datasource_ids: list,
        project_name: str = None,
        name: str = None,
        description: str = None,
        project_space_visible: bool = True,
    ) -> DataSource:
        """
        Create a CodeExplorationToolkit datasource that uses existing CodeAnalysisToolkit datasources.

        Args:
            toolkit_id: ID of the CodeExplorationToolkit
            provider_name: Name of the provider
            code_analysis_datasource_ids: List of CodeAnalysisToolkit datasource IDs to use
            project_name: Project name (defaults to PROJECT)
            name: Datasource name (auto-generated if not provided)
            description: Datasource description (auto-generated if not provided)
            project_space_visible: Whether datasource is visible to project (default: True)

        Returns:
            DataSource: The indexed datasource object

        Raises:
            TimeoutError: If datasource indexing doesn't complete within timeout
            ApiError: If datasource creation or indexing fails
        """
        datasource_name = name if name else get_random_name()

        create_request_params = {
            "name": datasource_name,
            "description": description if description else get_random_name(),
            "project_name": project_name if project_name else PROJECT,
            "project_space_visible": project_space_visible,
            "code_analysis_datasource_ids": code_analysis_datasource_ids,
        }

        create_datasource_request = CodeExplorationDataSourceRequest(
            **create_request_params
        )

        # Create the datasource using the SDK
        self.client.datasources.create_provider_datasource(
            toolkit_id=toolkit_id,
            provider_name=provider_name,
            request=create_datasource_request,
        )

        # Wait for the datasource to appear in the list
        datasource = wait_for_entity(
            lambda: self.client.datasources.list(per_page=200),
            entity_name=datasource_name,
        )

        # Wait for indexing to complete
        return self.wait_for_indexing(
            datasource.id, timeout=1200
        )  # Longer timeout for exploration datasource
