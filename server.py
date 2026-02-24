#!/usr/bin/env python3
import http.server
import json
import os
import pathlib
import subprocess
import re
import time
import argparse
from datetime import datetime

BASE_DIR = pathlib.Path(__file__).resolve().parent
WORKSPACE = "/home/rosebud0585/.openclaw/workspace1"
MEMORY_DIR = f"{WORKSPACE}/memory"
SKILLS_DIR = f"{WORKSPACE}/skills"
PORT = 8899
TODO_FILE = BASE_DIR / "TODO.md"
WORKSPACE_PATH = pathlib.Path(WORKSPACE)
TASKBOARD_FILE = WORKSPACE_PATH / "taskboard-projects.json"

KNOWN_SKILLS = ["antigravity-code","antigravity-proxy","backup-rotate","claude-antigravity-task","email-sender","morning-brief","nba-analytics","openclaw-superpowers","openrouter-credits","self-improving-agent","subagent-runner","system-check"]

ACTION_COOLDOWN_SEC = 10
_action_last_run = {}
ACTION_MAP = {
    "restart_homie_dashboard": {
        "label": "Restart homie-dashboard.service",
        "cmd": ["systemctl", "--user", "restart", "homie-dashboard.service"],
        "timeout": 20,
    },
    "restart_openclaw_gateway": {
        "label": "Restart openclaw-gateway.service",
        "cmd": ["systemctl", "--user", "restart", "openclaw-gateway.service"],
        "timeout": 25,
    },
    "check_gateway_health": {
        "label": "Check OpenClaw Gateway health",
        "cmd": ["openclaw", "health"],
        "timeout": 15,
    },
}

_cpu_last_idle = 0
_cpu_last_total = 0
_cpu_last_time = 0

def get_cpu():
    global _cpu_last_idle, _cpu_last_total, _cpu_last_time
    try:
        with open('/proc/stat') as f:
            line = f.readline()
        fields = list(map(int, line.split()[1:]))
        idle, total = fields[3], sum(fields)
        
        now = time.time()
        if _cpu_last_total == 0 or (now - _cpu_last_time) < 0.1:
            time.sleep(0.1)
            with open('/proc/stat') as f:
                line = f.readline()
            fields2 = list(map(int, line.split()[1:]))
            idle2, total2 = fields2[3], sum(fields2)
            _cpu_last_idle, _cpu_last_total, _cpu_last_time = idle2, total2, time.time()
            return round(100 * (1 - (idle2 - idle) / (total2 - total)), 1)
        else:
            idle_diff = idle - _cpu_last_idle
            total_diff = total - _cpu_last_total
            cpu = round(100 * (1 - idle_diff / total_diff), 1) if total_diff > 0 else 0.0
            _cpu_last_idle, _cpu_last_total, _cpu_last_time = idle, total, now
            return cpu
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


def parse_todo_file(path):
    items = []
    try:
        for idx, raw in enumerate(path.read_text().splitlines()):
            line = raw.strip()
            if not line:
                continue

            # Markdown checkbox style: - [ ] task / - [x] task
            m = re.match(r"^[-*]\s*\[( |x|X)\]\s*(.+)$", line)
            if m:
                done = m.group(1).lower() == "x"
                items.append({"text": m.group(2).strip(), "done": done, "line_no": idx})
                continue

            # Emoji/task marker style: - ✅ done thing / - ⬜ todo thing
            m2 = re.match(r"^[-*]\s*(✅|☑️|✔️|✔|🟩|🟢|⬜|🔲|❌|⭕)\s+(.+)$", line)
            if m2:
                mark = m2.group(1)
                text = m2.group(2).strip()
                done = mark in {"✅", "☑️", "✔️", "✔", "🟩", "🟢"}
                items.append({"text": text, "done": done, "line_no": idx})
                continue
    except:
        pass

    total = len(items)
    done_count = len([t for t in items if t["done"]])
    pct = round((done_count / total) * 100) if total else 0
    return {"items": items, "total": total, "done": done_count, "percent": pct}


