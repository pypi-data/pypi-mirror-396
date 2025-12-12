# Automation Client Generator Scripts

## generate_sync_client.py

Automatischer Generator für den synchronen Wrapper `QuestraAutomationSync`.

### Workflow

1. **API-Änderung**: GraphQL Schema oder Operations ändern
2. **Async Client generieren**:
   ```bash
   uv run ariadne-codegen
   ```
3. **Sync Client generieren**:
   ```bash
   uv run python scripts/generate_sync_client.py
   ```

### Was wird generiert?

Der Generator liest `AutomationClientGenerated` (async) und erstellt:

- Identische Methodensignaturen (ohne `async`/`await`)
- Korrekte Type Hints (Python 3.10+ Union-Syntax)
- Automatisches `**kwargs` für alle Methoden
- Context Manager Support (`__enter__`, `__exit__`)
- Lifecycle-Methoden (`is_authenticated`, `reauthenticate`, `close`)

### Ausgabe

Generiert: `src/questra_automation/sync_client.py`

**WARNUNG**: Diese Datei wird bei jedem Lauf überschrieben!

### Validierung

Nach der Generierung prüfen:

```bash
# Ruff Check
uv run ruff check src/questra_automation/sync_client.py

# Import Test
uv run python -c "from questra_automation import QuestraAutomationSync; print('OK')"

# Signatur-Vergleich (siehe Skript im generate_sync_client.py)
```

### Anpassungen

Wenn du das Generator-Verhalten ändern möchtest:

- Bearbeite `scripts/generate_sync_client.py`
- **NICHT** `sync_client.py` direkt bearbeiten!

### Konfiguration

- `SKIP_METHODS`: Low-level Methoden, die nicht gewrappt werden
- `MANUAL_METHODS`: Lifecycle-Methoden mit eigener Implementierung
