import pytest

from codemie_test_harness.tests import CredentialsManager


@pytest.fixture(scope="module")
def code_analysis_toolkit(providers_utils):
    """Get existing CodeAnalysisToolkit from providers."""
    # Get existing providers
    providers_response = providers_utils.list_providers()
    providers_data = providers_response.json()

    # Find provider with CodeAnalysisToolkit
    for provider in providers_data:
        provided_toolkits = provider.get("provided_toolkits", [])
        for toolkit in provided_toolkits:
            if "CodeAnalysisToolkit" == toolkit["name"]:
                return {"toolkit": toolkit, "provider_name": provider["name"]}

    raise ValueError("CodeAnalysisToolkit not found in any provider")


@pytest.fixture(scope="module")
def code_exploration_toolkit(providers_utils):
    """Get existing CodeExplorationToolkit from providers."""
    # Get existing providers
    providers_response = providers_utils.list_providers()
    providers_data = providers_response.json()

    # Find provider with CodeExplorationToolkit
    for provider in providers_data:
        provided_toolkits = provider.get("provided_toolkits", [])
        for toolkit in provided_toolkits:
            if "CodeExplorationToolkit" == toolkit["name"]:
                return {"toolkit": toolkit, "provider_name": provider["name"]}

    raise ValueError("CodeExplorationToolkit not found in any provider")


@pytest.fixture(scope="module")
def code_analysis_datasource(code_analysis_toolkit, datasource_utils):
    """Create and index a CodeAnalysisToolkit datasource."""
    toolkit_id = code_analysis_toolkit["toolkit"]["toolkit_id"]
    provider_name = code_analysis_toolkit["provider_name"]

    # Get GitLab credentials
    gitlab_project = CredentialsManager.get_parameter("GITLAB_PROJECT")
    gitlab_token = CredentialsManager.get_parameter("GITLAB_TOKEN")

    # Create provider datasource
    datasource = datasource_utils.create_code_analysis_datasource(
        toolkit_id=toolkit_id,
        provider_name=provider_name,
        repository_url=gitlab_project,
        access_token=gitlab_token,
        branch="main",
        datasource_root=".",
        analyzer="Java",
    )

    yield datasource

    # Cleanup: delete the datasource
    datasource_utils.delete_datasource(datasource)


@pytest.fixture(scope="module")
def code_exploration_datasource(
    code_exploration_toolkit, code_analysis_datasource, datasource_utils
):
    """Create and index a CodeExplorationToolkit datasource."""
    toolkit_id = code_exploration_toolkit["toolkit"]["toolkit_id"]
    provider_name = code_exploration_toolkit["provider_name"]

    # Create CodeExplorationToolkit datasource
    datasource = datasource_utils.create_code_exploration_datasource(
        toolkit_id=toolkit_id,
        provider_name=provider_name,
        code_analysis_datasource_ids=[code_analysis_datasource.id],
    )

    yield datasource

    # Cleanup: delete the datasource
    datasource_utils.delete_datasource(datasource)
