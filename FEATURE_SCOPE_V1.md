# Homie Dashboard — Feature Scope V1

## Feature: Action Center + Quick Fixes

### Goal
Let Tom see system issues at a glance and apply the most common fixes from one place without SSH guesswork.

### In Scope (V1)
1. **Issue Triage Cards**
   - Show active issues from existing APIs (`/api/issues`, `/api/providers`, `/api/monitor`).
   - Severity badges: `error`, `warning`, `ok`.
   - “Last checked” timestamp.

2. **Quick Action Buttons**
   - Restart `homie-dashboard.service`
   - Restart `openclaw-gateway.service`
   - Run gateway health check
   - Refresh dashboard data

3. **Action Result Feed**
   - Inline success/failure result per action.
   - Include stderr snippet on failure.

4. **Safety Guardrails**
   - Only allow a fixed allowlist of commands (no arbitrary shell execution).
   - Basic cooldown (e.g., block same restart action for 10s).

### Out of Scope (for later)
- Multi-user auth/roles
- Remote deployment workflow
- Full terminal emulation
- Editing systemd unit files in UI

### Success Criteria
- Tom can recover dashboard/gateway from UI in under 30 seconds.
- Errors are visible without opening journalctl.
- No arbitrary command injection path exists.

### Implementation Notes
- Keep backend in `server.py` with explicit command map.
- Add new API endpoint: `POST /api/actions/run` with action id.
- Frontend: new “Action Center” panel in `index.html`.
- Log action events into memory file (optional V1.1).

### Proposed Next Tasks
1. Add backend action endpoint with allowlist + validation.
2. Add UI panel with 4 buttons + result area.
3. Add smoke tests (manual + curl examples in README).
4. Ship and verify on `127.0.0.1:8899`.
