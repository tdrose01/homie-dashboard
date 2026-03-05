# Homie Dashboard V4 — Semantic Memory + Sidebar Navigation
## Product Requirements Document
**Date**: March 3, 2026  
**Author**: Homie (CEO Agent)  
**Status**: ✅ **Sidebar Implemented** (2026-03-05) | Semantic Memory Pending  

---

## Implementation Status

| Feature | Status | Date |
|---------|--------|------|
| Sidebar Navigation (P0) | ✅ Done | 2026-03-05 |
| Semantic Memory Search (P0) | 📋 Planned | — |
| Task Board SQLite Migration (P1) | 📋 Planned | — |
| Duplicate Detection API (P1) | 📋 Planned | — |

---

## 1. Executive Summary

Transform the Homie Dashboard from a tab-based status monitor into a sidebar-navigated **operations intelligence center** powered by the new SQLite semantic memory system. Replace file-parsing with database queries, add semantic search, and improve UX with persistent sidebar navigation.

---

## 2. Goals

| Goal | Priority | Success Metric |
|------|----------|----------------|
| Replace tabs with sidebar navigation | P0 | Sidebar visible on all views, current section highlighted |
| Integrate semantic memory search | P0 | Search returns ranked results by cosine similarity |
| Migrate task board to SQLite | P1 | Live task status from `task_log` table |
| Add duplicate detection API | P1 | Pre-dispatch warnings for similar tasks |
| Archive obsolete code/docs | P2 | Remove ~40% legacy file-parsing code |

---

## 3. Current State Analysis

### 3.1 What's Working
- System monitoring (CPU, RAM, Disk, Uptime)
- Provider status indicators
- Agent fleet monitor with tree view
- Action Center with allowlisted commands
- Cost tracking (session-level)

### 3.2 What's Broken/Obsolete
| Component | Problem | Solution |
|-----------|---------|----------|
| **Memory Browser** | Parses `/memory/*.md` files, keyword search only | Replace with `search_memories_semantic()` API |
| **Activity Feed** | Regex-scrapes memory files | Query `memories` table directly |
| **Task Board** | Reads TODO.md files | Connect to `task_log` with live status |
| **Cost Tracking** | Estimates from sessions, stores in JSON | Use `task_log.prompt_tokens/completion_tokens` |
| **Tabs** | Clunky on mobile, limited space | **Sidebar Navigation** |

### 3.3 New Capabilities Available
- SQLite database with embeddings at `memory_system/openclaw_memory.db`
- `search_memories_semantic(query, limit)` — returns ranked results
- `is_duplicate_task(task_description, threshold=0.92)` — pre-dispatch check
- `get_context_for_task(task_description, limit=5)` — context injection preview

---

## 4. Feature Requirements

### 4.1 Navigation: Sidebar (P0)

**Design**:
```
┌─────────────────────────────────────────────┐
│  🐙 HOMIE      │  [Current Section Title]    │
│  ─────────────┼────────────────────────────│
│               │                              │
│  📊 Dashboard  │  [Main Content Area]         │
│  🤖 Agents     │                              │
│  🧠 Memory     │                              │
│  📋 Tasks      │                              │
│  💰 Costs      │                              │
│  ⚡ Actions    │                              │
│  ─────────────┼────────────────────────────│
│  🌙 Theme     │  [Footer: Status/Refresh]   │
│               │                              │
└─────────────────────────────────────────────┘
```

**Behavior**:
- Fixed sidebar on desktop (240px width), collapsible on mobile (<768px)
Current section highlighted with accent color
- Icons + text labels, text hidden in compact mode
- Mobile: hamburger menu, slide-out drawer
- Keyboard shortcut: `[` to toggle sidebar

**Icons**:
| Section | Icon | Color |
|---------|------|-------|
| Dashboard | 📊 | Cyan |
| Agents | 🤖 | Purple |
| Memory | 🧠 | Green |
| Tasks | 📋 | Yellow |
| Costs | 💰 | Amber |
| Actions | ⚡ | Red |

---

### 4.2 Memory Section: Semantic Search (P0)

**Current**: File browser with keyword search  
**New**: Full semantic search interface

