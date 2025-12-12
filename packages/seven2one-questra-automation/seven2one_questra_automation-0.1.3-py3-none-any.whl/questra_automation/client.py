"""QuestraAutomation - Wrapper für AutomationClientGenerated mit Token-Refresh."""

from __future__ import annotations

import httpx
from questra_authentication import QuestraAuthentication

from ._generated.graphql_client import AutomationClientGenerated


class QuestraAutomation(AutomationClientGenerated):
    """
    Wrapper für AutomationClientGenerated mit automatischem Token-Refresh.

    Dieser Client verwaltet automatisch die OAuth2-Token über QuestraAuthentication
    und stellt sicher, dass bei jedem GraphQL-Request ein gültiges Token verwendet wird.

    Examples:
        Service Account:
        ```python
        from questra_authentication import QuestraAuthentication
        from questra_automation import QuestraAutomation

        # QuestraAuthentication erstellen
        auth = QuestraAuthentication(
            url="https://authentik.dev.example.com",
            username="ServiceUser",
            password="secret_password",
            oidc_discovery_paths=["/application/o/automation"],
        )

        # QuestraAutomation Client erstellen
        client = QuestraAutomation(
            base_url="https://automation.dev.example.com/graphql",
            auth_client=auth,
        )

        # Workspaces abfragen
        workspaces = await client.list_workspaces(first=10)
        for workspace in workspaces.workspaces.nodes:
            print(f"Workspace: {workspace.name}")

        # Automation ausführen
        from questra_automation._generated.graphql_client import (
            ExecuteInput,
            ExecutionInitiator,
        )

        result = await client.execute_automation(
            input=ExecuteInput(
                workspace_name="my-workspace",
                automation_path="scripts/example.py",
                initiator_type=ExecutionInitiator.MANUAL,
            )
        )
        print(f"Execution ID: {result.execute.id}")

        # Session schließen
        await client.close()
        ```

        Interaktiv:
        ```python
        auth = QuestraAuthentication(
            url="https://authentik.dev.example.com",
            interactive=True,
            oidc_discovery_paths=["/application/o/automation"],
        )

        client = QuestraAutomation(
            base_url="https://automation.dev.example.com/graphql",
            auth_client=auth,
        )
        ```
    """

    def __init__(
        self,
        base_url: str,
        auth_client: QuestraAuthentication,
        **kwargs,
    ):
        """
        Initialisiert den QuestraAutomation Client.

        Args:
            base_url: URL des GraphQL-Endpunkts
            auth_client: Konfigurierte und authentifizierte QuestraAuthentication-Instanz
            **kwargs: Zusätzliche Parameter für AsyncBaseClient

        Raises:
            ValueError: Wenn auth_client nicht authentifiziert ist
        """
        if not auth_client.is_authenticated():
            msg = (
                "QuestraAuthentication ist nicht authentifiziert. "
                "Bitte authentifizieren Sie den Client vor der Übergabe."
            )
            raise ValueError(msg)

        self._auth: QuestraAuthentication = auth_client

        # Custom HTTP Client mit Token-Injection erstellen
        http_client = self._create_token_refreshing_client()

        # Parent-Klasse initialisieren
        super().__init__(
            url=base_url,
            http_client=http_client,
            **kwargs,
        )

    def _create_token_refreshing_client(self) -> httpx.AsyncClient:
        """
        Erstellt einen HTTP-Client, der automatisch Bearer-Token vor jedem Request aktualisiert.

        Returns:
            httpx.AsyncClient mit automatischer Token-Injection
        """

        class TokenInjectingClient(httpx.AsyncClient):
            """HTTP Client mit automatischer Token-Injection vor jedem Request."""

            _auth: QuestraAuthentication

            def __init__(self, auth: QuestraAuthentication, **kwargs):  # type: ignore[misc]
                # Explizit auth=None setzen, damit httpx kein Auth-Flow verwendet
                super().__init__(auth=None, **kwargs)
                self._auth = auth

            async def send(  # type: ignore[misc,override]
                self,
                request: httpx.Request,
                *,
                stream: bool = False,
                auth: httpx._types.AuthTypes | None = httpx._client.USE_CLIENT_DEFAULT,  # type: ignore[name-defined]
                follow_redirects: bool = httpx._client.USE_CLIENT_DEFAULT,  # type: ignore[name-defined,assignment]
            ) -> httpx.Response:
                """Injiziert aktuellen Bearer-Token vor dem Request."""
                # Token vor Request aktualisieren (automatischer Refresh bei Bedarf)
                token = self._auth.get_access_token()
                request.headers["Authorization"] = f"Bearer {token}"
                # Ignoriere auth Parameter und setze auf None
                return await super().send(
                    request, stream=stream, auth=None, follow_redirects=follow_redirects
                )

        return TokenInjectingClient(auth=self._auth)

    def is_authenticated(self) -> bool:
        """
        Prüft, ob der Client authentifiziert ist.

        Returns:
            bool: True wenn authentifiziert, sonst False
        """
        return self._auth.is_authenticated()

    def reauthenticate(self) -> None:
        """
        Erzwingt eine erneute Authentifizierung.

        Nützlich bei Authentifizierungsproblemen oder wenn Credentials geändert wurden.
        """
        self._auth.reauthenticate()
