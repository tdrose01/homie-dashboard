# Homie Dashboard

OpenClaw Command Center - A web-based dashboard for monitoring and managing your OpenClaw instance.

## Features

- **Sidebar Navigation**: Fixed sidebar with 6 sections (Dashboard, Agents, Memory, Tasks, Costs, Actions)
- **Mobile Responsive**: Collapsible sidebar with hamburger menu on mobile
- **System Monitoring**: Real-time CPU, RAM, and uptime metrics
- **Agent Fleet**: Live agent status with parent/child tree view
- **Provider Status**: Visual status indicators for all configured AI providers
- **Skills Overview**: Grid view of installed vs available skills
- **Memory Browser**: Browse session memory files by date with search
- **Cost Tracking**: Daily cost history, model breakdown, rate limits
- **Cron Monitor**: Status of all enabled cron jobs
- **Live Updates**: Auto-refresh with pulse animations
- **Keyboard Shortcuts**: `[` toggles sidebar, `r` refreshes, `t` toggles theme

## Quick Start

```bash
# Run the dashboard
python3 server.py

# Access at http://localhost:8899
```

## Navigation Sections

| Section | Icon | Description |
|---------|------|-------------|
| Dashboard | 📊 | System overview, gateway health, memory log, alerts |
| Agents | 🤖 | Active agent fleet with tree view |
| Memory | 🧠 | Memory browser with semantic search (planned) |
| Tasks | 📋 | TODO progress and task tracking |
| Costs | 💰 | Cost history, model breakdown, rate limits |
| Actions | ⚡ | Quick action center with allowlisted commands |

## Endpoints

- `/` - Dashboard UI
- `/api/status` - System status JSON
- `/api/agents` - Active agents list
- `/api/costs` - Cost breakdown by model
- `/api/cost-history` - Daily cost history
- `/api/crons` - Cron job status
- `/api/actions` - List allowlisted quick actions + cooldown info
- `/api/actions/run` - Execute one allowlisted action (POST JSON: `{"action":"restart_homie_dashboard"}`)

## Action Center

The dashboard includes an **Action Center** panel with safe quick actions:

- Restart `homie-dashboard.service`
- Restart `openclaw-gateway.service`
- Check OpenClaw gateway health

### Example API calls

```bash
# list actions
curl -s http://127.0.0.1:8899/api/actions | jq

# run one action
curl -s -X POST http://127.0.0.1:8899/api/actions/run \
  -H 'Content-Type: application/json' \
  -d '{"action":"check_gateway_health"}' | jq
```

## Tech Stack

- Python 3 (http.server)
- Vanilla HTML/CSS/JS
- No external dependencies

## Recent Changes

- **V4 (2026-03-05)**: Added sidebar navigation per PRD V4
- **V3.1**: Daily cost history chart with hover tooltips
- **V3**: Ops Intel tab with cost tracking and cron monitor

---
Built for OpenClaw
