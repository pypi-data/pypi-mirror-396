"""Test data for vendor service endpoint tests."""

import pytest
from codemie_sdk.models.vendor_assistant import VendorType
from codemie_sdk.models.integration import CredentialTypes

from codemie_test_harness.tests.utils.credentials_manager import CredentialsManager


# Test data for vendor endpoint tests
# Extensible for AWS Bedrock, Azure AI, and GCP Vertex AI
vendor_endpoint_test_data = [
    pytest.param(
        VendorType.AWS,
        CredentialTypes.AWS,
        CredentialsManager.aws_credentials(),
        marks=[pytest.mark.aws, pytest.mark.bedrock],
        id="AWS_Bedrock",
    ),
    # Future: Azure AI endpoints
    # pytest.param(
    #     VendorType.AZURE,
    #     CredentialTypes.AZURE,
    #     CredentialsManager.azure_credentials(),
    #     marks=[pytest.mark.azure],
    #     id="Azure_AI",
    # ),
    # Future: GCP Vertex AI endpoints
    # pytest.param(
    #     VendorType.GCP,
    #     CredentialTypes.GCP,
    #     CredentialsManager.gcp_credentials(),
    #     marks=[pytest.mark.gcp],
    #     id="GCP_Vertex_AI",
    # ),
]
