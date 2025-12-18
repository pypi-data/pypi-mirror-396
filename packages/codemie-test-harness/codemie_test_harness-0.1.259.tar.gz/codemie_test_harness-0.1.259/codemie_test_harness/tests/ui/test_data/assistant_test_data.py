"""
Test Data for Assistant UI Tests

This module provides test data generation and management for assistant-related UI tests.
Following best practices by separating test data from test logic and providing
reusable data factories for consistent testing.
"""

from dataclasses import dataclass
from typing import Optional, List
from enum import Enum

from codemie_test_harness.tests.utils.base_utils import get_random_name


@dataclass
class AssistantTestData:
    """
    Data class for assistant test data.

    This class encapsulates all the data needed for assistant creation tests,
    providing a clean and type-safe way to manage test data.
    """

    name: str
    description: str
    system_prompt: str
    icon_url: Optional[str] = None
    shared: bool = False


@dataclass
class AssistantMCPConfigTestData:
    """
    Data class for assistant MCP config test data.

    This class encapsulates all the data needed for assistant creation tests,
    providing a clean and type-safe way to manage test data.
    """

    name: str
    description: str
    configuration: str
    token_size_limit: Optional[str] = None
    configuration_type: Optional[bool] = False
    env_var: Optional[str] = None
    mcp_url: Optional[str] = None


class AssistantTestDataFactory:
    """
    Factory class for generating assistant test data.

    This factory provides various methods to create different types of
    assistant test data for different testing scenarios.
    """

    @staticmethod
    def create_minimal_assistant_data() -> AssistantTestData:
        """
        Create minimal assistant data with only required fields.

        This represents the most basic assistant creation scenario
        with minimal required information.

        Returns:
            AssistantTestData: Minimal assistant test data
        """
        return AssistantTestData(
            name=f"QA Test Assistant {get_random_name()}",
            description="Minimal test assistant for QA automation.",
            system_prompt=(
                "You are a test assistant created for QA validation purposes. "
                "Provide helpful and accurate responses to user queries."
            ),
            shared=False,
            icon_url=ICON_URL,
        )

    @staticmethod
    def create_shared_assistant_data() -> AssistantTestData:
        """
        Create shared assistant data for public/shared testing scenarios.

        Returns:
            AssistantTestData: Shared assistant test data
        """
        return AssistantTestData(
            name=f"QA Shared Assistant {get_random_name()}",
            description="Shared QA assistant available to all team members",
            system_prompt=(
                "You are a shared QA assistant available to the entire team. "
                "Provide collaborative testing support, knowledge sharing, and "
                "help maintain consistent quality standards across projects."
            ),
            icon_url=ICON_URL,
            shared=True,
        )

    @staticmethod
    def create_validation_test_data() -> List[AssistantTestData]:
        """
        Create a list of assistant data for validation testing scenarios.

        This includes data for testing various validation scenarios,
        edge cases in form validation, and error handling.

        Returns:
            List[AssistantTestData]: List of validation test data
        """
        return [
            # Empty name scenario
            AssistantTestData(
                name="",
                description="Test description",
                system_prompt="Test prompt",
            ),
            # Long name scenario
            AssistantTestData(
                name="A" * 100,  # Very long name
                description="Test description for long name validation",
                system_prompt="Test prompt for long name scenario",
            ),
            # Empty description scenario
            AssistantTestData(
                name="Test Assistant",
                description="",
                system_prompt="Test prompt",
            ),
            # Empty system prompt scenario
            AssistantTestData(
                name="Test Assistant",
                description="Test description",
                system_prompt="",
            ),
        ]


class AssistantMCPTestDataFactory:
    """
    Factory class for generating assistant test data for creating new MCP server..

    This factory provides various methods to create different types of
    assistant test data for different testing scenarios.
    """

    @staticmethod
    def create_minimal_assistant_mcp_data() -> AssistantMCPConfigTestData:
        """
        Create minimal assistant data with only required fields.

        This represents the most basic assistant creation scenario
        with minimal required information.

        Returns:
            AssistantMCPTestDataFactory: Minimal assistant mcp config test data
        """
        return AssistantMCPConfigTestData(
            name="MCP Test",
            description="MCP for test purposes",
            configuration='{"command": "test"}',
        )


