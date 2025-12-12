"""Global pytest fixtures for Questra Automation tests."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Path to JSON fixtures
FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_json_response(filename: str) -> dict:
    """
    Load a GraphQL response from a JSON file.

    Args:
        filename: Name of the JSON file (e.g., "workspaces_response.json")

    Returns:
        dict: Deserialized GraphQL response
    """
    filepath = FIXTURES_DIR / filename
    with filepath.open(encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def mock_auth_client():
    """Mock for QuestraAuthentication client."""
    mock = MagicMock()
    mock.is_authenticated.return_value = True
    mock.get_access_token.return_value = "mock_token_12345"
    return mock


@pytest.fixture
def mock_graphql_execute():
    """Mock for GraphQL execute function."""
    return MagicMock()


# ========== Query Fixtures ==========


@pytest.fixture
def workspaces_response():
    """GraphQL response for workspaces query."""
    return load_json_response("workspaces_response.json")


@pytest.fixture
def repositories_response():
    """GraphQL response for repositories query."""
    return load_json_response("repositories_response.json")


@pytest.fixture
def automations_response():
    """GraphQL response for automations query."""
    return load_json_response("automations_response.json")


@pytest.fixture
def executions_response():
    """GraphQL response for executions query."""
    return load_json_response("executions_response.json")


@pytest.fixture
def schedules_response():
    """GraphQL response for schedules query."""
    return load_json_response("schedules_response.json")


@pytest.fixture
def scheduled_executions_response():
    """GraphQL response for scheduled executions query."""
    return load_json_response("scheduled_executions_response.json")


@pytest.fixture
def error_codes_response():
    """GraphQL response for error codes query."""
    return load_json_response("error_codes_response.json")


@pytest.fixture
def service_info_response():
    """GraphQL response for automation service info query."""
    return load_json_response("service_info_response.json")


# ========== Mutation Fixtures ==========


@pytest.fixture
def execute_success_response():
    """GraphQL response for execute mutation (success)."""
    return load_json_response("execute_success.json")


@pytest.fixture
def create_repository_success_response():
    """GraphQL response for create repository mutation (success)."""
    return load_json_response("create_repository_success.json")


@pytest.fixture
def update_repository_success_response():
    """GraphQL response for update repository mutation (success)."""
    return load_json_response("update_repository_success.json")


@pytest.fixture
def delete_repository_success_response():
    """GraphQL response for delete repository mutation (success)."""
    return load_json_response("delete_repository_success.json")


@pytest.fixture
def renew_ssh_key_success_response():
    """GraphQL response for renew SSH key mutation (success)."""
    return load_json_response("renew_ssh_key_success.json")


@pytest.fixture
def create_workspace_success_response():
    """GraphQL response for create workspace mutation (success)."""
    return load_json_response("create_workspace_success.json")


@pytest.fixture
def update_workspace_success_response():
    """GraphQL response for update workspace mutation (success)."""
    return load_json_response("update_workspace_success.json")


@pytest.fixture
def delete_workspace_success_response():
    """GraphQL response for delete workspace mutation (success)."""
    return load_json_response("delete_workspace_success.json")


@pytest.fixture
def synchronize_workspace_success_response():
    """GraphQL response for synchronize workspace mutation (success)."""
    return load_json_response("synchronize_workspace_success.json")


@pytest.fixture
def create_schedule_success_response():
    """GraphQL response for create schedule mutation (success)."""
    return load_json_response("create_schedule_success.json")


@pytest.fixture
def update_schedule_success_response():
    """GraphQL response for update schedule mutation (success)."""
    return load_json_response("update_schedule_success.json")


@pytest.fixture
def delete_schedule_success_response():
    """GraphQL response for delete schedule mutation (success)."""
    return load_json_response("delete_schedule_success.json")
