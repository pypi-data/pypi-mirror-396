"""Test data for vendor knowledge base integration tests."""

import pytest
from codemie_sdk.models.vendor_assistant import VendorType
from codemie_sdk.models.integration import CredentialTypes

from codemie_test_harness.tests.utils.credentials_manager import CredentialsManager


# Test data for vendor knowledge base integration tests
# Extensible for AWS Bedrock, Azure AI, and GCP Vertex AI
vendor_knowledge_base_test_data = [
    pytest.param(
        VendorType.AWS,
        CredentialTypes.AWS,
        CredentialsManager.aws_credentials(),
        "Tell me about filtering by language",
        "Filtering by language allows you to select books based on your preferred language. "
        "According to the knowledge base, the available language filter options include:\n\n"
        "- English\n- Spanish\n- French\n- German\n\n"
        "You can use these filters to view only the books that are available in the selected language.",
        marks=[pytest.mark.aws, pytest.mark.bedrock],
        id="AWS_Bedrock",
    ),
    # Future: Azure AI knowledge bases
    # pytest.param(
    #     VendorType.AZURE,
    #     CredentialTypes.AZURE,
    #     CredentialsManager.azure_credentials(),
    #     "Tell me about filtering by language",
    #     "Filtering by language allows you to select books based on your preferred language.",
    #     marks=[pytest.mark.azure],
    #     id="Azure_AI",
    # ),
    # Future: GCP Vertex AI knowledge bases
    # pytest.param(
    #     VendorType.GCP,
    #     CredentialTypes.GCP,
    #     CredentialsManager.gcp_credentials(),
    #     "Tell me about filtering by language",
    #     "Filtering by language allows you to select books based on your preferred language.",
    #     marks=[pytest.mark.gcp],
    #     id="GCP_Vertex_AI",
    # ),
]

# Test data for vendor assistant with KB integration tests
vendor_assistant_with_kb_test_data = [
    pytest.param(
        VendorType.AWS,
        CredentialTypes.AWS,
        CredentialsManager.aws_credentials(),
        "codemie-autotests-with-kb",
        "Tell me about filtering by language",
        "Filtering by language allows you to select books based on your preferred language. "
        "According to the knowledge base, the available language filter options include:\n\n"
        "- English\n- Spanish\n- French\n- German\n\n"
        "You can use these filters to view only the books that are available in the selected language.",
        marks=[pytest.mark.aws, pytest.mark.bedrock],
        id="AWS_Bedrock",
    ),
    # Future: Azure AI assistants with KB
    # pytest.param(
    #     VendorType.AZURE,
    #     CredentialTypes.AZURE,
    #     CredentialsManager.azure_credentials(),
    #     "codemie-autotests-with-kb",
    #     "Tell me about filtering by language",
    #     "Filtering by language allows you to select books based on your preferred language.",
    #     marks=[pytest.mark.azure],
    #     id="Azure_AI",
    # ),
    # Future: GCP Vertex AI assistants with KB
    # pytest.param(
    #     VendorType.GCP,
    #     CredentialTypes.GCP,
    #     CredentialsManager.gcp_credentials(),
    #     "codemie-autotests-with-kb",
    #     "Tell me about filtering by language",
    #     "Filtering by language allows you to select books based on your preferred language.",
    #     marks=[pytest.mark.gcp],
    #     id="GCP_Vertex_AI",
    # ),
]
