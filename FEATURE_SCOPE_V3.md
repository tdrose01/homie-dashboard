# Homie Dashboard — Feature Scope V3 (Operations Intelligence)

## Goal
Transform the dashboard from a status monitor into a full operations intelligence center by adding cost visibility, cron oversight, rate-limit awareness, and a live event feed.

## In Scope (V3)

### 1. Cost & Token Tracking
- New `/api/costs` endpoint that parses OpenClaw session logs from `~/.openclaw/agents/*/sessions/` to extract token counts and estimated costs per model.
- Falls back to the `session-cost` CLI skill if installed (`node scripts/session-cost.js --format json`).
- Frontend panel showing:
  - **Today's cost** / **All-time cost** / **Projected monthly cost** as stat cards.
  - **Per-model breakdown** table (model name, input tokens, output tokens, total cost).

### 2. Cron Job Panel
- New `/api/crons` endpoint (or filter from existing `/api/agents` data) that returns cron-type sessions with status, schedule, last run, next run, duration, and model.
- Frontend panel with a clean table/card layout showing each cron job's health at a glance.

### 3. Rate Limit Gauges
- New `/api/rate-limits` endpoint that queries `openclaw status --usage` or parses provider usage data to return per-provider usage percentages.
- Frontend visual gauges (progress bars with colored fills) showing how close each provider is to its rolling-window limit.

### 4. Live Activity Feed
- New `/api/feed` SSE (Server-Sent Events) endpoint that tails OpenClaw session logs and streams new entries as they appear.
- Frontend scrolling feed panel with color-coded entries:
  - Red = errors, Green = completions, Yellow = tool calls, Blue = LLM requests, Purple = user messages.
- Auto-scroll with a pause button; max 200 entries in-memory.

## Out of Scope (for V3)
- Cost alerts / budget thresholds (V3.1).
- Editing cron schedules from the UI.
- Historical cost charting (line/bar graphs over time).
- Full session transcript viewer.

## Success Criteria
- Tom can see at a glance how much his agents are costing today and which model is most expensive.
- Cron jobs are visible without SSH — failed crons are immediately obvious.
- Rate-limit gauges prevent surprise throttling by showing usage before it hits the wall.
- The live feed makes the dashboard feel alive and provides real-time awareness of agent activity.
