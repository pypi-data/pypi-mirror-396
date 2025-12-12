"""
Questra Automation - Python Client for Automation GraphQL API.

Provides a type-safe interface to the Questra Automation service with automatic
OAuth2 token management through QuestraAuthentication.

Available Clients:
    - QuestraAutomation: Asynchroner Client (empfohlen für FastAPI, async Contexts)

Example (Async):
    ```python
    from questra_authentication import QuestraAuthentication
    from questra_automation import QuestraAutomation, ExecuteInput, ExecutionInitiator

    # Create QuestraAuthentication
    auth = QuestraAuthentication(
        url="https://authentik.dev.example.com",
        username="ServiceUser",
        password="secret_password",
        oidc_discovery_paths=["/application/o/automation"],
    )

    # Initialize QuestraAutomation (async)
    async with QuestraAutomation(
        base_url="https://automation.dev.example.com/graphql",
        auth_client=auth,
    ) as client:
        # Query workspaces
        workspaces = await client.list_workspaces(first=10)
        for workspace in workspaces.workspaces.nodes:
            print(f"Workspace: {workspace.name}")

        # Execute an automation
        result = await client.execute_automation(
            input=ExecuteInput(
                workspace_name="my-workspace",
                automation_path="scripts/example.py",
                initiator_type=ExecutionInitiator.MANUAL,
            )
        )
    ```

Example (Sync):
    ```python

        base_url="https://automation.dev.example.com/graphql",
        auth_client=auth,
    ) as client:
        # Query workspaces (ohne await!)
        workspaces = client.list_workspaces(first=10)
        for workspace in workspaces.workspaces.nodes:
            print(f"Workspace: {workspace.name}")
    ```
"""

import os
import sys

from loguru import logger

logger.remove()

LOG_LEVEL = os.getenv("QUESTRA_AUTOMATION_LOG_LEVEL", "WARNING")
LOG_FORMAT = os.getenv(
    "QUESTRA_AUTOMATION_LOG_FORMAT",
    (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level> | "
        "{extra}{exception}"
    ),
)

_ = logger.add(
    sys.stdout,
    format=LOG_FORMAT,
    level=LOG_LEVEL,
    colorize=True,
    backtrace=True,
    diagnose=True,
)

LOG_FILE = os.getenv("QUESTRA_AUTOMATION_LOG_FILE")
if LOG_FILE:
    _ = logger.add(
        LOG_FILE,
        format=LOG_FORMAT,
        level="DEBUG",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        enqueue=True,
    )

logger.debug("Questra Automation logger initialized")

# Main clients
# Re-export commonly used types from generated client
from ._generated.graphql_client import (  # Input types; Exceptions; Filter inputs; Sort inputs
    ApplyPolicy,
    AutomationBuildStatusViewData,
    AutomationClientGenerated,
    AutomationExecutionDomainStatusViewData,
    AutomationExecutionStatusViewData,
    AutomationExecutionViewFilterInput,
    AutomationExecutionViewSortInput,
    AutomationInitiatorTypeViewData,
    AutomationViewFilterInput,
    AutomationViewSortInput,
    CreateRepositoryInput,
    CreateScheduleInput,
    CreateWorkspaceInput,
    DeleteRepositoryInput,
    DeleteScheduleInput,
    DeleteWorkspaceInput,
    ErrorCodeViewFilterInput,
    ErrorCodeViewSortInput,
    ExecuteArgumentInput,
    ExecuteInput,
    ExecutionInitiator,
    GraphQLClientError,
    GraphQLClientGraphQLError,
    GraphQLClientGraphQLMultiError,
    GraphQLClientHttpError,
    GraphQLClientInvalidResponseError,
    RenewRepositorySshKeyInput,
    RepositoryAuthenticationMethod,
    RepositoryViewFilterInput,
    RepositoryViewSortInput,
    ScheduleArgumentInput,
    ScheduleViewFilterInput,
    ScheduleViewSortInput,
    SynchronizeWorkspaceInput,
    UpdateRepositoryInput,
    UpdateScheduleInput,
    UpdateWorkspaceInput,
    WorkspaceViewFilterInput,
    WorkspaceViewSortInput,
)
from .client import QuestraAutomation

__version__ = "0.1.0"

__all__ = [
    # Main clients
    "QuestraAutomation",
    # Generated client (for advanced usage)
    "AutomationClientGenerated",
    # Enums
    "ExecutionInitiator",
    "ApplyPolicy",
    "AutomationBuildStatusViewData",
    "AutomationExecutionDomainStatusViewData",
    "AutomationExecutionStatusViewData",
    "AutomationInitiatorTypeViewData",
    "RepositoryAuthenticationMethod",
    # Input types
    "ExecuteInput",
    "ExecuteArgumentInput",
    "CreateRepositoryInput",
    "UpdateRepositoryInput",
    "DeleteRepositoryInput",
    "RenewRepositorySshKeyInput",
    "CreateWorkspaceInput",
    "UpdateWorkspaceInput",
    "DeleteWorkspaceInput",
    "SynchronizeWorkspaceInput",
    "CreateScheduleInput",
    "UpdateScheduleInput",
    "DeleteScheduleInput",
    "ScheduleArgumentInput",
    # Filter inputs
    "WorkspaceViewFilterInput",
    "AutomationViewFilterInput",
    "AutomationExecutionViewFilterInput",
    "RepositoryViewFilterInput",
    "ScheduleViewFilterInput",
    "ErrorCodeViewFilterInput",
    # Sort inputs
    "WorkspaceViewSortInput",
    "AutomationViewSortInput",
    "AutomationExecutionViewSortInput",
    "RepositoryViewSortInput",
    "ScheduleViewSortInput",
    "ErrorCodeViewSortInput",
    # Exceptions
    "GraphQLClientError",
    "GraphQLClientGraphQLError",
    "GraphQLClientGraphQLMultiError",
    "GraphQLClientHttpError",
    "GraphQLClientInvalidResponseError",
]
