Create a pull request for current work.

---

## Step 1: Ensure Active Task Exists

```bash
anyt active --json
```

**If no active task**, create one from the current discussion:

```bash
# Create implementation plan
cat > /tmp/plan.md << 'EOF'
## Overview
{Brief summary of what was implemented}

## Steps
1. {What was done}
2. {What was done}

## Files Modified
- `path/to/file` - {Changes made}
EOF

# Create and activate task
anyt task add "{Title from discussion}" \
  --description "## Objectives
- {Goal 1}
- {Goal 2}

## Acceptance Criteria
- [ ] {Criterion 1}
- [ ] {Criterion 2}
- [ ] Tests pass" \
  --status active \
  --plan-file /tmp/plan.md \
  --json
```

Extract the task identifier (e.g., `EOH-123`) from the response.

---

## Step 2: Setup Branch

```bash
IDENTIFIER={task identifier}

# Create branch if not already on a task branch
git fetch origin
git checkout -b ${IDENTIFIER}-{short-description} 2>/dev/null || true
```

---

## Step 3: Run Quality Checks

Discover and run quality checks from the project (Makefile, package.json, pyproject.toml):

1. Format code
2. Run linting
3. Run type checking
4. Run tests

Fix any issues before proceeding.

---

## Step 4: Commit and Push

```bash
git add -A
git commit -m "${IDENTIFIER}: {summary}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

git push -u origin HEAD
```

---

## Step 5: Create Pull Request

```bash
gh pr create --title "[${IDENTIFIER}] {Task Title}" --body "$(cat <<'EOF'
## Summary
{Brief description of changes}

## Changes
- {Change 1}
- {Change 2}

## Test Plan
- [ ] All tests pass
- [ ] Linting passes

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## Step 6: Register PR with Task

```bash
PR_URL=$(gh pr view --json url -q .url)
PR_NUMBER=$(gh pr view --json number -q .number)

anyt task pr register ${IDENTIFIER} \
  --pr-number $PR_NUMBER \
  --pr-url $PR_URL \
  --head-branch $(git branch --show-current) \
  --base-branch main \
  --head-sha $(git rev-parse HEAD)

anyt comment add ${IDENTIFIER} -m "PR created: $PR_URL"
```

---

## Done

Return the PR URL to the user.
