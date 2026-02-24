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

## Next (recommended)

1. Add lightweight toast for API fetch failures.
2. Add per-panel skeleton/loading state.
3. Add gateway health card (`status`, `NRestarts`, last probe time).
4. Add compact mode toggle for mobile.
