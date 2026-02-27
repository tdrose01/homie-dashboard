# Homie Dashboard — Feature Scope V2 (Agent Fleet Monitor)

## Feature: Agent Fleet Tab

### Goal
Provide a dedicated view to monitor all active OpenClaw agents and sub-agents, separated into distinct cards, showing exactly what they are currently working on.

### In Scope (V2)
1. **Tabbed Navigation UI**
   - Add a navigation bar/tabs to switch between "System Overview" (current dashboard) and "Agent Fleet" (new).
   - Smooth, instant client-side switching without full page reloads.

2. **Agent Cards**
   - Distinct cards for each active agent/session.
   - **Details to display:**
     - Agent Name / Session ID
     - Type (Main Session, Sub-agent, Cron Monitor)
     - Status (Idle, Working, Error)
     - Current Task / Last Message
     - Active Time / Last Seen

3. **Backend Data Pipeline (`/api/agents`)**
   - Add a new API endpoint to `server.py` that fetches the live session list.
   - Will likely query `openclaw sessions list --json` or parse OpenClaw's internal session states to extract real-time activity.

### Out of Scope (for V2)
- Interacting with agents from the UI (e.g., sending prompts or killing sub-agents from the dashboard). V2 will be *read-only* monitoring.
- Historical transcripts of dead/completed agents.

### Success Criteria
- Tom can switch to the "Agent Fleet" tab and instantly see if a sub-agent is hung or actively processing a background task.
- Clean glassmorphism cards that match the existing V1 UI.
