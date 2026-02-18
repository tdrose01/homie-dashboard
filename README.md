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

## Screenshot

Dark-themed command center with glass-morphism cards and live status indicators.

## Tech Stack

- Python 3 (http.server)
- Vanilla HTML/CSS/JS
- No external dependencies

---
Built for OpenClaw
