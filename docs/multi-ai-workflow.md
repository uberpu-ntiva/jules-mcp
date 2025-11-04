# Multi-AI Workflow: Claude + Jules Collaboration

## Complete Feature Development Example

### Scenario: Implement User Authentication System

---

## **Phase 1: Research & Architecture (Claude)**

### Step 1: Claude Starts Work

```bash
# Claude creates branch
git checkout -b feature/claude/auth-design

# Claude declares intent
echo '{
  "agent_id": "claude-20251104-001",
  "task": "Design authentication architecture",
  "status": "active",
  "locked_resources": [
    "docs/auth-architecture.md",
    "docs/planning.md"
  ]
}' > .state/claude-status.json
```

### Step 2: Claude Researches & Designs

```markdown
# docs/auth-architecture.md (Created by Claude)

## Authentication System Architecture

### Design Decisions
- JWT tokens for stateless auth
- OAuth2 for third-party login
- Refresh token rotation
- Rate limiting per user

### API Design
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
GET  /api/v1/auth/verify

### Security Requirements
- Bcrypt password hashing (12 rounds)
- JWT expiry: 15 minutes
- Refresh token expiry: 7 days
- HTTPS only
```

### Step 3: Claude Commits & Handoff

```bash
# Claude commits work
git add docs/
git commit -m "feat(auth): Architecture design by Claude

- JWT-based authentication
- OAuth2 integration plan
- Security requirements specified

Agent: claude-20251104-001"

git push origin feature/claude/auth-design

# Claude updates coordination file
echo '{
  "from": "claude",
  "to": "jules",
  "message": {
    "type": "handoff",
    "action": "begin_implementation",
    "reference_docs": [
      "docs/auth-architecture.md",
      "docs/planning.md"
    ],
    "priority": "high"
  },
  "timestamp": "2025-11-04T10:30:00Z"
}' >> .state/ai-messages.json

# Claude updates status
echo '{
  "agent_id": "claude-20251104-001",
  "status": "completed",
  "next_agent": "jules"
}' > .state/claude-status.json
```

---

## **Phase 2: Implementation (Jules)**

### Step 1: Jules Receives Handoff

```python
# Jules checks for messages
messages = await coordinator.check_messages("jules")
# Message: "Begin implementation of auth system"

# Jules reads Claude's design docs
design = read_file("docs/auth-architecture.md")
planning = read_file("docs/planning.md")
```

### Step 2: Jules Creates Worker Session

```python
# Connect to Jules MCP
client = await connect_to_jules_mcp()

# Create worker for implementation
worker = await client.call_tool("jules_create_worker", {
    "task_description": """
    Implement authentication system based on Claude's architecture.

    Requirements from docs/auth-architecture.md:
    - JWT token generation and validation
    - OAuth2 login flow
    - Refresh token rotation
    - Rate limiting middleware
    - Password hashing with bcrypt

    Follow all security requirements specified.
    """,
    "source": "sources/github/yourcompany/webapp",
    "title": "Auth System Implementation",
    "github_branch": "feature/jules/auth-implementation"
})

session_id = worker["session_id"]
```

### Step 3: Jules Monitors Progress

```python
# Poll for updates
while True:
    activities = await client.call_tool("jules_get_activities", {
        "session_id": session_id
    })

    latest = activities[-1]

    if latest["status"] == "plan_ready":
        # Review generated plan
        plan = latest["plan"]
        print("Jules generated implementation plan:")
        print(plan)

        # Approve or send feedback
        await client.call_tool("jules_approve_plan", {
            "session_id": session_id,
            "plan_id": plan["id"]
        })
        break

    await asyncio.sleep(5)
```

### Step 4: Jules Completes Implementation

```bash
# Jules creates files
src/auth/AuthService.ts
src/auth/JWTService.ts
src/auth/OAuth2Service.ts
src/middleware/authMiddleware.ts
tests/auth.test.ts

# Jules commits
git add src/ tests/
git commit -m "feat(auth): Implementation by Jules

- JWT token service
- OAuth2 integration
- Auth middleware
- Comprehensive tests

Based on design by Claude (claude-20251104-001)
Agent: jules-20251104-002"

git push origin feature/jules/auth-implementation
```

### Step 5: Jules Requests Review

```bash
# Jules updates coordination
echo '{
  "from": "jules",
  "to": "claude",
  "message": {
    "type": "review_request",
    "action": "code_review",
    "branch": "feature/jules/auth-implementation",
    "files": [
      "src/auth/AuthService.ts",
      "src/auth/JWTService.ts"
    ],
    "tests_passing": true
  },
  "timestamp": "2025-11-04T14:30:00Z"
}' >> .state/ai-messages.json
```

---

## **Phase 3: Code Review (Claude)**

### Step 1: Claude Receives Review Request

```python
# Claude checks messages
messages = await coordinator.check_messages("claude")
# Message: "Review Jules' auth implementation"
```

### Step 2: Claude Reviews Code