class AssistantValidationErrors(Enum):
    """
    Validation rules and constraints for assistant data.

    This class defines the validation rules that should be applied
    to assistant data during testing.
    """

    NAME_REQUIRED = "Name is required"
    ICON_URL_NOT_VALID = "Icon URL must be a valid URL"
    DESCRIPTION_REQUIRED = "Description is required"
    SYSTEM_PROMPT_REQUIRED = "System instructions are required"
    TEMPERATURE_NOT_VALID = "Temperature must be at most 2"
    TOP_P_NOT_VALID = "Top P must be at most 1"


class AssistantPopUpMessages(Enum):
    """
    Enumerates expected popup notification and toast messages for assistant actions in UI tests.

    This enum class should include all standardized popup/toast messages
    that are expected to appear as a result of user workflow, such as
    success/error messages after saving or updating an assistant,
    deletion confirmations, or integration test results.

    Using this enum in UI tests ensures message checks are maintainable,
    consistent, and robust against typo errors or message changes.
    """

    ASSISTANT_UPDATED_SUCCESS = "Assistant has been updated successfully!"
    ASSISTANT_CREATED_SUCCESS = "Assistant has been created successfully!"
    ASSISTANT_DELETED_SUCCESS = "Assistant has been deleted successfully!"


# ==================== CONVENIENCE FUNCTIONS ====================


def get_minimal_assistant_data() -> AssistantTestData:
    """Convenience function to get minimal assistant data."""
    return AssistantTestDataFactory.create_minimal_assistant_data()


def get_shared_assistant_data() -> AssistantTestData:
    """Convenience function to get shared assistant data."""
    return AssistantTestDataFactory.create_shared_assistant_data()


def get_validation_test_data() -> List[AssistantTestData]:
    """Convenience function to get validation test data."""
    return AssistantTestDataFactory.create_validation_test_data()


def get_minimal_assistant_mcp_config_data() -> AssistantMCPConfigTestData:
    """Convenience function to get minimal assistant mcp config test data."""
    return AssistantMCPTestDataFactory.create_minimal_assistant_mcp_data()


# ==================== TEST DATA CONSTANTS ====================

# Common test values for reuse
COMMON_TEST_PROMPTS = {
    "qa_assistant": (
        "You are a QA testing assistant. Your primary role is to help with "
        "quality assurance tasks, test automation, and ensuring software quality. "
        "Provide detailed and actionable guidance."
    ),
    "general_assistant": (
        "You are a helpful assistant. Provide clear, accurate, and helpful "
        "responses to user queries. Always be polite and professional."
    ),
    "specialist_assistant": (
        "You are a specialist assistant with deep expertise in your domain. "
        "Provide expert-level guidance and detailed technical solutions."
    ),
}

COMMON_TEST_DESCRIPTIONS = {
    "qa_assistant": "QA testing assistant for automation and quality assurance tasks",
    "general_assistant": "General purpose assistant for various tasks and queries",
    "specialist_assistant": "Specialist assistant with domain-specific expertise",
}

COMMON_ICON_URLS = {
    "qa_icon": "https://example.com/qa-assistant-icon.png",
    "general_icon": "https://example.com/general-assistant-icon.png",
    "specialist_icon": "https://example.com/specialist-assistant-icon.png",
}

ICON_URL = "https://raw.githubusercontent.com/epam-gen-ai-run/ai-run-install/main/docs/assets/ai/AQAUiTestGenerator.png"

GENERAL_PROMPT = "You are a helpful integration test assistant"


# ==================== ASSISTANT TOOLS CONSTANTS ====================
class Section(Enum):
    AVAILABLE_TOOLS = "Available Tools"
    EXTERNAL_TOOLS = "External Tools"


