# Homie Dashboard Safe Reload Automation

## 1) Install systemd guardrail (one-time)

```bash
mkdir -p ~/.config/systemd/user/homie-dashboard.service.d
cp /home/rosebud0585/.openclaw/workspace1/homie-dashboard/deploy/systemd-override.conf ~/.config/systemd/user/homie-dashboard.service.d/override.conf
systemctl --user daemon-reload
systemctl --user restart homie-dashboard.service
```

## 2) Use safe reload for every change

```bash
bash /home/rosebud0585/.openclaw/workspace1/homie-dashboard/scripts/safe-reload.sh
```

What it does:
- backup `server.py` + `index.html`
- syntax check (`ast.parse`, avoids `__pycache__` writes)
- restart service
- verify service active
- health check `http://127.0.0.1:8899/`
- print listener status