```python
# Claude reads Jules' implementation
auth_service = read_file("src/auth/AuthService.ts")

# Claude performs analysis
review = analyze_code(auth_service, criteria=[
    "security",
    "best_practices",
    "matches_architecture",
    "test_coverage"
])

# Generate review document
review_doc = f"""
# Code Review: Authentication Implementation

## Summary
Jules' implementation follows the architecture correctly.

## Security Analysis
✅ Bcrypt password hashing (12 rounds)
✅ JWT expiry set to 15 minutes
✅ Refresh token rotation implemented
⚠️  Suggestion: Add rate limiting to login endpoint

## Code Quality
✅ TypeScript types properly defined
✅ Async/await used correctly
✅ Error handling comprehensive
✅ Test coverage: 94%

## Recommendations
1. Add rate limiting middleware (5 requests/minute on /login)
2. Add logging for failed login attempts
3. Consider adding MFA support in future

## Verdict: APPROVED with minor suggestions
"""

# Save review
write_file("docs/auth-code-review.md", review_doc)
```

### Step 3: Claude Sends Feedback

```bash
# Claude commits review
git add docs/auth-code-review.md
git commit -m "docs(auth): Code review by Claude

Reviewed Jules' auth implementation.
Approved with minor suggestions.

Agent: claude-20251104-003"

# Send message to Jules
echo '{
  "from": "claude",
  "to": "jules",
  "message": {
    "type": "review_complete",
    "verdict": "approved",
    "suggestions": [
      "Add rate limiting to login endpoint",
      "Add logging for failed attempts"
    ],
    "priority": "low"
  }
}' >> .state/ai-messages.json
```

---

## **Phase 4: Refinement (Jules)**

### Step 1: Jules Implements Suggestions

```python
# Jules receives review
review = await coordinator.check_messages("jules")
suggestions = review[0]["message"]["suggestions"]

# Send refinement message to Jules worker
await client.call_tool("jules_send_message", {
    "session_id": session_id,
    "message": f"Please implement these improvements: {suggestions}"
})

# Wait for completion
# ... Jules implements rate limiting and logging ...
```

### Step 2: Jules Finalizes

```bash
# Jules commits improvements
git add src/middleware/rateLimiter.ts
git add src/utils/authLogger.ts
git commit -m "feat(auth): Add rate limiting and logging

Based on Claude's review suggestions.

Agent: jules-20251104-004"

git push origin feature/jules/auth-implementation
```

---

## **Phase 5: Merge & Deploy (Coordinated)**

### Step 1: Create Pull Requests

```bash
# PR #1: Claude's design
gh pr create \
  --base main \
  --head feature/claude/auth-design \
  --title "Authentication System Architecture" \
  --body "Architecture and design docs by Claude"

# PR #2: Jules' implementation
gh pr create \
  --base main \
  --head feature/jules/auth-implementation \
  --title "Authentication System Implementation" \
  --body "Implementation based on Claude's design

  Reviewed by: Claude (claude-20251104-003)
  Implemented by: Jules (jules-20251104-002)"
```

### Step 2: Human Final Approval

```bash
# Human reviews both PRs
# Checks that implementation matches design
# Verifies tests pass
# Approves both PRs
```

### Step 3: Merge to Main

```bash
# Merge design first
gh pr merge 1 --squash

# Merge implementation second
gh pr merge 2 --squash

# Both AIs update memory banks
```

---

## **Coordination Summary**

| Phase | Agent | Actions | Output |
|-------|-------|---------|--------|
| 1. Research | Claude | Research, architecture design | docs/auth-architecture.md |
| 2. Planning | Claude | API design, security specs | docs/planning.md |
| 3. Handoff | Claude → Jules | Message via coordination file | .state/ai-messages.json |
| 4. Implementation | Jules | Code generation via MCP | src/auth/*.ts |
| 5. Testing | Jules | Unit & integration tests | tests/auth.test.ts |
| 6. Review Request | Jules → Claude | Request code review | .state/ai-messages.json |
| 7. Code Review | Claude | Security & quality analysis | docs/auth-code-review.md |
| 8. Refinement | Jules | Implement suggestions | Updated code |
| 9. Approval | Both → Human | PRs for final review | GitHub PRs |
| 10. Deployment | Human | Merge and deploy | Production |

---

## **Key Coordination Files**

```
project/
├── .state/                      # Ephemeral coordination (git-ignored)
│   ├── claude-status.json      # Claude's current status
│   ├── jules-status.json       # Jules' current status
│   ├── ai-messages.json        # Inter-AI messages
│   └── coordination-lock       # Prevents race conditions
│
├── memory-banks/               # Persistent knowledge (committed)
│   ├── SERVICE_auth.json       # Auth service state
│   └── AI_COLLABORATION.json   # Collaboration history
│
└── docs/
    ├── auth-architecture.md    # Claude's design
    ├── planning.md             # Claude's planning
    └── auth-code-review.md     # Claude's review
```

---

## **Benefits of This Workflow**

✅ **Clear Separation**: Claude = design, Jules = implementation
✅ **No Conflicts**: Different branches until merge
✅ **Audit Trail**: Every action tracked with agent IDs
✅ **Quality Control**: Built-in review process
✅ **Scalable**: Can add more AIs with same pattern
✅ **Secure**: Separate authentication for each AI
✅ **Cost Optimized**: Use right AI for right task

