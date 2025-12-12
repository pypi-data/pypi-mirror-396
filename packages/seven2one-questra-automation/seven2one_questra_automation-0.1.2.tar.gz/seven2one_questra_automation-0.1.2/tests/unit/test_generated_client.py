"""Unit tests for generated GraphQL client (AutomationClientGenerated)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest

from questra_automation import (
    AutomationBuildStatusViewData,
    AutomationClientGenerated,
    AutomationExecutionStatusViewData,
    RepositoryAuthenticationMethod,
)


@pytest.mark.unit
class TestGeneratedClientWorkspaces:
    """Tests für workspaces Query."""

    @pytest.mark.asyncio
    async def test_workspaces_query(self, workspaces_response):
        """Test workspaces query execution."""
        # Mock HTTP client
        mock_http_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.is_success = True
        mock_response.json.return_value = workspaces_response
        mock_http_client.post.return_value = mock_response

        # Create client with mocked HTTP client
        client = AutomationClientGenerated(
            url="https://automation.example.com/graphql",
            http_client=mock_http_client,
        )

        # Execute query
        result = await client.workspaces(first=10)

        # Verify response structure
        assert result.workspaces is not None
        assert result.workspaces.nodes is not None
        assert result.workspaces.total_count == 3
        assert len(result.workspaces.nodes) == 3

        # Verify first workspace
        ws1 = result.workspaces.nodes[0]
        assert ws1.name == "dev-workspace"
        assert ws1.repository_name == "main-repo"
        assert ws1.build_status == AutomationBuildStatusViewData.SUCCEEDED
        assert len(ws1.build_errors) == 0

        # Verify second workspace (running)
        ws2 = result.workspaces.nodes[1]
        assert ws2.name == "staging-workspace"
        assert ws2.build_status == AutomationBuildStatusViewData.RUNNING
        assert ws2.build_finished_at is None

        # Verify third workspace (failed with errors)
        ws3 = result.workspaces.nodes[2]
        assert ws3.name == "failed-workspace"
        assert ws3.build_status == AutomationBuildStatusViewData.FAILED
        assert len(ws3.build_errors) == 1
        assert ws3.build_errors[0].code == "BUILD_ERROR_001"


@pytest.mark.unit
class TestGeneratedClientRepositories:
    """Tests für repositories Query."""

    @pytest.mark.asyncio
    async def test_repositories_query(self, repositories_response):
        """Test repositories query execution."""
        mock_http_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.is_success = True
        mock_response.json.return_value = repositories_response
        mock_http_client.post.return_value = mock_response

        client = AutomationClientGenerated(
            url="https://automation.example.com/graphql",
            http_client=mock_http_client,
        )

        result = await client.repositories(first=10)

        assert result.repositories is not None
        assert result.repositories.nodes is not None
        assert result.repositories.total_count == 2
        assert len(result.repositories.nodes) == 2

        # First repository (username/password)
        repo1 = result.repositories.nodes[0]
        assert repo1.name == "main-repo"
        assert repo1.url == "https://github.com/example/main-repo.git"
        assert (
            repo1.authentication_method
            == RepositoryAuthenticationMethod.USERNAME_PASSWORD
        )
        assert repo1.username == "deploy-user"
        assert repo1.ssh_public_key is None

        # Second repository (SSH key)
        repo2 = result.repositories.nodes[1]
        assert repo2.name == "test-repo"
        assert repo2.authentication_method == RepositoryAuthenticationMethod.SSH_KEY
        assert repo2.username is None
        assert repo2.ssh_public_key is not None


@pytest.mark.unit
class TestGeneratedClientAutomations:
    """Tests für automations Query."""

    @pytest.mark.asyncio
    async def test_automations_query(self, automations_response):
        """Test automations query execution."""
        mock_http_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.is_success = True
        mock_response.json.return_value = automations_response
        mock_http_client.post.return_value = mock_response

        client = AutomationClientGenerated(
            url="https://automation.example.com/graphql",
            http_client=mock_http_client,
        )

        result = await client.automations(first=10)

        assert result.automations is not None
        assert result.automations.nodes is not None
        assert result.automations.total_count == 2
        assert len(result.automations.nodes) == 2

        # First automation (with arguments)
        auto1 = result.automations.nodes[0]
        assert auto1.workspace_name == "dev-workspace"
        assert auto1.path == "scripts/daily_sync.py"
        assert auto1.allow_parallel_execution is False
        assert len(auto1.argument_definitions) == 3

        # Check argument definitions
        arg1 = auto1.argument_definitions[0]
        assert arg1.name == "source"
        assert arg1.mandatory is True

        # Second automation (without arguments)
        auto2 = result.automations.nodes[1]
        assert auto2.path == "scripts/cleanup.py"
        assert auto2.allow_parallel_execution is True
        assert len(auto2.argument_definitions) == 0


@pytest.mark.unit
class TestGeneratedClientExecutions:
    """Tests für executions Query."""

    @pytest.mark.asyncio
    async def test_executions_query(self, executions_response):
        """Test executions query execution."""
        mock_http_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.is_success = True
        mock_response.json.return_value = executions_response
        mock_http_client.post.return_value = mock_response

        client = AutomationClientGenerated(
            url="https://automation.example.com/graphql",
            http_client=mock_http_client,
        )

        result = await client.executions(first=10)

        assert result.executions is not None
        assert result.executions.nodes is not None
        assert result.executions.total_count == 3
        assert len(result.executions.nodes) == 3

        # First execution (succeeded, manual)
        exec1 = result.executions.nodes[0]
        assert isinstance(exec1.id, UUID)
        assert str(exec1.id) == "12345678-1234-1234-1234-123456789012"
        assert exec1.workspace_name == "dev-workspace"
        assert exec1.automation_path == "scripts/daily_sync.py"
        assert exec1.status == AutomationExecutionStatusViewData.SUCCEEDED
        assert exec1.finished_at is not None

        # Second execution (running)
        exec2 = result.executions.nodes[1]
        assert exec2.status == AutomationExecutionStatusViewData.RUNNING
        assert exec2.finished_at is None

        # Third execution (failed)
        exec3 = result.executions.nodes[2]
        assert exec3.status == AutomationExecutionStatusViewData.FAILED
        assert exec3.output is not None


@pytest.mark.unit
class TestGeneratedClientSchedules:
    """Tests für schedules Query."""

    @pytest.mark.asyncio
    async def test_schedules_query(self, schedules_response):
        """Test schedules query execution."""
        mock_http_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.is_success = True
        mock_response.json.return_value = schedules_response
        mock_http_client.post.return_value = mock_response

        client = AutomationClientGenerated(
            url="https://automation.example.com/graphql",
            http_client=mock_http_client,
        )

        result = await client.schedules(first=10)

        assert result.schedules is not None
        assert result.schedules.nodes is not None
        assert result.schedules.total_count == 2
        assert len(result.schedules.nodes) == 2

        # First schedule (active)
        sched1 = result.schedules.nodes[0]
        assert sched1.automation_path == "scripts/daily_sync.py"
        assert sched1.name == "daily-sync-schedule"
        assert sched1.cron == "0 2 * * *"
        assert sched1.active is True
        assert len(sched1.argument_instances) == 2

        # Second schedule (inactive)
        sched2 = result.schedules.nodes[1]
        assert sched2.name == "weekly-cleanup"
        assert sched2.active is False


@pytest.mark.unit
class TestGeneratedClientErrorCodes:
    """Tests für errorCodes Query."""

    @pytest.mark.asyncio
    async def test_error_codes_query(self, error_codes_response):
        """Test error codes query execution."""
        mock_http_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.is_success = True
        mock_response.json.return_value = error_codes_response
        mock_http_client.post.return_value = mock_response

        client = AutomationClientGenerated(
            url="https://automation.example.com/graphql",
            http_client=mock_http_client,
        )

        result = await client.error_codes(first=10)

        assert result.error_codes is not None
        assert result.error_codes.nodes is not None
        assert result.error_codes.total_count == 10
        assert len(result.error_codes.nodes) == 10

        # First error code
        err1 = result.error_codes.nodes[0]
        assert err1.code == "AUTOMATION_ARGUMENT_DUPLICATE"
        assert "Duplicate argument" in err1.message_template
        assert "ArgumentName" in err1.parameters


@pytest.mark.unit
class TestGeneratedClientServiceInfo:
    """Tests für automationServiceInfo Query."""

    @pytest.mark.asyncio
    async def test_service_info_query(self, service_info_response):
        """Test service info query execution."""
        mock_http_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.is_success = True
        mock_response.json.return_value = service_info_response
        mock_http_client.post.return_value = mock_response

        client = AutomationClientGenerated(
            url="https://automation.example.com/graphql",
            http_client=mock_http_client,
        )

        result = await client.automation_service_info()

        assert result.automation_service_info is not None
        assert result.automation_service_info.name == "Questra Automation Service"
        assert result.automation_service_info.version == "1.2.3"
        assert "1.2.3+build." in result.automation_service_info.informational_version


@pytest.mark.unit
class TestGeneratedClientMutations:
    """Tests für Mutations."""

    @pytest.mark.asyncio
    async def test_execute_automation_mutation(self, execute_success_response):
        """Test execute automation mutation."""
        mock_http_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.is_success = True
        mock_response.json.return_value = execute_success_response
        mock_http_client.post.return_value = mock_response

        client = AutomationClientGenerated(
            url="https://automation.example.com/graphql",
            http_client=mock_http_client,
        )

        from questra_automation import (
            ExecuteArgumentInput,
            ExecuteInput,
            ExecutionInitiator,
        )

        result = await client.execute_automation(
            input=ExecuteInput(
                workspaceName="dev-workspace",
                automationPath="scripts/daily_sync.py",
                initiatorType=ExecutionInitiator.MANUAL,
                arguments=[
                    ExecuteArgumentInput(name="source", value="system-a"),
                ],
            )
        )

        assert result.execute is not None
        assert isinstance(result.execute.id, UUID)
        assert str(result.execute.id) == "12345678-1234-1234-1234-123456789012"

    @pytest.mark.asyncio
    async def test_create_workspace_mutation(self, create_workspace_success_response):
        """Test create workspace mutation."""
        mock_http_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.is_success = True
        mock_response.json.return_value = create_workspace_success_response
        mock_http_client.post.return_value = mock_response

        client = AutomationClientGenerated(
            url="https://automation.example.com/graphql",
            http_client=mock_http_client,
        )

        from questra_automation import CreateWorkspaceInput
        from questra_automation._generated.graphql_client.input_types import BranchInput

        result = await client.create_workspace(
            input=CreateWorkspaceInput(
                repositoryName="main-repo",
                name="new-workspace",
                branch=BranchInput(name="main", commit="abc123"),
            )
        )

        assert result.create_workspace is not None
        assert result.create_workspace.name == "new-workspace"
