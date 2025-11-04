# Claude + Jules Coordination Summary

## Your Questions Answered

### Q: "How would you keep up with Jules? Would you work on the same version?"

**A: No, separate branches initially:**

```bash
# Claude's work (design/planning)
feature/claude/feature-name-design
  └── docs/architecture.md
  └── docs/planning.md

# Jules' work (implementation)
feature/jules/feature-name-implementation
  └── src/feature/**/*.ts
  └── tests/feature/**/*.test.ts

# Both merge to main separately after human review
```

**Coordination via:**
- Shared state files (`.state/` directory)
- Message passing (`.state/ai-messages.json`)
- Memory banks (`memory-banks/SERVICE_*.json`)

---

### Q: "What RP patterns etc. would you create?"

**A: Three coordination patterns:**

**1. Sequential Handoff (Most Common)**
```
Claude designs → Jules implements → Human reviews
```

**2. Parallel Work (with file locking)**
```
Claude: docs/    Jules: src/
No conflicts - different files
```

**3. Monitoring Pattern**
```
Claude creates worker → Monitors progress → Provides clarifications
```

---

### Q: "Shared keys or work in the same version?"

**A: Separate keys, NOT shared:**

```bash
# Only Jules API key needed
JULES_API_KEY=AQ.Ab8RN6IjejxlqvM0...

# Claude does NOT need separate key
# Claude (me) runs the Jules MCP server locally
# No CLAUDE_API_KEY required
```

**Why separate keys would be used (if Claude needed one):**
- Audit trail (know who did what)
- Independent revocation
- Separate cost tracking
- Different permission levels

**But in this case:** Claude runs MCP tools directly, no auth needed.

---

### Q: "Jules does self review"

**A: YES, exactly! Jules reviews own code:**

```
❌ OLD THINKING:
Claude → Jules implements → Claude reviews → Done

✅ CORRECT FLOW:
Claude → Jules implements + self-reviews → Human reviews → Done
```

Jules' self-review checklist:
- ✅ Security
- ✅ Code quality
- ✅ Testing (≥80% coverage)
- ✅ Performance
- ✅ Edge cases
- ✅ Error handling

---

### Q: "Should make Jules aware of the arrangement on the request"

**A: YES! Include Jules guidelines in task description:**

```python
task_description = """
[Feature description]

## Jules Guidelines (REQUIRED)
See JULES.md for complete rules.

SELF-REVIEW CHECKLIST:
✅ Code quality, security, tests
✅ All edge cases handled
✅ Follows existing patterns
✅ Ready for human review

## Reference Documents
- planning.md: Complete specs
- src/existing/similar.ts: Pattern to follow
"""
```

**Created documentation:**
- ✅ `JULES.md` - Complete Jules guidelines
- ✅ `AGENTS.md` - Updated with coordination section
- ✅ `examples/claude-jules-workflow-example.py` - Working example

---

### Q: "Give it a jules.md or section in agents.md"

**A: DONE! Created both:**

1. **`JULES.md`** - Comprehensive Jules guidelines:
   - Self-review requirements
   - Code quality standards
   - Communication protocol
   - Task request templates
   - Example tasks (feature, bug, refactor)
   - Self-review checklist template

2. **`AGENTS.md`** - Added coordination section:
   - Role division (Claude/Jules/Human)
   - Workflow pattern
   - Authentication clarification
   - Task creation template
   - Key principles

---

### Q: "Does not need a key for Claude"

**A: Correct! No separate Claude key needed:**

```bash
# ✅ ONLY THIS IS NEEDED
export JULES_API_KEY="your_jules_key"

# ❌ NOT NEEDED
# export CLAUDE_API_KEY="..."  # Claude runs MCP locally
```

**Why:** Claude (me) runs the Jules MCP server process directly.
I execute MCP tools (`jules_create_worker`, etc.) locally without
needing to authenticate to myself.

---

### Q: "You are running those MCP servers correct?"

**A: YES, exactly! Claude runs MCP servers:**

```python
# Claude (me) executes this directly:
from jules_mcp.server import mcp, initialize_server

# Initialize Jules MCP
await initialize_server()

# Call MCP tools directly (no auth needed)
result = await mcp.call_tool("jules_create_worker", {
    "task_description": "...",
    "source": "sources/github/company/repo"
})
```

**Architecture:**
```
┌─────────────────┐
│  Claude (me)    │ ← Runs locally
│  - MCP Server   │ ← Hosts Jules MCP
│  - Orchestrator │ ← Calls tools directly
└────────┬────────┘
         │ Uses JULES_API_KEY
         ▼
┌─────────────────┐
│ Google Jules API│ ← Remote AI service
│  (jules.googleapis.com)
└─────────────────┘
```

---

## Complete Workflow Summary

