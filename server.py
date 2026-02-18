#!/usr/bin/env python3
import http.server
import json
import os
import pathlib
import subprocess
import re
import time
from datetime import datetime

WORKSPACE = "/home/rosebud0585/.openclaw/workspace1"
MEMORY_DIR = f"{WORKSPACE}/memory"
SKILLS_DIR = f"{WORKSPACE}/skills"
PORT = 8899

KNOWN_SKILLS = ["antigravity-code","antigravity-proxy","backup-rotate","claude-antigravity-task","email-sender","morning-brief","nba-analytics","openclaw-superpowers","openrouter-credits","self-improving-agent","subagent-runner","system-check"]

def get_cpu():
    try:
        with open('/proc/stat') as f:
            line = f.readline()
        fields = list(map(int, line.split()[1:]))
        idle, total = fields[3], sum(fields)
        time.sleep(0.1)
        with open('/proc/stat') as f:
            line = f.readline()
        fields2 = list(map(int, line.split()[1:]))
        return round(100 * (1 - (fields2[3] - idle) / (sum(fields2) - total)), 1)
    except:
        return 0.0

def get_mem():
    try:
        mem = {}
        with open('/proc/meminfo') as f:
            for line in f:
                if ':' in line:
                    parts = line.split(':')
                    mem[parts[0].strip()] = int(parts[1].split()[0]) // 1024
        total = mem.get('MemTotal', 0)
        used = total - mem.get('MemAvailable', mem.get('MemFree', 0))
        return used // 1024, total // 1024
    except:
        return 0, 0

def get_disk():
    try:
        st = os.statvfs('/')
        used = (st.f_blocks - st.f_bavail) * st.f_frsize
        total = st.f_blocks * st.f_frsize
        return round(used / 1e9, 2), round(total / 1e9, 2)
    except:
        return 0, 0

