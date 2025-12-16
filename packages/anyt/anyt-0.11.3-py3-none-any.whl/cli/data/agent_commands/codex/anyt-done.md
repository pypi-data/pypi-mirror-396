Complete the current task and prepare for the next one.

**Purpose:** Run quality checks, sync changes, and mark the active task as done. Use this when implementation is complete but you don't need to create a PR yet.

**Usage:** `/anyt:anyt-done`

**IMPORTANT:** This command marks the task as complete WITHOUT creating a PR. Use `/anyt:anyt-pr` if you need to create a pull request.

---

## Workflow

### 1. Get Active Task

```bash
anyt active --json
```

If no active task, inform the user and stop.

### 2. Run Quality Checks

Check for quality checklist at `.anyt/tasks/{IDENTIFIER}/context/quality-checklist.md`.

If it exists, execute each command listed:
- Format check (e.g., `make format`)
- Lint check (e.g., `make lint`)
- Type check (e.g., `make typecheck`)
- Unit tests (e.g., `make test`)

**If any check fails:**
- Report the failure
- Stop and ask the user how to proceed
- Do NOT mark the task as done

### 3. Verify Acceptance Criteria

Read `.anyt/tasks/{IDENTIFIER}/task.md` and verify:
- All items in `## Acceptance Criteria` section are met
- Any manual verification steps are complete

**If criteria are not met:**
- List the incomplete criteria
- Stop and ask the user how to proceed
- Do NOT mark the task as done

### 4. Sync Local Changes

```bash
anyt push {IDENTIFIER}
```

This uploads any local task changes (notes, status updates) to the server.

### 5. Add Completion Comment

```bash
anyt comment add {IDENTIFIER} -m "✓ Task completed. All quality checks passed. All acceptance criteria verified."
```

### 6. Mark Task as Done

```bash
anyt task done {IDENTIFIER} --note "Completed: {brief summary of what was implemented}"
```

### 7. Clear Active Task

```bash
anyt task unpick
```

---

## Output

After completion, inform the user:

```
✓ Task {IDENTIFIER} marked as done

Quality Checks:
  ✓ Format check passed
  ✓ Lint check passed
  ✓ Type check passed
  ✓ Tests passed

Next Steps:
- Use `/anyt:anyt-next` to pick the next task
- Use `/anyt:anyt-pr` if you need to create a pull request for this work
- Use `/clear` to clear conversation context
```

---

## Key Commands

| Command | Description |
|---------|-------------|
| `anyt active --json` | Get current active task |
| `anyt push {ID}` | Sync local task changes |
| `anyt comment add -m "..."` | Add completion comment |
| `anyt task done --note "..."` | Mark task as done |
| `anyt task unpick` | Clear active task |

---

Begin the completion workflow for the active task now.
