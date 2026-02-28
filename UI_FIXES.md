# UI Fixes (Phase 1)

## Implemented now

- Added **Refresh now** button in header for manual updates.
- Improved **mobile behavior**:
  - memory panel now collapses to full-width on tablet/mobile.
  - tighter meta spacing on small screens.
- Hardened client rendering against broken markup/XSS:
  - escaped provider names/messages/status labels.
  - escaped skill names/descriptions.
  - escaped issues and TODO text.
- Fixed memory date chip switch bug:
  - removed implicit global `event` usage.
  - now passes clicked element directly (`switchMem(date, this)`).
  - URL param is now `encodeURIComponent` safe.
- Added empty-state messages for provider/skills panels when no data exists.

## Phase 2 (completed)

1. ~~Add lightweight toast for API fetch failures.~~
   - Toast container fixed top-right, auto-dismiss after 4s, dedup within 10s, max 3 visible.
   - `get()` and `post()` helpers now surface errors via toast instead of silently swallowing.
2. ~~Add per-panel skeleton/loading state.~~
   - Shimmer-animated skeleton placeholders for every panel on initial load.
3. ~~Add gateway health card (`status`, `NRestarts`, last probe time).~~
   - New `/api/gateway-health` endpoint queries `systemctl --user` for service state and restart count.
   - Frontend card with color-coded status, restart counter, and last probe timestamp.
4. ~~Add compact mode toggle for mobile.~~
   - Toggle in header persisted to `localStorage`.
   - Reduces padding, font sizes, gaps, and max-heights across all panels.

## Phase 3 (completed)

1. ~~Add service uptime duration to gateway health card.~~
   - Backend returns `active_since` from `ActiveEnterTimestamp`; frontend computes human-readable duration.
   - Gateway card now shows 4 metrics: Status, Restarts, Uptime, Last Probe.
2. ~~Add error boundary for individual panel render failures.~~
   - Each of the 9 panels in `load()` is wrapped in its own try/catch.
   - A single broken panel no longer prevents the rest of the dashboard from rendering.
3. ~~Add keyboard shortcuts (R to refresh, 1/2 for tab switching).~~
   - `R` refresh, `1` overview tab, `2` agents tab, `T` toggle theme, `C` toggle compact.
   - Press `?` for an in-app cheat sheet toast.
4. ~~Add dark/light theme toggle.~~
   - Sun/moon button in header; persisted to `localStorage`.
   - Full light-theme CSS: adjusted backgrounds, shadows, text colors, skeletons, toasts, etc.

## Next (recommended)

1. Add notification badge on Agent Fleet tab when agents are active.
2. Add per-action confirmation dialog for destructive actions.
3. Add auto-pause refresh when browser tab is hidden (Page Visibility API).
4. Add exportable system snapshot (JSON dump of all panel data).
