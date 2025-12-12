"""
Beispiele für QuestraAutomation Client.

Zeigt verschiedene Anwendungsfälle mit dem asynchronen Client.
"""

import asyncio

from questra_authentication import QuestraAuthentication

from questra_automation import ExecuteInput, ExecutionInitiator, QuestraAutomation

# ============================================================================
# Setup: Authentication
# ============================================================================

auth = QuestraAuthentication(
    url="https://authentik.dev.example.com",
    username="ServiceUser",
    password="secret_password",
    oidc_discovery_paths=["/application/o/automation"],
)

BASE_URL = "https://dev.techstack.s2o.dev/automation/graphql"


# ============================================================================
# Beispiel 1: Einfache Queries
# ============================================================================


async def simple_example():
    """Einfache Queries - Workspaces, Service Info."""
    print("=== Einfache Queries ===")

    # Context Manager öffnet und schließt Session automatisch
    async with QuestraAutomation(base_url=BASE_URL, auth_client=auth) as client:
        # Workspaces abfragen
        workspaces = await client.workspaces(first=5)

        if workspaces.workspaces and workspaces.workspaces.nodes:
            print(f"Gefunden: {workspaces.workspaces.total_count} Workspaces")
            for ws in workspaces.workspaces.nodes:
                print(f"  - {ws.name}")

        # Service Info abfragen
        service_info = await client.automation_service_info()
        if service_info.automation_service_info:
            info = service_info.automation_service_info
            print(f"Service Version: {info.version}")

        # Automation ausführen
        execution = await client.execute_automation(
            input=ExecuteInput(arguments=[],
                workspaceName="my-workspace",
                automationPath="scripts/hello.py",
                initiatorType=ExecutionInitiator.MANUAL,
            )
        )
        if execution.execute:
            print(f"Execution gestartet: {execution.execute.id}")


# ============================================================================
# Beispiel 2: Parallele Requests
# ============================================================================


async def parallel_example():
    """
    Parallel Requests - mehrere Queries gleichzeitig ausführen.

    Der async Client kann mehrere Requests gleichzeitig starten.
    """
    print("\n=== Parallele Requests ===")

    async with QuestraAutomation(base_url=BASE_URL, auth_client=auth) as client:
        # Mehrere Requests parallel starten
        workspaces_task = client.workspaces(first=10)
        repositories_task = client.repositories(first=10)
        service_info_task = client.automation_service_info()

        # Auf alle Ergebnisse warten (parallel ausgeführt!)
        workspaces, repositories, service_info = await asyncio.gather(
            workspaces_task, repositories_task, service_info_task
        )

        print(
            f"Workspaces: {workspaces.workspaces.total_count if workspaces.workspaces else 0}"
        )
        print(
            f"Repositories: {repositories.repositories.total_count if repositories.repositories else 0}"
        )
        if service_info.automation_service_info:
            print(f"Service: {service_info.automation_service_info.version}")


# ============================================================================
# Beispiel 3: FastAPI Integration
# ============================================================================


async def fastapi_example():
    """
    FastAPI Integration - async Client in FastAPI routes.

    In FastAPI route handlers wird der async Client verwendet,
    da FastAPI selbst async ist.
    """
    print("\n=== FastAPI-ähnlicher Use Case ===")

    # In FastAPI würde man den Client als Dependency injizieren
    # Hier simuliert als async Function
    async def get_workspace_info(workspace_name: str):
        """FastAPI Route Handler."""
        async with QuestraAutomation(base_url=BASE_URL, auth_client=auth) as client:
            # Workspaces und Automations parallel laden
            workspaces_task = client.workspaces(first=1)
            automations_task = client.automations(
                first=10, where={"workspaceName": {"eq": workspace_name}}  # type: ignore
            )

            workspaces, automations = await asyncio.gather(
                workspaces_task, automations_task
            )

            return {
                "workspace_count": workspaces.workspaces.total_count
                if workspaces.workspaces
                else 0,
                "automation_count": automations.automations.total_count
                if automations.automations
                else 0,
            }

    result = await get_workspace_info("my-workspace")
    print(f"Result: {result}")


# ============================================================================
# Beispiel 4: Error Handling
# ============================================================================


async def error_handling_example():
    """Error Handling - GraphQL Errors abfangen."""
    print("\n=== Error Handling ===")

    from questra_automation import (
        GraphQLClientGraphQLMultiError,
        GraphQLClientHttpError,
    )

    async with QuestraAutomation(base_url=BASE_URL, auth_client=auth) as client:
        try:
            # Ungültige Workspace-Name
            await client.workspaces(where={"name": {"eq": "non-existent"}})  # type: ignore
            print("Query erfolgreich")

        except GraphQLClientGraphQLMultiError as e:
            print(f"GraphQL Fehler: {e}")
            for error in e.errors:
                print(f"  - {error}")

        except GraphQLClientHttpError as e:
            print(f"HTTP Fehler: {e.status_code}")


# ============================================================================
# Hauptprogramm
# ============================================================================


async def main():
    """Führt alle Beispiele aus."""
    print("=" * 70)
    print("Questra Automation: Client Examples")
    print("=" * 70)

    # 1. Einfache Queries
    await simple_example()

    # 2. Parallel Requests
    await parallel_example()

    # 3. FastAPI Use Case
    await fastapi_example()

    # 4. Error Handling
    await error_handling_example()

    print("\n" + "=" * 70)
    print("Zusammenfassung:")
    print("=" * 70)
    print("✓ QuestraAutomation (async Client):")
    print("  - Für FastAPI, async Frameworks, Scripts")
    print("  - Parallele Requests möglich (asyncio.gather)")
    print("  - Context Manager für automatisches Session Management")
    print("  - Type-safe durch Generated GraphQL Client")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
