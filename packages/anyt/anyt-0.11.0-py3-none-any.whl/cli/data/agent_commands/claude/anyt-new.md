Create new task(s) in AnyTask cloud: $ARGUMENTS

**Purpose:** Analyze the description, create task(s), and set up dependencies. No confirmation needed - just create the tasks.

**Usage:** `/anyt:anyt-new Add API endpoint for user comments with threading support`

---

## Workflow

### 1. Analyze Description

- Break down what needs to be implemented
- Identify technical requirements
- **Assess complexity:**
  - **Simple** (one PR): Limited scope, few files
  - **Complex** (multiple PRs): Many systems, natural breakpoints

### 2. Discover Quality Commands

Look for quality check commands in the project:
- `Makefile` (e.g., `make lint`, `make test`, `make typecheck`)
- `package.json` scripts
- `pyproject.toml` / CI configs

### 3. Create Plan File

Before creating the task, write an implementation plan to a temporary file:

```bash
cat > /tmp/plan.md << 'EOF'
## Overview
Brief summary of the approach

## Steps
1. Step 1 - Description
2. Step 2 - Description
3. Step 3 - Description

## Files to Modify
- `path/to/file1.py` - Changes needed
- `path/to/file2.py` - Changes needed

## Testing Strategy
- Unit tests for...
- Integration tests for...

## Risks & Mitigations
- Risk 1: Mitigation approach
EOF
```

### 4. Create Task(s) with Plan

**Do NOT ask for confirmation - just create the tasks.**

**For SIMPLE tasks:**
```bash
anyt task add "Task Title" \
  --description "## Objectives
- Goal 1
- Goal 2

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Tests pass

## Technical Notes
Implementation guidance" \
  --status backlog \
  --plan-file /tmp/plan.md \
  --json
```

**For COMPLEX tasks (multiple PRs):**
Break into smaller tasks and create them all (each with their own plan):

```bash
# Task 1 - Foundation
cat > /tmp/plan1.md << 'EOF'
## Overview
Foundation setup...
EOF

anyt task add "First subtask" \
  --description "Description..." \
  --status backlog \
  --plan-file /tmp/plan1.md \
  --json

# Task 2 - Depends on Task 1
cat > /tmp/plan2.md << 'EOF'
## Overview
Build on foundation...
EOF

anyt task add "Second subtask" \
  --description "Description..." \
  --status backlog \
  --plan-file /tmp/plan2.md \
  --json

# Set dependency
anyt task dep add {TASK_2_ID} --on {TASK_1_ID}
```

### 5. Pull to Local

```bash
anyt pull {TASK_ID}
```

Creates `.anyt/tasks/{IDENTIFIER}/` with:
- `task.md` - Description
- `plan.md` - Implementation plan (if submitted)
- `.meta.json` - Metadata
- `context/` - Context folder

### 6. Create Quality Checklist

Create `.anyt/tasks/{IDENTIFIER}/context/quality-checklist.md`:

```markdown
# Quality Control Checklist

## Code Quality
- [ ] Code formatted: `{format_command}`
- [ ] Linting passes: `{lint_command}`
- [ ] Type checking passes: `{typecheck_command}`

## Testing
- [ ] Unit tests pass: `{test_command}`

## Build
- [ ] Build succeeds: `{build_command}`
```

### 7. Report Created Tasks

Show summary of created task(s):
- Task identifier(s)
- Plan status (pending/approved)
- Dependency chain (if multiple)
- Local paths

**Tell the user:**
- "Task(s) created with implementation plan (status: pending)"
- "Use `/anyt:anyt-work {ID}` to start working on a specific task"
- "Or use `/anyt:anyt-next` to auto-pick the next available task"

---

## Examples

**Simple task with plan:**
```bash
# Create plan
cat > /tmp/plan.md << 'EOF'
## Overview
Add email validation to user registration form.

## Steps
1. Create email validation utility function
2. Integrate validation into registration form
3. Add error messages

## Files to Modify
- `src/utils/validation.py` - Add email regex validator
- `src/forms/registration.py` - Use validator

## Testing Strategy
- Unit tests for validation function
EOF

# Create task with plan
anyt task add "Add email validation" \
  --description "## Objectives\n- Validate email format\n\n## Acceptance Criteria\n- [ ] Regex validation\n- [ ] Error messages\n- [ ] Tests pass" \
  --status backlog \
  --plan-file /tmp/plan.md \
  --json

# Pull to local (includes plan.md)
anyt pull DEV-45
```

---

## Key Commands

| Command | Description |
|---------|-------------|
| `anyt task add --plan-file FILE` | Create task with implementation plan |
| `anyt task add --plan "content"` | Create task with inline plan |
| `anyt task dep add {ID} --on {DEP}` | Add dependency |
| `anyt pull {ID}` | Pull task locally (includes plan.md) |
| `anyt push {ID}` | Push changes (including plan.md updates) |
| `anyt task plan show` | Show plan status |

---

Create the task(s) now without asking for confirmation. Include an implementation plan with each task.
