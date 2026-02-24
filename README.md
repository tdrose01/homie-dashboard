# Homie Dashboard

OpenClaw Command Center - A web-based dashboard for monitoring and managing your OpenClaw instance.

## Features

- **System Monitoring**: Real-time CPU, RAM, and uptime metrics
- **Provider Status**: Visual status indicators for all configured AI providers
- **Skills Overview**: Grid view of installed vs available skills
- **Memory Browser**: Browse session memory files by date
- **Live Updates**: Auto-refresh with pulse animations

## Quick Start

```bash
# Run the dashboard
python3 server.py

# Access at http://localhost:8899
```

## Endpoints

- `/` - Dashboard UI
- `/api/status` - System status JSON
- `/api/actions` - List allowlisted quick actions + cooldown info
- `/api/actions/run` - Execute one allowlisted action (POST JSON: `{"action":"restart_homie_dashboard"}`)

## Action Center (V1)

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

## Screenshot

Dark-themed command center with glass-morphism cards and live status indicators.

## Tech Stack

- Python 3 (http.server)
- Vanilla HTML/CSS/JS
- No external dependencies

---
Built for OpenClaw