**UI Components**:
1. **Search Input** — Text field with placeholder "Search memories by meaning..."
2. **Similarity Threshold** — Slider 0.5-0.95 (default 0.7)
3. **Filters** — Importance (1-3), Agent (dropdown), Type (task/result/decision/error)
4. **Results List** — Ranked by similarity score (distance)

**Result Card**:
```
┌────────────────────────────────────────────────┐
│ [sim=0.89] ceo · task · 2h ago              │
│ Implement semantic memory with brute-force   │
│ cosine similarity for ARM64 compatibility    │
│ [View Context] [Copy to Prompt]              │
└────────────────────────────────────────────────┘
```

**API Endpoint**: `GET /api/memory/search?q={query}&threshold={0.7}&limit={10}`

---

### 4.3 Tasks Section: Live Task Board (P1)

**Current**: Parses TODO.md files  
**New**: Real-time task tracking from SQLite

**Columns**:
| Status | Count | Description |
|--------|-------|-------------|
| 🟡 Running | N | Active subagent tasks |
| 🟢 Done | N | Completed with results |
| 🔴 Failed | N | Errors logged |

**Task Card**:
```
┌────────────────────────────────────────────────┐
│ [ceo] Refactor dashboard to sidebar layout    │
│ 2.3K tokens · $0.04 · 5m ago                   │
│ Status: running                                │
│ [Inject Context] [Cancel]                      │
└────────────────────────────────────────────────┘
```

**API Endpoints**:
- `GET /api/memory/tasks` — Recent tasks
- `GET /api/memory/tasks/{session_id}` — Tasks by session
- `POST /api/memory/duplicate-check` — Pre-dispatch validation

---

### 4.4 Duplicate Detection Panel (P1)

**Location**: Tasks section or standalone  
**Purpose**: Warn before dispatching similar tasks

**Flow**:
1. User types task description in "New Task" input
2. Real-time debounced call to `is_duplicate_task()`
3. If duplicate found (distance < 0.4):

```
⚠️ Similar task found:
   "Implement semantic memory..." (0.19 distance)
   [View Original] [Proceed Anyway]
```

---

### 4.5 Costs Section: Task-Level Tracking (P1)

**Current**: Session-level estimates from `openclaw sessions`  
**New**: Precise per-task costs from `task_log`

**Metrics**:
- Today's cost / tokens / sessions
- All-time cost / tokens
- Projected monthly
- Per-model breakdown (from `task_log.model`)
- **Top 5 most expensive tasks** (by token count)

**Chart**: Simple bar chart showing daily cost (last 30 days from `cost_history`)

---

## 5. API Changes (Backend)

### 5.1 New Endpoints

```python
# /api/memory/search
@Handler.do_GET
elif path == "/api/memory/search":
    query = params.get("q", "")
    threshold = float(params.get("threshold", 0.7))
    limit = int(params.get("limit", 10))
    results = search_memories_semantic(query, limit=min(limit, 50))
    # Filter by threshold
    filtered = [r for r in results if r["distance"] <= (2*(1-threshold))**0.5]
    self.send_json({"results": filtered})

# /api/memory/duplicates
def do_POST(self):
    if path == "/api/memory/duplicates":
        task = payload.get("task", "")
        duplicate = is_duplicate_task(task, threshold=0.92)
        self.send_json({"duplicate": duplicate, "is_duplicate": bool(duplicate)})
```

### 5.2 Migration: Cost Tracking

Update `/api/costs` to query `task_log`:
```sql
SELECT 
    DATE(created_at) as day,
    SUM(prompt_tokens) as prompt_tokens,
    SUM(completion_tokens) as completion_tokens,
    model
FROM task_log
WHERE created_at >= DATE('now', '-30 days')
GROUP BY day, model
```

---

## 6. UI Changes (Frontend)

### 6.1 CSS for Sidebar

```css
:root {
    --sidebar-width: 240px;
    --sidebar-collapsed: 60px;
}

.sidebar {
    position: fixed;
    left: 0;
    top: 0;
    width: var(--sidebar-width);
    height: 100vh;
    background: rgba(20, 20, 28, 0.95);
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    z-index: 100;
}

.main-content {
    margin-left: var(--sidebar-width);
    min-height: 100vh;
}

@media (max-width: 768px) {
    .sidebar {
        transform: translateX(-100%);
        transition: transform 0.3s;
    }
    .