class Toolkit(Enum):
    GIT = "Git"
    VCS = "VCS"
    CODEBASE_TOOLS = "Codebase Tools"
    RESEARCH = "Research"
    CLOUD = "Cloud"
    AZURE_DEVOPS_WIKI = "Azure DevOps Wiki"
    AZURE_DEVOPS_WORK_ITEM = "Azure DevOps Work Item"
    AZURE_DEVOPS_TEST_PLAN = "Azure DevOps Test Plan"
    ACCESS_MANAGEMENT = "Access Management"
    PROJECT_MANAGEMENT = "Project Management"
    PLUGIN = "Plugin"
    OPEN_API = "OpenAPI"
    NOTIFICATION = "Notification"
    DATA_MANAGEMENT = "Data Management"
    FILE_MANAGEMENT = "File Management"
    QUALITY_ASSURANCE = "Quality Assurance"
    REPORT_PORTAL = "Report Portal"
    IT_SERVICE_MANAGEMENT = "IT Service Management"


class ExternalToolKit(Enum):
    MCP_SERVERS = "MCP Servers"


class GitTool(Enum):
    CREATE_BRANCH = "Create Branch"
    SET_ACTIVE_BRANCH = "Set Active Branch"
    LIST_BRANCHES_IN_REPO = "List Branches In Repo"
    CREATE_FILE = "Create File"
    UPDATE_FILE = "Update File"
    UPDATE_FILE_DIFF = "Update File Diff"
    DELETE_FILE = "Delete File"
    CREATE_PULL_REQUEST = "Create Pull/Merge request"
    GET_PR_CHANGES = "Get Pull/Merge Request Changes"
    CREATE_PR_CHANGE_COMMENT = "Create Pull/Merge Request Change Comment"


class VcsTool(Enum):
    GITHUB = "Github"
    GITLAB = "Gitlab"


class CodebaseTool(Enum):
    GET_REPOSITORY_FILE_TREE_V2 = "Get Repo Tree with filtering (Experimental)"
    SEARCH_CODE_REPO_V2 = "Search Code with filtering (Experimental)"
    READ_FILES_CONTENT = "Read Files Content"
    READ_FILES_CONTENT_SUMMARY = "Read Files Content With Summary For Large"
    SEARCH_CODE_REPO_BY_PATH = "Search Code Repo By Path"
    SONAR = "Sonar"


class ResearchTool(Enum):
    GOOGLE_SEARCH = "Google Search"
    GOOGLE_PLACES = "Google Places"
    GOOGLE_PLACES_FIND_NEAR = "Google Places Find Near"
    WIKIPEDIA = "Wikipedia"
    TAVILY_SEARCH = "Tavily Search"
    WEB_SCRAPPER = "Web Scraper"


class CloudTool(Enum):
    KUBERNETES = "Kubernetes"
    AWS = "AWS"
    GCP = "GCP"
    AZURE = "Azure"


class AzureDevOpsWikiTool(Enum):
    GET_WIKI = "Get Wiki"
    GET_WIKI_PAGE_BY_PATH = "Get Wiki Page By Path"
    GET_WIKI_PAGE_BY_ID = "Get Wiki Page By ID"
    DELETE_PAGE_BY_PATH = "Delete Wiki Page By Path"
    DELETE_PAGE_BY_ID = "Delete Wiki Page By ID"
    MODIFY_WIKI_PAGE = "Modify Wiki Page"
    RENAME_WIKI_PAGE = "Rename Wiki Page"


class AzureDevOpsWorkItemTool(Enum):
    SEARCH_WORK_ITEMS = "Search Work Items"
    CREATE_WORK_ITEM = "Create Work Item"
    UPDATE_WORK_ITEM = "Update Work Item"
    GET_WORK_ITEM = "Get Work Item"
    LINK_WORK_ITEMS = "Link Work Items"
    GET_RELATION_TYPES = "Get Relation Types"
    GET_COMMENTS = "Get Comments"


