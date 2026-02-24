#!/usr/bin/env bash
set -euo pipefail

SERVICE="homie-dashboard.service"
ROOT="/home/rosebud0585/.openclaw/workspace1/homie-dashboard"
SERVER="$ROOT/server.py"
URL="http://127.0.0.1:8899/"
BACKUP_DIR="$ROOT/.deploy-backups"
TS="$(date -u +%Y%m%dT%H%M%SZ)"

mkdir -p "$BACKUP_DIR"

echo "[1/6] Backup current app files"
tar -czf "$BACKUP_DIR/homie-dashboard-$TS.tgz" -C "$ROOT" server.py index.html >/dev/null 2>&1 || true

echo "[2/6] Pre-flight syntax check"
python3 -c "import pathlib, ast; ast.parse(pathlib.Path('$SERVER').read_text(encoding='utf-8'))"

echo "[3/6] Restart service"
systemctl --user restart "$SERVICE"

echo "[4/6] Wait for service"
sleep 1

if ! systemctl --user is-active --quiet "$SERVICE"; then
  echo "Service failed to start. Showing logs:"
  journalctl --user -u "$SERVICE" -n 80 --no-pager || true
  exit 1
fi

echo "[5/6] Health check"
if curl -fsS "$URL" >/dev/null; then
  echo "✅ Reload successful: $URL"
else
  echo "❌ Health check failed; showing status/logs"
  systemctl --user status "$SERVICE" --no-pager -l || true
  journalctl --user -u "$SERVICE" -n 80 --no-pager || true
  exit 1
fi

echo "[6/6] Listener check"
ss -ltnp | grep 8899 || true

echo "Done. Backup: $BACKUP_DIR/homie-dashboard-$TS.tgz"