def toggle_todo_item(path_str, line_no, new_done):
    try:
        p = pathlib.Path(path_str).resolve()
        ws = WORKSPACE_PATH.resolve()
        if not str(p).startswith(str(ws)):
            return False, "Path outside workspace"
        if not p.exists() or not p.is_file():
            return False, "File not found"
        if p.name not in {"TODO.md", "TASKS.md", "CHECKLIST.md", "EXECUTION_QUEUE.md", "NEXT_STEPS.md"}:
            return False, "Unsupported task file"

        lines = p.read_text().splitlines()
        if line_no < 0 or line_no >= len(lines):
            return False, "Invalid line"

        raw = lines[line_no]

        def repl_checkbox(m):
            mark = "x" if new_done else " "
            return f"- [{mark}] {m.group(2)}"

        m = re.match(r"^\s*[-*]\s*\[( |x|X)\]\s*(.+)$", raw)
        if m:
            lines[line_no] = repl_checkbox(m)
            p.write_text("\n".join(lines) + "\n")
            return True, "updated"

        m2 = re.match(r"^\s*[-*]\s*(✅|☑️|✔️|✔|🟩|🟢|⬜|🔲|❌|⭕)\s+(.+)$", raw)
        if m2:
            mark = "✅" if new_done else "⬜"
            lines[line_no] = f"- {mark} {m2.group(2)}"
            p.write_text("\n".join(lines) + "\n")
            return True, "updated"

        return False, "Line is not a task item"
    except Exception as e:
        return False, str(e)


def run_allowed_action(action_id):
    now = time.time()
    if action_id not in ACTION_MAP:
        return {"ok": False, "error": "Action not allowed"}, 400

    last = _action_last_run.get(action_id, 0)
    wait_left = ACTION_COOLDOWN_SEC - int(now - last)
    if wait_left > 0:
        return {"ok": False, "error": f"Cooldown active ({wait_left}s left)"}, 429

    action = ACTION_MAP[action_id]
    try:
        proc = subprocess.run(
            action["cmd"],
            capture_output=True,
            text=True,
            timeout=action.get("timeout", 15),
        )
        _action_last_run[action_id] = now
        out = (proc.stdout or "").strip()
        err = (proc.stderr or "").strip()
        return {
            "ok": proc.returncode == 0,
            "action": action_id,
            "label": action.get("label", action_id),
            "exit_code": proc.returncode,
            "stdout": out[-2000:],
            "stderr": err[-1200:],
            "ran_at": int(now),
        }, 200 if proc.returncode == 0 else 500
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "Action timed out", "action": action_id}, 504
    except FileNotFoundError as e:
        return {"ok": False, "error": f"Executable not found: {e}"}, 500
    except Exception as e:
        return {"ok": False, "error": str(e)}, 500