class AzureDevOpsTestPlanTool(Enum):
    CREATE_TEST_PLAN = "Create Test Plan"
    DELETE_TEST_PLAN = "Delete Test Plan"
    GET_TEST_PLAN = "Get Test Plan"
    CREATE_TEST_SUITE = "Create Test Suite"
    DELETE_TEST_SUITE = "Delete Test Suite"
    GET_TEST_SUITE = "Get Test Suite"
    ADD_TEST_CASE = "Add Test Case"
    GET_TEST_CASE = "Get Test Case"
    GET_TEST_CASES = "Get Test Cases"


class AccessManagementTool(Enum):
    KEYCLOAK = "Keycloak"


class ProjectManagementTool(Enum):
    GENERIC_JIRA = "Generic Jira"
    GENERIC_CONFLUENCE = "Generic Confluence"


class PluginTool(Enum):
    PLUGIN = "Plugin"


class OpenAPITool(Enum):
    INVOKE_EXTERNAL_API = "Invoke external API"
    GET_OPEN_API_SPEC = "Get Open API spec"


class NotificationTool(Enum):
    EMAIL = "Email"
    TELEGRAM = "Telegram"


class DataManagementTool(Enum):
    ELASTIC = "Search Elastic index"
    SQL = "SQL"


class FileManagementTool(Enum):
    READ_FILE = "Read file"
    WRITE_FILE = "Write file"
    LIST_DIRECTORY = "List directory"
    RUN_COMMAND_LINE = "Run command line"
    CODE_INTERPRETER = "Code Interpreter"
    GENERATE_IMAGE_TOOL = "Generate image"
    DIFF_UPDATE_FILE_TOOL = "Read Generate Update File (diff)"
    STR_REPLACE_EDITOR = "Filesystem Editor Tool"


class QualityAssuranceTool(Enum):
    ZEPHYR_SCALE = "Zephyr Scale"
    ZEPHYR_SQUAD = "Zephyr Squad"


class ITServiceManagementTool(Enum):
    SERVICENOW_TABLE_API = "ServiceNow Table API"


class MCPServersTool(Enum):
    ADD_MCP_SERVER = " Add MCP Server "


