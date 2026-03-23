The cron-config endpoint code is present and correct in the repository.

The "Not found" error means the live dashboard process is not running this code.

**Host-side fix (run on the host, not in this sandbox):**

1. Restart the dashboard service:
   ```
   systemctl --user restart homie-dashboard.service
   ```

2. Verify it's active:
   ```
   systemctl --user is-active homie-dashboard.service && echo "active" || echo "inactive"
   ```

3. Test the endpoint:
   ```
   curl http://127.0.0.1:8899/api/cron-config
   ```

If it still returns {"error":"Not found"}, check:
- Service status: `systemctl --user status homie-dashboard.service`
- Logs: `journalctl --user -u homie-dashboard.service -n 50`
- Confirm the service ExecStart points to the correct server.py (the one in /home/rosebud0585/.openclaw/workspace1/homie-dashboard/server.py)

Once the endpoint returns JSON, the "Scheduled Jobs" panel will appear on the Costs screen.