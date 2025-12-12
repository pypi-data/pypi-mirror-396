"""
Beispiel für den QuestraAutomation Client mit automatischem Token-Refresh.

Der Client nutzt QuestraAuthentication für OAuth2 und verwaltet Token automatisch.
"""

import asyncio

from questra_authentication import QuestraAuthentication

from questra_automation import QuestraAutomation
from questra_automation._generated.graphql_client import (
    AutomationExecutionStatusViewData,
    ExecutionInitiator,
)
from questra_automation._generated.graphql_client.input_types import (
    AutomationExecutionViewFilterInput,
    AutomationExecutionViewSortInput,
    ExecuteArgumentInput,
    ExecuteInput,
    WorkspaceViewFilterInput,
)


async def main() -> None:
    """Demonstriert die Verwendung des QuestraAutomation Clients."""

    # QuestraAuthentication erstellen
    auth = QuestraAuthentication(
        url="https://authentik.dev.example.com",
        username="ServiceUser",
        password="secret_password",
        oidc_discovery_paths=["/application/o/automation"],
    )

    # QuestraAutomation Client initialisieren (async context manager)
    # Der Client verwendet automatisch den aktuellen Token für jeden Request
    async with QuestraAutomation(
        base_url="https://dev.techstack.s2o.dev/automation/graphql",
        auth_client=auth,
    ) as client:
        # Beispiel 1: Service Info abrufen
        print("=== Service Info ===")
        service_info = await client.automation_service_info()
        if service_info.automation_service_info:
            info = service_info.automation_service_info
            print(f"Service: {info.name}")
            print(f"Version: {info.version}")
            print(f"Informational Version: {info.informational_version}")

        # Beispiel 2: Workspaces auflisten (mit Filter)
        print("\n=== Workspaces ===")
        workspaces_result = await client.workspaces(
            first=10,
            where=WorkspaceViewFilterInput(name={"eq": "my-workspace"}),  # type: ignore
        )

        if workspaces_result.workspaces:
            workspaces = workspaces_result.workspaces
            print(f"Total: {workspaces.total_count}")

            if workspaces.nodes:
                for workspace in workspaces.nodes:
                    print(f"  - {workspace.name} (Repo: {workspace.repository_name})")
                    print(f"    Build Status: {workspace.build_status.value}")
                    print(f"    Active Branch: {workspace.active_branch}")

        # Beispiel 3: Automations auflisten
        print("\n=== Automations ===")
        automations_result = await client.automations(first=5)

        if automations_result.automations and automations_result.automations.nodes:
            for automation in automations_result.automations.nodes:
                print(f"  - {automation.path}")
                print(f"    Workspace: {automation.workspace_name}")
                print(f"    Environment: {automation.environment}")
                print("    Arguments:")
                for arg_def in automation.argument_definitions:
                    mandatory = "required" if arg_def.mandatory else "optional"
                    print(f"      - {arg_def.name} ({mandatory}): {arg_def.description}")

        # Beispiel 4: Executions mit Filter und Sortierung
        print("\n=== Recent Failed Executions ===")
        executions_result = await client.executions(
            first=5,
            where=AutomationExecutionViewFilterInput(
                status={"eq": AutomationExecutionStatusViewData.FAILED}  # type: ignore
            ),
            order=[AutomationExecutionViewSortInput(createdAt="DESC")],  # type: ignore
        )

        if executions_result.executions and executions_result.executions.nodes:
            for execution in executions_result.executions.nodes:
                print(f"  - Execution ID: {execution.id}")
                print(f"    Automation: {execution.automation_path}")
                print(f"    Status: {execution.status.value}")
                print(f"    Created: {execution.created_at}")
                if execution.domain_status_message:
                    print(f"    Error: {execution.domain_status_message}")

        # Beispiel 5: Automation ausführen (Mutation)
        print("\n=== Execute Automation ===")
        execution = await client.execute_automation(
            input=ExecuteInput(
                workspaceName="my-workspace",
                automationPath="scripts/example.py",
                initiatorType=ExecutionInitiator.MANUAL,
                arguments=[
                    ExecuteArgumentInput(name="param1", value="value1"),
                    ExecuteArgumentInput(name="param2", value="value2"),
                ],
            )
        )

        if execution.execute:
            print(f"Started Execution: {execution.execute.id}")

        # Beispiel 6: Pagination verwenden
        print("\n=== Pagination Example ===")
        page1 = await client.schedules(first=10)

        if page1.schedules and page1.schedules.page_info.has_next_page:
            # Nächste Seite laden
            page2 = await client.schedules(
                first=10, after=page1.schedules.page_info.end_cursor
            )
            if page2.schedules and page2.schedules.nodes:
                print(f"Loaded page 2 with {len(page2.schedules.nodes)} schedules")

        # Beispiel 7: Token-Status prüfen
        print("\n=== Authentication Status ===")
        print(f"Authenticated: {auth.is_authenticated()}")


if __name__ == "__main__":
    asyncio.run(main())