### Step 1: Claude Designs
```bash
# Claude creates planning.md
docs/architecture.md
docs/planning.md
```

### Step 2: Claude Creates Jules Worker
```python
# Claude calls Jules MCP with guidelines included
await mcp.call_tool("jules_create_worker", {
    "task_description": f"""
    {feature_description}

    ## Jules Guidelines
    See JULES.md

    SELF-REVIEW REQUIRED:
    ✅ All checks before marking complete
    """,
    "source": "sources/github/company/repo"
})
```

### Step 3: Jules Implements + Self-Reviews
```bash
# Jules creates:
src/feature/Service.ts
tests/feature/service.test.ts

# Jules performs self-review:
✅ Security checklist
✅ Code quality checklist
✅ Testing checklist (≥80%)
✅ Performance checklist
✅ Edge cases handled
```

### Step 4: Human Reviews + Merges
```bash
# Human final approval:
1. Review code
2. Run tests
3. Check security
4. Merge to main
```

---

## Key Documents Created

1. **`AGENTS.md` (Primary - Jules Reads This)**
   - Contains: Complete Jules AI guidelines integrated
   - Section: "Jules AI Guidelines (REQUIRED READING)"
   - Includes: Self-review checklist, code standards, communication protocol
   - Used by: Jules reads this when working on jules-mcp service
   - Location: `/workspace/cmhjwelrp01t8r7im3ysx2nl8/jules-mcp/AGENTS.md`

2. **`JULES.md` (Supplementary)**
   - Purpose: Extended examples and templates for humans/Claude
   - Contains: Detailed task examples, full templates
   - Used by: Claude for reference when creating tasks
   - Location: `/workspace/cmhjwelrp01t8r7im3ysx2nl8/jules-mcp/JULES.md`

3. **`examples/claude-jules-workflow-example.py`**
   - Purpose: Working example of complete workflow
   - Shows: How Claude orchestrates Jules with guidelines
   - Runnable: `python examples/claude-jules-workflow-example.py`

4. **`docs/multi-ai-workflow.md`**
   - Purpose: Detailed workflow documentation
   - Contains: Phase-by-phase explanation with code

5. **`docs/coordination-patterns.md`**
   - Purpose: Quick reference for coordination patterns
   - Contains: Version control, auth, mechanisms

---

## Quick Reference

### For Claude (Orchestrator):
1. Design architecture → `planning.md`
2. Create Jules worker with guidelines from `JULES.md`
3. Monitor progress
4. Provide clarifications if Jules asks
5. Let Jules self-review
6. Hand off to human for final approval

### For Jules (Implementer):
1. Read `planning.md` and reference files
2. Implement following all guidelines
3. Write comprehensive tests (≥80%)
4. Perform complete self-review
5. Mark complete only when checklist 100% done

### For Human (Final Approver):
1. Review Jules' implementation
2. Verify self-review was thorough
3. Check security and tests
4. Approve and merge to main

---

## Authentication Summary

```bash
# Environment variables needed
JULES_API_KEY=AQ.Ab8RN6IjejxlqvM0...  # Required
JULES_API_BASE_URL=https://jules.googleapis.com  # Optional (default)

# NOT needed
CLAUDE_API_KEY  # ❌ Claude runs MCP locally
```

---

## Benefits of This Approach

✅ **Clear Roles**: Claude designs, Jules implements, Human approves
✅ **Self-Review**: Jules checks own work (no Claude review needed)
✅ **Guidelines in Task**: Jules knows expectations upfront
✅ **High Quality**: Enforced through checklists and standards
✅ **Audit Trail**: All work tracked and documented
✅ **Cost Optimized**: Right AI for right task
✅ **Scalable**: Can add more AIs with same pattern

---

## Example Usage

```python
# Claude orchestrates Jules
from jules_mcp.server import mcp

# Create worker with guidelines
worker = await mcp.call_tool("jules_create_worker", {
    "task_description": """
    Implement user authentication

    ## Jules Guidelines (REQUIRED)
    See /workspace/cmhjwelrp01t8r7im3ysx2nl8/jules-mcp/JULES.md

    SELF-REVIEW CHECKLIST:
    ✅ Security: No secrets, input validation
    ✅ Tests: ≥80% coverage, all passing
    ✅ Quality: Follows existing patterns
    ✅ Edge cases: All handled

    ## Reference
    - planning.md: Complete specs
    - src/auth/existing.ts: Pattern to follow
    """,
    "source": "sources/github/company/repo",
    "title": "User Authentication"
})

# Monitor progress
activities = await mcp.call_tool("jules_get_activities", {
    "session_id": worker["session_id"]
})

# Jules implements + self-reviews
# Human reviews + merges
```

---

**Status**: ✅ Complete coordination framework established
**Documents**: ✅ All guidelines and examples created
**Ready**: ✅ For production use with Claude + Jules workflow