def parse_todos():
    projects = []
    grand_total = 0
    grand_done = 0

    # Preferred mode: explicit project map for a clean, unified board.
    # File: /workspace/taskboard-projects.json
    # {
    #   "projects": [
    #     {"name": "homie-dashboard", "file": "homie-dashboard-phase1/CHECKLIST.md"},
    #     {"name": "city-builder", "file": "city-builder/TODO.md"}
    #   ]
    # }
    if TASKBOARD_FILE.exists():
        try:
            data = json.loads(TASKBOARD_FILE.read_text())
            for entry in data.get("projects", []):
                rel = entry.get("file", "").strip()
                if not rel:
                    continue
                f = (WORKSPACE_PATH / rel).resolve()
                if not f.exists() or not f.is_file():
                    continue
                parsed = parse_todo_file(f)
                if parsed["total"] == 0:
                    continue
                name = entry.get("name") or f.parent.name
                projects.append({
                    "name": name,
                    "path": str(f),
                    "total": parsed["total"],
                    "done": parsed["done"],
                    "percent": parsed["percent"],
                    "items": parsed["items"],
                })
                grand_total += parsed["total"]
                grand_done += parsed["done"]
        except:
            pass

    # Fallback mode: auto-discover if no explicit map projects loaded.
    if not projects:
        todo_files = []
        if TODO_FILE.exists():
            todo_files.append(TODO_FILE)

        task_filenames = {"TODO.md", "TASKS.md", "CHECKLIST.md", "EXECUTION_QUEUE.md"}
        skip_dirs = {".git", "node_modules", ".venv", ".venv-img", "__pycache__", "memory", ".openclaw"}

        try:
            for root, dirs, files in os.walk(WORKSPACE):
                dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith('.')]
                for fn in files:
                    if fn not in task_filenames:
                        continue
                    f = pathlib.Path(root) / fn
                    if not str(f).startswith(str(WORKSPACE_PATH)):
                        continue
                    todo_files.append(f)
        except:
            pass

        todo_files = [pathlib.Path(p) for p in sorted({str(p) for p in todo_files})]
        for f in todo_files:
            parsed = parse_todo_file(f)
            if parsed["total"] == 0:
                continue

            if f.parent == BASE_DIR:
                project_name = "homie-dashboard"
            elif f.parent == WORKSPACE_PATH:
                project_name = "workspace-root"
            else:
                project_name = f.parent.name

            projects.append({
                "name": project_name,
                "path": str(f),
                "total": parsed["total"],
                "done": parsed["done"],
                "percent": parsed["percent"],
                "items": parsed["items"],
            })
            grand_total += parsed["total"]
            grand_done += parsed["done"]

    grand_pct = round((grand_done / grand_total) * 100) if grand_total else 0
    return {"projects": projects, "total": grand_total, "done": grand_done, "percent": grand_pct}

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {fmt % args}")

    def send_json(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_POST(self):
        try:
            path = self.path.split("?")[0]
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length).decode() if length else "{}"
            payload = json.loads(body or "{}")

            if path == "/api/todos/toggle":
                p = payload.get("path", "")
                line_no = int(payload.get("line_no", -1))
                new_done = bool(payload.get("done", False))
                ok, msg = toggle_todo_item(p, line_no, new_done)
                if ok:
                    self.send_json({"ok": True, "message": msg})
                else:
                    self.send_json({"ok": False, "error": msg}, 400)
                return

            if path == "/api/actions/run":
                action_id = str(payload.get("action", "")).strip()
                result, code = run_allowed_action(action_id)
                self.send_json(result, code)
                return

            self.send_json({"error": "Not found"}, 404)
        except Exception as e:
            self.send_json({"ok": False, "error": str(e)}, 500)

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
                with open(BASE_DIR / "index.html") as f:
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
                # Reflect current setup (Feb 2026):
                # - Antigravity (Gemini Pro High/Low) is primary "big brain"
                # - OpenAI Codex is active in main session routing
                # - Ollama is local/tiny runtime
                # - OpenRouter and Kimi are intentionally removed from auto-routing
                try:
                    ag = subprocess.run(
                        ["curl", "-fsS", "http://127.0.0.1:8080/health"],
                        capture_output=True,
                        timeout=2,
                        text=True,
                    ).returncode == 0
                except:
                    ag = False

                try:
                    ollama = subprocess.run(["pgrep", "-x", "ollama"], capture_output=True, timeout=2).returncode == 0
                except:
                    ollama = False

                codex_token_hint = bool(os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_TOKEN"))

                self.send_json({"providers": [
                    {
                        "name": "Antigravity (Gemini Pro)",
                        "status": "ok" if ag else "missing",
                        "message": "Proxy healthy" if ag else "Proxy down"
                    },
                    {
                        "name": "OpenAI Codex",
                        "status": "ok",
                        "message": "Auth available" if codex_token_hint else "OAuth/session managed"
                    },
                    {
                        "name": "Ollama (tiny)",
                        "status": "ok" if ollama else "missing",
                        "message": "Running" if ollama else "Not running"
                    }
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
            elif path == "/api/todos":
                self.send_json(parse_todos())
            elif path == "/api/actions":
                actions = []
                now = time.time()
                for aid, cfg in ACTION_MAP.items():
                    last = _action_last_run.get(aid, 0)
                    cooldown_left = max(0, ACTION_COOLDOWN_SEC - int(now - last)) if last else 0
                    actions.append({
                        "id": aid,
                        "label": cfg.get("label", aid),
                        "cooldown_left": cooldown_left,
                    })
                self.send_json({"actions": actions, "cooldown_sec": ACTION_COOLDOWN_SEC})
            else:
                self.send_json({"error": "Not found"}, 404)
        except Exception as e:
            print(f"Error: {e}")
            self.send_json({"error": str(e)}, 500)

def main():
    parser = argparse.ArgumentParser(description="Homie Dashboard server")
    parser.add_argument("--host", default=os.getenv("HOMIE_DASHBOARD_HOST", ""))
    parser.add_argument("--port", type=int, default=int(os.getenv("HOMIE_DASHBOARD_PORT", PORT)))
    args = parser.parse_args()

    host = args.host
    port = args.port
    bind_label = host if host else "0.0.0.0"
    print(f"Dashboard: http://{bind_label}:{port}")
    http.server.HTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    main()
