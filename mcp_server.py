import urllib.request
import json
import subprocess
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Homie Dashboard API Wrapper")

DASHBOARD_URL = "http://127.0.0.1:8899"

def call_dashboard_action(action_id: str) -> str:
    """Helper to call the dashboard's internal API via POST"""
    try:
        url = f"{DASHBOARD_URL}/api/actions/run"
        data = json.dumps({'action': action_id}).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            # The dashboard returns {"success": True, "output": "..."}
            if result.get("success"):
                return f"Success:\n{result.get('output', 'Action completed.')}"
            else:
                return f"Failed:\n{result.get('error', 'Unknown error.')}\nOutput:\n{result.get('output', '')}"
                
    except urllib.error.URLError as e:
        return f"Failed to connect to dashboard API: {str(e)}"
    except Exception as e:
        return f"Exception occurred: {str(e)}"

@mcp.tool()
def restart_gateway() -> str:
    """Restarts the OpenClaw gateway systemd service via the Dashboard API."""
    return call_dashboard_action("restart_openclaw_gateway")

@mcp.tool()
def restart_dashboard() -> str:
    """Restarts the Homie Dashboard systemd service via the Dashboard API."""
    return call_dashboard_action("restart_homie_dashboard")

@mcp.tool()
def check_gateway_health() -> str:
    """Runs a health check by getting the status of the gateway via the Dashboard API."""
    return call_dashboard_action("check_gateway_health")

@mcp.tool()
def get_system_status() -> str:
    """Fetches the current system metrics (CPU, Memory, Disk) from the Dashboard API."""
    try:
        url = f"{DASHBOARD_URL}/api/status"
        with urllib.request.urlopen(url, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            return json.dumps(result, indent=2)
    except Exception as e:
        return f"Failed to fetch system status: {str(e)}"

@mcp.tool()
def get_service_logs(service: str, lines: int = 50) -> str:
    """Fetches recent systemd logs for allowed services via journalctl.
    Allowed services: 'openclaw-gateway.service', 'homie-dashboard.service'
    """
    allowed_services = ["openclaw-gateway.service", "homie-dashboard.service"]
    if service not in allowed_services:
        return f"Error: Access to logs for '{service}' is not allowed for security reasons."
    
    try:
        # Safely fetch logs using subprocess
        result = subprocess.run(
            ["journalctl", "--user", "-u", service, "-n", str(lines), "--no-pager"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout if result.stdout else "No logs found."
        else:
            return f"Error fetching logs: {result.stderr}"
    except Exception as e:
        return f"Exception occurred: {str(e)}"

@mcp.tool()
def get_todos() -> str:
    """Fetches the current project progress and todo lists from the Dashboard API."""
    try:
        url = f"{DASHBOARD_URL}/api/todos"
        with urllib.request.urlopen(url, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            return json.dumps(result, indent=2)
    except Exception as e:
        return f"Failed to fetch todos: {str(e)}"

@mcp.tool()
def toggle_todo(path: str, line_no: int, done: bool) -> str:
    """Toggles a specific todo item's status via the Dashboard API.
    Args:
        path: The file path where the todo is located.
        line_no: The line number of the todo item.
        done: Boolean True (complete) or False (incomplete).
    """
    try:
        url = f"{DASHBOARD_URL}/api/todos/toggle"
        data = json.dumps({'path': path, 'line_no': line_no, 'done': done}).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get("ok"):
                return f"Success: {result.get('message', 'Todo toggled.')}"
            else:
                return f"Failed: {result.get('error', 'Unknown error.')}"
    except urllib.error.URLError as e:
        return f"Failed to connect to dashboard API: {str(e)}"
    except Exception as e:
        return f"Exception occurred: {str(e)}"

@mcp.tool()
def get_fleet_status() -> str:
    """Fetches the current real-time status of all active OpenClaw agents and sub-agents.
    Returns a summarized list of working agents, their models, token usage, and status.
    """
    try:
        url = f"{DASHBOARD_URL}/api/agents"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            if not data.get("ok"):
                return f"API returned an error: {data.get('error', 'Unknown')}"
            
            sessions = data.get("sessions", [])
            working_agents = []
            for s in sessions:
                key = s.get("key", "")
                if "cron:" in key:
                    continue
                if s.get("ageMs", 999999) < 120000 or s.get("abortedLastRun"):
                    working_agents.append(s)
            
            if not working_agents:
                return "Agent Fleet Status: No agents are currently actively working."
            
            lines = ["Agent Fleet Status (Actively Working):"]
            for s in working_agents:
                agent_id = s.get("agentId", "unknown")
                model = s.get("model", "unknown")
                tokens = s.get("totalTokens", 0)
                aborted = s.get("abortedLastRun", False)
                age_s = s.get("ageMs", 0) // 1000
                status = "Aborted/Error" if aborted else f"Working ({age_s}s ago)"
                lines.append(f"- Agent [{agent_id}] | Model: {model} | Tokens: {tokens} | Status: {status}")
                
            return "\n".join(lines)
            
    except Exception as e:
        return f"Exception occurred: {str(e)}"

if __name__ == "__main__":
    mcp.run()