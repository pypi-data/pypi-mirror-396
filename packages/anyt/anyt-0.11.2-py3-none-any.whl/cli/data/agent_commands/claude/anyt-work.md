Work on a specific task by ID: $ARGUMENTS

**Purpose:** Pick and immediately start working on the specified task.

**Usage:** `/anyt:anyt-work DEV-42`

**IMPORTANT:** Use `/clear` to clear context before starting a new task if you have previous work context.

---

## Workflow

### 1. Pick the Task

```bash
anyt task pick $ARGUMENTS
```

This will:
- Set task status to "active" in cloud
- Pull task to `.anyt/tasks/{IDENTIFIER}/`
- Set as locally active task

### 2. Create Branch (if needed)

Check if already on a branch for this task:
```bash
git branch --show-current
```

If not on the task branch:
```bash
git fetch origin
git checkout -b {IDENTIFIER}-{short-description}
```

### 3. Check Plan Status

Before implementing, check if a plan is required:

```bash
anyt task plan show {IDENTIFIER}
```

**If plan status is `changes_requested`:**
- Review feedback and update the plan
- Resubmit with: `anyt task plan submit {IDENTIFIER} -f updated-plan.md`
- Wait for approval before proceeding

**If plan status is `pending`:**
- Wait for plan approval before implementing
- Notify user: "Plan is pending review. Implementation will begin after approval."

**If plan status is `approved` or `none`:**
- Proceed with implementation

### 4. Begin Implementation

Read task details from:
- `.anyt/tasks/{IDENTIFIER}/task.md` - Description and acceptance criteria
- `.anyt/tasks/{IDENTIFIER}/.meta.json` - Status, priority, labels
- `.anyt/tasks/{IDENTIFIER}/context/` - Additional context files

Check for quality checklist at `.anyt/tasks/{IDENTIFIER}/context/quality-checklist.md`:
- If missing, discover project quality commands from Makefile/package.json and create it

Implement following the acceptance criteria.

**Add progress comments as you work:**
```bash
anyt comment add -m "Started implementation of {feature}..."
anyt comment add -m "Completed {component}, moving to {next step}..."
```

### 5. Task Completion

**Verify acceptance criteria:**
- Read `## Acceptance Criteria` in task.md
- Ensure ALL criteria are met before marking done

**Run quality checks:**
- Execute commands from `context/quality-checklist.md`
- All checks must pass

**Mark complete:**
```bash
anyt comment add -m "All acceptance criteria verified. Quality checks passed."
anyt push {IDENTIFIER}
anyt task done --note "Completed: {summary}"
```

### 6. Create PR

```bash
git add -A
git commit -m "{IDENTIFIER}: {summary}"
git push -u origin HEAD
gh pr create --title "{IDENTIFIER}: {title}" --body "$(cat <<'EOF'
## Summary
- Brief description of changes

## Task
- {IDENTIFIER}

## Changes
- Key changes made

## Test Plan
- [ ] Quality checklist completed
- [ ] Manual testing completed

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

Return the PR URL to the user.

---

## After Completion

**Tell the user:** "Task complete! Use `/clear` to clear context, then `/anyt:anyt-next` for the next task or `/anyt:anyt-work {ID}` for a specific task."

---

## Key Commands

| Command | Description |
|---------|-------------|
| `anyt task pick {ID}` | Pick and activate task |
| `anyt active` | Show current task |
| `anyt task plan show` | Show implementation plan status |
| `anyt task plan submit -f plan.md` | Submit implementation plan |
| `anyt comment add -m "..."` | Add progress comment |
| `anyt task done` | Mark task complete |
| `anyt push {ID}` | Sync local changes |
| `anyt task pr list` | List PRs for task |
| `anyt task pr register ...` | Register a PR for task |

---

Begin working on the specified task now.
