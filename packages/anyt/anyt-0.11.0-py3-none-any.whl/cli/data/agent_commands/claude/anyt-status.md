Show AnyTask workspace status and suggested tasks.

**Purpose:** Quick overview of current work state - active task, suggested next tasks, and recent activity.

**Usage:** `/anyt:anyt-status`

---

## Workflow

### 1. Check Active Task

```bash
anyt active --json
```

If there is an active task, display:
- Task identifier and title
- Current status
- When it was picked

### 2. Get Suggested Tasks

```bash
anyt task suggest --limit 5 --json
```

Show top 5 suggested tasks (respects dependencies and priority).

### 3. Get Workspace Summary

```bash
anyt summary --period today --format text
```

Shows:
- Tasks completed today
- Active tasks
- Blocked tasks
- Next priorities

---

## Output Format

Present the information concisely:

```
## Current State

**Active Task:** DEV-42 - Implement OAuth callback
  Status: active | Picked: 2h ago

## Suggested Next Tasks (5)

1. DEV-45 - Add rate limiting (priority: high)
2. DEV-46 - Update error messages (priority: normal)
3. DEV-47 - Fix login timeout (priority: normal)
...

## Today's Summary

- Completed: 2 tasks
- Active: 1 task
- Blocked: 0 tasks
```

---

## Key Commands

| Command | Description |
|---------|-------------|
| `anyt active --json` | Get current active task |
| `anyt task suggest --limit N --json` | Get N suggested tasks |
| `anyt summary --period today` | Today's workspace summary |
| `anyt task list --status active` | List all active tasks |

---

Run the status check now and present the results.
