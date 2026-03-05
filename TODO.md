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
- [x] Smoke-test action buttons on host and verify service behavior
- [x] Update README with Action Center usage examples

## Ops Cleanup (2026-02-24)
- [x] Verified `homie-dashboard.service` recovered and is running on `127.0.0.1:8899`.
- [x] Unblock project file ownership (`deploy/`, `scripts/`, `__pycache__/`, `UI_FIXES.md` are root-owned).
- [x] Update `scripts/safe-reload.sh` from `py_compile` to `ast.parse` to avoid `__pycache__` permission regressions.
- [x] Sync `deploy/DEPLOY_AUTOMATION.md` wording with current `ast.parse` guardrail.
- [x] Re-validate Tailscale path routing (`/dashboard` and `/dashboard/api`).

## V3 Operations Intelligence (see FEATURE_SCOPE_V3.md)
- [x] Cost & token tracking panel (`/api/costs` + frontend stat cards + per-model breakdown)
- [x] Cron job monitoring panel (`/api/crons` + frontend table/cards)
- [x] Rate limit gauges (`/api/rate-limits` + visual progress bars per provider)
- [x] Live activity feed (`/api/feed` + scrolling color-coded event panel)

## V4 Sidebar Navigation (2026-03-05)
- [x] Replace tab-based navigation with fixed sidebar (240px desktop)
- [x] Add 6 navigation sections: Dashboard, Agents, Memory, Tasks, Costs, Actions
- [x] Mobile responsive: hamburger menu + slide-out drawer
- [x] Keyboard shortcut `[` to toggle sidebar
- [x] Dark theme with smooth transitions
- [x] Update documentation (README, PRD_V4, TODO)

## V4 Pending (Semantic Memory Integration)
- [ ] Integrate `search_memories_semantic()` API for Memory section
- [ ] Add semantic search UI with similarity threshold slider
- [ ] Connect Task Board to SQLite `task_log` table
- [ ] Add duplicate detection API endpoint