TOOLKIT_TOOLS = {
    Section.AVAILABLE_TOOLS: {
        Toolkit.GIT: [
            GitTool.CREATE_BRANCH,
            GitTool.SET_ACTIVE_BRANCH,
            GitTool.LIST_BRANCHES_IN_REPO,
            GitTool.CREATE_FILE,
            GitTool.UPDATE_FILE,
            GitTool.UPDATE_FILE_DIFF,
            GitTool.DELETE_FILE,
            GitTool.CREATE_PULL_REQUEST,
            GitTool.GET_PR_CHANGES,
            GitTool.CREATE_PR_CHANGE_COMMENT,
        ],
        Toolkit.VCS: [
            VcsTool.GITHUB,
            VcsTool.GITLAB,
        ],
        Toolkit.CODEBASE_TOOLS: [
            CodebaseTool.GET_REPOSITORY_FILE_TREE_V2,
            CodebaseTool.SEARCH_CODE_REPO_V2,
            CodebaseTool.READ_FILES_CONTENT,
            CodebaseTool.READ_FILES_CONTENT_SUMMARY,
            CodebaseTool.SEARCH_CODE_REPO_BY_PATH,
            CodebaseTool.SONAR,
        ],
        Toolkit.RESEARCH: [
            ResearchTool.GOOGLE_SEARCH,
            ResearchTool.GOOGLE_PLACES,
            ResearchTool.GOOGLE_PLACES_FIND_NEAR,
            ResearchTool.WIKIPEDIA,
            ResearchTool.TAVILY_SEARCH,
            ResearchTool.WEB_SCRAPPER,
        ],
        Toolkit.CLOUD: [
            CloudTool.KUBERNETES,
            CloudTool.AWS,
            CloudTool.GCP,
            CloudTool.AZURE,
        ],
        Toolkit.AZURE_DEVOPS_WIKI: [
            AzureDevOpsWikiTool.GET_WIKI,
            AzureDevOpsWikiTool.GET_WIKI_PAGE_BY_PATH,
            AzureDevOpsWikiTool.GET_WIKI_PAGE_BY_ID,
            AzureDevOpsWikiTool.DELETE_PAGE_BY_PATH,
            AzureDevOpsWikiTool.DELETE_PAGE_BY_ID,
            AzureDevOpsWikiTool.MODIFY_WIKI_PAGE,
            AzureDevOpsWikiTool.RENAME_WIKI_PAGE,
        ],
        Toolkit.AZURE_DEVOPS_WORK_ITEM: [
            AzureDevOpsWorkItemTool.SEARCH_WORK_ITEMS,
            AzureDevOpsWorkItemTool.CREATE_WORK_ITEM,
            AzureDevOpsWorkItemTool.UPDATE_WORK_ITEM,
            AzureDevOpsWorkItemTool.GET_WORK_ITEM,
            AzureDevOpsWorkItemTool.LINK_WORK_ITEMS,
            AzureDevOpsWorkItemTool.GET_RELATION_TYPES,
            AzureDevOpsWorkItemTool.GET_COMMENTS,
        ],
        Toolkit.AZURE_DEVOPS_TEST_PLAN: [
            AzureDevOpsTestPlanTool.CREATE_TEST_PLAN,
            AzureDevOpsTestPlanTool.DELETE_TEST_PLAN,
            AzureDevOpsTestPlanTool.GET_TEST_PLAN,
            AzureDevOpsTestPlanTool.CREATE_TEST_SUITE,
            AzureDevOpsTestPlanTool.DELETE_TEST_SUITE,
            AzureDevOpsTestPlanTool.GET_TEST_SUITE,
            AzureDevOpsTestPlanTool.ADD_TEST_CASE,
            AzureDevOpsTestPlanTool.GET_TEST_CASE,
            AzureDevOpsTestPlanTool.GET_TEST_CASES,
        ],
        Toolkit.ACCESS_MANAGEMENT: [
            AccessManagementTool.KEYCLOAK,
        ],
        Toolkit.PROJECT_MANAGEMENT: [
            ProjectManagementTool.GENERIC_JIRA,
            ProjectManagementTool.GENERIC_CONFLUENCE,
        ],
        Toolkit.PLUGIN: [
            PluginTool.PLUGIN,
        ],
        Toolkit.OPEN_API: [
            OpenAPITool.INVOKE_EXTERNAL_API,
            OpenAPITool.GET_OPEN_API_SPEC,
        ],
        Toolkit.NOTIFICATION: [
            NotificationTool.EMAIL,
            NotificationTool.TELEGRAM,
        ],
        Toolkit.DATA_MANAGEMENT: [
            DataManagementTool.ELASTIC,
            DataManagementTool.SQL,
        ],
        Toolkit.FILE_MANAGEMENT: [
            FileManagementTool.READ_FILE,
            FileManagementTool.WRITE_FILE,
            FileManagementTool.LIST_DIRECTORY,
            FileManagementTool.RUN_COMMAND_LINE,
            FileManagementTool.CODE_INTERPRETER,
            FileManagementTool.GENERATE_IMAGE_TOOL,
            FileManagementTool.DIFF_UPDATE_FILE_TOOL,
            FileManagementTool.STR_REPLACE_EDITOR,
        ],
        Toolkit.QUALITY_ASSURANCE: [
            QualityAssuranceTool.ZEPHYR_SCALE,
            QualityAssuranceTool.ZEPHYR_SQUAD,
        ],
        Toolkit.IT_SERVICE_MANAGEMENT: [
            ITServiceManagementTool.SERVICENOW_TABLE_API,
        ],
    },
    Section.EXTERNAL_TOOLS: {
        ExternalToolKit.MCP_SERVERS: [
            MCPServersTool.ADD_MCP_SERVER,
        ]
    },
}
