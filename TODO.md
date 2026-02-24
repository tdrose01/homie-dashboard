# Homie Dashboard TODO

- [x] Fix server to serve local repo `index.html`
- [x] Restore complete frontend file (was truncated)
- [x] Verify app + API status endpoint
- [x] Add TODO/progress panel in dashboard UI
- [x] Commit and push baseline fixes
- [x] Define first product feature scope with Tom (see FEATURE_SCOPE_V1.md)

## V1 Action Center
- [x] Add backend allowlisted action endpoint (`/api/actions` + `/api/actions/run`)
- [x] Add Action Center UI panel with quick action buttons + result feed
- [ ] Smoke-test action buttons on host and verify service behavior
- [x] Update README with Action Center usage examples

## Ops Cleanup (2026-02-24)
- [x] Verified `homie-dashboard.service` recovered and is running on `127.0.0.1:8899`.
- [x] Unblock project file ownership (`deploy/`, `scripts/`, `__pycache__/`, `UI_FIXES.md` are root-owned).
- [x] Update `scripts/safe-reload.sh` from `py_compile` to `ast.parse` to avoid `__pycache__` permission regressions.
- [x] Sync `deploy/DEPLOY_AUTOMATION.md` wording with current `ast.parse` guardrail.
- [ ] Re-validate Tailscale path routing (`/dashboard` and `/dashboard/api`).