def get_uptime():
    try:
        with open('/proc/uptime') as f:
            up = float(f.read().split()[0])
        d, h, m = int(up // 86400), int((up % 86400) // 3600), int((up % 3600) // 60)
        return f"{d}d {h}h {m}m"
    except:
        return "unknown"

def parse_activities(limit=50):
    acts = []
    files = sorted([f for f in os.listdir(MEMORY_DIR) if re.match(r"\d{4}-\d{2}-\d{2}\.md", f)], reverse=True)
    for fname in files[:7]:
        date = fname.replace('.md', '')
        try:
            with open(f"{MEMORY_DIR}/{fname}") as f:
                content = f.read()
            for line in content.split('\n'):
                line = line.strip()
                if not line or len(line) < 10:
                    continue
                if line.startswith('# MEMORY') or line.startswith('---') or line.startswith('Last updated'):
                    continue
                typ, icon, color = 'note', '•', 'cyan'
                lo = line.lower()
                if any(k in lo for k in ['complete','done','finish','success']): typ, icon, color = 'complete', '✓', 'green'
                elif any(k in lo for k in ['error','fail','crash','broken']): typ, icon, color = 'error', '!', 'red'
                elif any(k in lo for k in ['warning','alert','timeout','429']): typ, icon, color = 'warning', '⚠', 'amber'
                elif any(k in lo for k in ['create','add','new','build']): typ, icon = 'create', '+'
                elif any(k in lo for k in ['update','change','modify','edit']): typ, icon = 'update', '⟳'
                elif any(k in lo for k in ['delete','remove','clean','prune']): typ, icon = 'delete', '−'
                elif any(k in lo for k in ['install','setup','configure']): typ, icon = 'setup', '⚙'
                elif any(k in lo for k in ['run','execute','start','launch']): typ, icon = 'run', '▶'
                elif line.startswith('#'): typ, icon, color = 'section', '◆', 'purple'
                acts.append({'date': date, 'message': line[:100], 'type': typ, 'icon': icon, 'color': color})
                if len(acts) >= limit:
                    break
        except:
            pass
        if len(acts) >= limit:
            break
    return acts

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {fmt % args}")
    
    def send_json(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_GET(self):
        try:
            path = self.path.split("?")[0]
            params = {}
            if "?" in self.path:
                for p in self.path.split("?")[1].split("&"):
                    if "=" in p:
                        k, v = p.split("=", 1)
                        params[k] = v
            
            if path == "/":
                with open(f"{WORKSPACE}/dashboard/index.html") as f:
                    html = f.read()
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(html.encode())
            elif path == "/api/status":
                ram, ramt = get_mem()
                dsk, dskt = get_disk()
                self.send_json({"cpu_percent": get_cpu(), "ram_gb": ram, "ram_total_gb": ramt, "disk_gb": dsk, "disk_total_gb": dskt, "uptime": get_uptime()})
            elif path == "/api/monitor":
                try:
                    with open(f"{WORKSPACE}/memory/monitor-state.json") as f:
                        self.send_json(json.load(f))
                except:
                    self.send_json({"lastCheckAt": None, "lastRateLimitCount": 0, "lastAlertAt": None})
            elif path == "/api/providers":
                nvidia = bool(os.getenv("NVIDIA_API_KEY"))
                claude = pathlib.Path(f"{SKILLS_DIR}/claude-antigravity-task/SKILL.md").exists()
                try:
                    ollama = subprocess.run(["pgrep", "-x", "ollama"], capture_output=True, timeout=2).returncode == 0
                except:
                    ollama = False
                self.send_json({"providers": [
                    {"name": "Kimi 2.5", "status": "ok" if nvidia else "missing", "message": "NVIDIA key" if nvidia else "No key"},
                    {"name": "Claude", "status": "ok" if claude else "missing", "message": "Installed" if claude else "Missing"},
                    {"name": "Ollama", "status": "ok" if ollama else "missing", "message": "Running" if ollama else "Down"}
                ]})
            elif path == "/api/skills":
                skills = []
                for name in KNOWN_SKILLS:
                    sf = pathlib.Path(f"{SKILLS_DIR}/{name}/SKILL.md")
                    exists = sf.exists()
                    desc = ""
                    if exists:
                        try:
                            for ln in sf.read_text().split("\n"):
                                if ln.strip().startswith("description:"):
                                    desc = ln.split(":",1)[1].strip().strip('"').strip("'")
                                    break
                        except:
                            pass
                    skills.append({"name": name, "installed": exists, "description": desc})
                self.send_json({"skills": skills})
            elif path == "/api/activity":
                self.send_json({"activities": parse_activities()})
            elif path == "/api/memory":
                date = params.get("date")
                files = sorted([f for f in os.listdir(MEMORY_DIR) if re.match(r"\d{4}-\d{2}-\d{2}\.md", f)], reverse=True)
                all_dates = [f.replace(".md", "") for f in files]
                if date and f"{date}.md" in files:
                    content = pathlib.Path(f"{MEMORY_DIR}/{date}.md").read_text()
                elif files:
                    date = files[0].replace(".md", "")
                    content = pathlib.Path(f"{MEMORY_DIR}/{files[0]}").read_text()
                else:
                    date, content = None, "No memory files"
                self.send_json({"date": date, "content": content, "all_dates": all_dates})
            elif path == "/api/issues":
                issues = []
                files = sorted([f for f in os.listdir(MEMORY_DIR) if re.match(r"\d{4}-\d{2}-\d{2}\.md", f)], reverse=True)
                if files:
                    with open(f"{MEMORY_DIR}/{files[0]}") as f:
                        txt = f.read()
                    for line in txt.split("\n"):
                        lo = line.lower()
                        if any(k in lo for k in ["error", "fail", "warning", "missing", "blocked", "rate limit", "timeout", "429"]):
                            lvl = "error" if any(x in lo for x in ["error","fail","429","blocked"]) else "warning"
                            issues.append({"message": line.strip()[:120], "level": lvl})
                self.send_json({"issues": issues, "nominal": len(issues)==0})
            else:
                self.send_json({"error": "Not found"}, 404)
        except Exception as e:
            print(f"Error: {e}")
            self.send_json({"error": str(e)}, 500)

print(f"Dashboard: http://localhost:{PORT}")
http.server.HTTPServer(("", PORT), Handler).serve_forever()
