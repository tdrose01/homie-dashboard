The code for the cron-config endpoint is present in /workspace/homie-dashboard/server.py and the frontend is updated.
The error "Not found" indicates the running dashboard service is not using this code.
Please restart the dashboard service on the host:

  systemctl --user restart homie-dashboard.service

Then verify with:

  curl http://127.0.0.1:8899/api/cron-config

If that still fails, check the service status and logs:

  systemctl --user status homie-dashboard.service
  journalctl --user -u homie-dashboard.service -n 50