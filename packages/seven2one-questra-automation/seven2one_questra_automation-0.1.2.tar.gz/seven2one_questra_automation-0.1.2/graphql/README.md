# GraphQL Client Code-Generierung

Der GraphQL Client in `src/questra_automation/_generated/graphql_client` wird automatisch mit [Ariadne Codegen](https://github.com/mirumee/ariadne-codegen) aus dem Schema und den Operationen generiert.

## Workflow

### 1. Schema ändern
Falls sich das Backend-Schema ändert, aktualisiere:
```bash
packages/automation/schema/automation.sdl
```

Dann Operations neu generieren:
```bash
uv run python scripts/generate_graphql_operations.py
```

### 2. Operationen anpassen

**Zwei Dateien:**
- `operations.graphql` - **Auto-generiert** (wird überschrieben!)
- `custom_operations.graphql` - **Manuell gepflegt** (bleibt erhalten)

**Custom Operations hinzufügen:**
```bash
# Editiere diese Datei für eigene Queries/Mutations:
packages/automation/graphql/custom_operations.graphql
```

Beispiel:
```graphql
query GetWorkspaceByName($name: String!) {
  workspaces(where: { name: { eq: $name } }) {
    nodes {
      name
      repositoryName
      buildStatus
    }
  }
}
```

### 3. Client regenerieren
```bash
cd packages/automation
uv run ariadne-codegen
```

Generierte Dateien:
- `client.py` - Haupt-Client mit allen Methoden
- `enums.py` - Alle GraphQL Enums
- `input_types.py` - Input Types für Mutations/Filters
- `<operation>.py` - Pydantic Models pro Query/Mutation

### 4. Verwendung

```python
from questra_automation._generated.graphql_client import AutomationClient
from questra_automation._generated.graphql_client.input_types import ExecuteInput

client = AutomationClient(
    url="https://api.example.com/graphql",
    headers={"Authorization": "Bearer token"}
)

# Type-safe API Calls
workspaces = await client.list_workspaces(first=10)
if workspaces.workspaces:
    for ws in workspaces.workspaces.nodes:
        print(ws.name)  # Autocomplete funktioniert!
```

## Konfiguration

Siehe `pyproject.toml`:

```toml
[tool.ariadne-codegen]
schema_path = "schema/automation.sdl"
queries_path = ["graphql/operations.graphql", "graphql/custom_operations.graphql"]
target_package_path = "src/questra_automation/_generated"
target_package_name = "graphql_client"
client_name = "AutomationClientGenerated"

[tool.ariadne-codegen.scalars.DateTime]
type = "datetime.datetime"

[tool.ariadne-codegen.scalars.UUID]
type = "uuid.UUID"

[tool.ariadne-codegen.scalars.TimeSpan]
type = "datetime.timedelta"
```

## GraphQL Flexibilität vs. Code-Generierung

### Trade-off: Statische Queries vs. Runtime-Flexibilität

**GraphQL Selling Point:** Clients können flexibel nur die benötigten Felder abfragen und so Bandbreite sparen.

**Ariadne Codegen Ansatz:** Queries werden zur Build-Time aus `.graphql` Dateien generiert → **statische Field-Sets**.

#### Problem

Du kannst **nicht** zur Runtime entscheiden, welche Felder abgefragt werden:

```python
# ❌ Nicht möglich: Dynamisch Felder wählen
result = await client.list_executions(fields=["id", "status"])
```

Die Query ist "fest verdrahtet" in `operations.graphql`:
```graphql
query ListExecutions {
  executions {
    nodes {
      id
      status
      workspaceName
      # ... alle 20+ Felder
    }
  }
}
```

#### Lösungsansätze

**Option 1: Mehrere Query-Varianten** (Empfohlen)

Definiere verschiedene Queries für unterschiedliche Use-Cases:

```graphql
# Minimal - für Listen/Übersichten
query ListExecutionsMinimal($first: Int) {
  executions(first: $first) {
    nodes {
      id
      status
      createdAt
    }
  }
}

# Standard - häufigster Use-Case
query ListExecutions($first: Int, $where: AutomationExecutionViewFilterInput) {
  executions(first: $first, where: $where) {
    nodes {
      id
      status
      workspaceName
      automationPath
      createdAt
      finishedAt
    }
  }
}

# Detailed - für Einzelansicht mit Output
query ListExecutionsDetailed($first: Int) {
  executions(first: $first) {
    nodes {
      id
      status
      output
      domainStatusMessage
      # ... alle relevanten Debug-Felder
    }
  }
}
```

**Verwendung:**
```python
# Schnelle Übersicht
overview = await client.list_executions_minimal(first=100)

# Detail-View beim Klick
detail = await client.list_executions_detailed(
    first=1,
    where={"id": {"eq": selected_id}}
)
```

**Vorteil:** Type-Safe, klare Semantik, IDE Autocomplete
**Nachteil:** Mehr Boilerplate in `operations.graphql`

---

**Option 2: GraphQL Fragments** (DRY-Prinzip)

Felder in wiederverwendbare Fragments extrahieren:

```graphql
fragment ExecutionMinimal on AutomationExecutionView {
  id
  status
  createdAt
}

fragment ExecutionTimestamps on AutomationExecutionView {
  createdAt
  startedAt
  finishedAt
  duration
}

query ListExecutionsMinimal {
  executions {
    nodes {
      ...ExecutionMinimal
    }
  }
}

query ListExecutionsWithTiming {
  executions {
    nodes {
      ...ExecutionMinimal
      ...ExecutionTimestamps
    }
  }
}
```

**Vorteil:** Keine Duplikation von Field-Listen
**Nachteil:** Immer noch statisch

---

**Option 3: Custom Operations Mode** (Runtime-Flexibilität)

Aktiviere in `pyproject.toml`:
```toml
[tool.ariadne-codegen]
enable_custom_operations = true
```

Dann Query Builder nutzen:
```python
from questra_automation._generated.graphql_client.custom_fields import Query

query = Query().executions(first=10).nodes(
    # Felder zur Runtime wählen
).id().status().workspace_name()

result = await client.execute_custom_query(query)
```

**Vorteil:** Maximale Flexibilität
**Nachteil:** Verboserer Code, weniger Type-Safety, höhere Fehleranfälligkeit

---

### Empfehlung für Automation Package

**Für die Automation API gilt:**
- Datenmengen sind überschaubar (wenige Workspaces/Executions pro Request)
- Over-Fetching von 10-20 zusätzlichen String-Feldern ist vernachlässigbar (~1-2 KB)
- **Type-Safety und Developer Experience > Bandbreiten-Optimierung**

**→ Nutze Option 1 (Mehrere Query-Varianten) nur bei echtem Bedarf:**
- Wenn eine Query **deutlich** mehr Daten liefert (z.B. `output` kann MB groß sein)
- Wenn Performance-Messungen zeigen, dass es relevant ist

**Ansonsten:** Die aktuellen "Full-Queries" sind pragmatisch und ausreichend.

---

## Best Practices

1. **NICHT** die generierten Dateien in `_generated/` manuell editieren

2. **Wrapper-Client** für High-Level-API schreiben:
   ```python
   # src/questra_automation/client.py
   class QuestraAutomationClient:
       def __init__(self, base_url: str, token: str):
           self._graphql = AutomationClient(url=base_url, headers={...})

       async def execute_automation_sync(self, workspace: str, path: str) -> UUID:
           """High-level wrapper mit Error Handling"""
           result = await self._graphql.execute_automation(...)
           return result.execute.id
   ```

3. **Query-Varianten** nur bei echtem Performance-Bedarf erstellen (z.B. `output`-Feld ausschließen)

4. **Pagination** über `pageInfo.endCursor` verwenden

5. **Filter/Sort** über Input Types typsicher nutzen

6. Bei neuen **großen** Feldern (Blobs, lange Logs): Separate Queries ohne diese Felder erstellen
