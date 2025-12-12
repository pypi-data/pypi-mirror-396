"""Example usage of the Questra Automation client."""

import asyncio
from datetime import datetime, timedelta

from questra_authentication import QuestraAuthentication

from questra_automation import (
    CreateRepositoryInput,
    CreateScheduleInput,
    CreateWorkspaceInput,
    DeleteRepositoryInput,
    DeleteScheduleInput,
    DeleteWorkspaceInput,
    ExecuteArgumentInput,
    ExecuteInput,
    ExecutionInitiator,
    QuestraAutomation,
    RenewRepositorySshKeyInput,
    RepositoryAuthenticationMethod,
    ScheduleArgumentInput,
    SynchronizeWorkspaceInput,
    UpdateScheduleInput,
)
from questra_automation._generated.graphql_client.input_types import BranchInput


async def main():
    """Run example operations."""
    # Create QuestraAuthentication
    auth_client = QuestraAuthentication(
        url="https://authentik.dev.example.com",
        username="ServiceUser",
        password="secret_password",
        oidc_discovery_paths=["/application/o/automation"],
    )

    # Initialize QuestraAutomation
    async with QuestraAutomation(
        base_url="https://automation.dev.example.com/graphql",
        auth_client=auth_client,
    ) as client:
        # ===== Query Examples =====

        # Get service info
        service_info_result = await client.automation_service_info()
        if service_info_result.automation_service_info:
            service_info = service_info_result.automation_service_info
            print(f"Service: {service_info.name} v{service_info.version}")

        # Get workspaces
        workspaces_result = await client.workspaces(first=10)
        if workspaces_result.workspaces and workspaces_result.workspaces.nodes:
            print(f"\nTotal workspaces: {workspaces_result.workspaces.total_count}")
            for workspace in workspaces_result.workspaces.nodes:
                print(f"  - {workspace.name} (Status: {workspace.build_status.value})")

        # Get automations with filter
        automations_result = await client.automations(
            first=10, where={"workspaceName": {"eq": "my-workspace"}}
        )
        if automations_result.automations and automations_result.automations.nodes:
            print(
                f"\nAutomations in 'my-workspace': {automations_result.automations.total_count}"
            )
            for automation in automations_result.automations.nodes:
                print(f"  - {automation.path}")

        # Get executions with filter and sorting
        executions_result = await client.executions(
            first=10,
            where={"status": {"eq": "SUCCEEDED"}},
            order=[{"createdAt": "DESC"}],
        )
        if executions_result.executions and executions_result.executions.nodes:
            print(
                f"\nSuccessful executions: {executions_result.executions.total_count}"
            )
            for execution in executions_result.executions.nodes:
                print(
                    f"  - {execution.automation_path} "
                    f"(Status: {execution.status.value}, Created: {execution.created_at})"
                )

        # Get repositories
        repositories_result = await client.repositories(first=10)
        if repositories_result.repositories and repositories_result.repositories.nodes:
            print(f"\nRepositories: {repositories_result.repositories.total_count}")
            for repo in repositories_result.repositories.nodes:
                print(f"  - {repo.name} ({repo.url})")

        # Get schedules
        schedules_result = await client.schedules(first=10)
        if schedules_result.schedules and schedules_result.schedules.nodes:
            print(f"\nSchedules: {schedules_result.schedules.total_count}")
            for schedule in schedules_result.schedules.nodes:
                print(
                    f"  - {schedule.name} (Active: {schedule.active}, Cron: {schedule.cron})"
                )

        # Get error codes
        error_codes_result = await client.error_codes(first=10)
        if error_codes_result.error_codes and error_codes_result.error_codes.nodes:
            print(f"\nError codes: {error_codes_result.error_codes.total_count}")
            for error_code in error_codes_result.error_codes.nodes:
                print(f"  - {error_code.code}: {error_code.message_template}")

        # ===== Mutation Examples =====

        # Execute an automation
        execution_result = await client.execute_automation(
            input=ExecuteInput(
                workspaceName="my-workspace",
                automationPath="scripts/my_automation.py",
                initiatorType=ExecutionInitiator.MANUAL,
                arguments=[
                    ExecuteArgumentInput(name="environment", value="production"),
                    ExecuteArgumentInput(name="verbose", value="true"),
                ],
            )
        )
        if execution_result.execute:
            print(f"\nExecution started with ID: {execution_result.execute.id}")

        # Create a repository
        from questra_automation._generated.graphql_client.input_types import (
            CredentialsInput,
            RemoteInput,
        )

        repo_result = await client.create_repository(
            input=CreateRepositoryInput(
                name="my-repo",
                remote=RemoteInput(
                    url="https://github.com/example/my-repo.git",
                    credentials=CredentialsInput(
                        method=RepositoryAuthenticationMethod.SSH_KEY,
                        username=None,
                        password=None,
                    ),
                ),
            )
        )
        if repo_result.create_repository:
            print(f"\nRepository created: {repo_result.create_repository.name}")

        # Create a workspace
        workspace_result = await client.create_workspace(
            input=CreateWorkspaceInput(
                repositoryName="my-repo",
                name="my-workspace",
                branch=BranchInput(name="main", commit="abc123def456"),
            )
        )
        if workspace_result.create_workspace:
            print(f"\nWorkspace created: {workspace_result.create_workspace.name}")

        # Create a schedule
        schedule_result = await client.create_schedule(
            input=CreateScheduleInput(
                workspaceName="my-workspace",
                automationPath="scripts/daily_task.py",
                name="daily-task",
                description="Run daily at midnight",
                cron="0 0 * * *",
                timezone="Europe/Berlin",
                active=True,
                arguments=[
                    ScheduleArgumentInput(name="environment", value="production")
                ],
            )
        )
        if schedule_result.create_schedule:
            print(
                f"\nSchedule created: {schedule_result.create_schedule.name} for {schedule_result.create_schedule.automation_path}"
            )

        # Update a schedule
        update_schedule_result = await client.update_schedule(
            input=UpdateScheduleInput(
                workspaceName="my-workspace",
                automationPath="scripts/daily_task.py",
                name="daily-task",
                active=False,
            )
        )
        if update_schedule_result.update_schedule:
            print(
                f"\nSchedule updated: {update_schedule_result.update_schedule.name}"
            )

        # Synchronize workspace
        sync_result = await client.synchronize_workspace(
            input=SynchronizeWorkspaceInput(name="my-workspace")
        )
        if sync_result.synchronize_workspace:
            print(
                f"\nWorkspace synchronized: {sync_result.synchronize_workspace.name}"
            )

        # Renew SSH key
        renew_result = await client.renew_repository_ssh_key(
            input=RenewRepositorySshKeyInput(name="my-repo")
        )
        if renew_result.renew_repository_ssh_key:
            print(
                f"\nSSH key renewed for: {renew_result.renew_repository_ssh_key.name}"
            )

        # Delete a schedule
        delete_schedule_result = await client.delete_schedule(
            input=DeleteScheduleInput(
                workspaceName="my-workspace",
                automationPath="scripts/daily_task.py",
                name="daily-task",
            )
        )
        if delete_schedule_result.delete_schedule:
            print(
                f"\nSchedule deleted: {delete_schedule_result.delete_schedule.name}"
            )

        # Delete a workspace
        delete_workspace_result = await client.delete_workspace(
            input=DeleteWorkspaceInput(name="my-workspace")
        )
        if delete_workspace_result.delete_workspace:
            print(
                f"\nWorkspace deleted: {delete_workspace_result.delete_workspace.name}"
            )

        # Delete a repository
        delete_repo_result = await client.delete_repository(
            input=DeleteRepositoryInput(name="my-repo")
        )
        if delete_repo_result.delete_repository:
            print(
                f"\nRepository deleted: {delete_repo_result.delete_repository.name}"
            )


if __name__ == "__main__":
    asyncio.run(main())
