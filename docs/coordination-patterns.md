# Claude + Jules Coordination Patterns

## Quick Answer to Your Questions

### **Would you work on the same version?**

**No, we'd work on separate branches initially, then merge:**

```bash
# Recommended Pattern: Separate Branches
main
  ├── feature/claude/auth-design          (Claude's work)
  └── feature/jules/auth-implementation   (Jules' work)

# Then merge both when complete
main ← [Merge Claude's design] ← [Merge Jules' implementation]
```

### **Would you share keys?**

**No, separate keys for security and auditing:**

```bash
# Each AI has its own credentials
CLAUDE_API_KEY=sk-ant-api03-xxx...
JULES_API_KEY=AQ.Ab8RN6IjejxlqvM0TAGt5bhWZeMJf9PFwuKBs...

# Benefits:
# - Track which AI did what (audit trail)
# - Revoke one without affecting the other
# - Separate cost tracking
# - Independent rate limits
```

### **What Repository Patterns (RP)?**

**Three coordination patterns:**

---

## **Pattern 1: Sequential Handoff (Most Common)**

```
┌─────────────┐
│   Claude    │ → Research & Design
│ (Architect) │   • docs/architecture.md
└──────┬──────┘   • docs/planning.md
       │
       │ Handoff via .state/ai-messages.json
       ▼
┌─────────────┐
│    Jules    │ → Implementation
│(Implementer)│   • src/**/*.ts
└──────┬──────┘   • tests/**/*.test.ts
       │
       │ Review request
       ▼
┌─────────────┐
│   Claude    │ → Code Review
│ (Reviewer)  │   • docs/review.md
└─────────────┘   • Approval/Feedback
```

**When to use:** New features, greenfield projects

**Coordination file:**
```json
{
  "workflow": "sequential",
  "current_stage": "implementation",
  "handoff": {
    "from": "claude",
    "to": "jules",
    "context": "Design complete, see docs/planning.md"
  }
}
```

---

## **Pattern 2: Parallel Collaboration**

```
┌─────────────┐           ┌─────────────┐
│   Claude    │           │    Jules    │
│(Architecture)│           │(Feature A)  │
└──────┬──────┘           └──────┬──────┘
       │                         │
       │ .state/locks            │
       │                         │
       ├── docs/arch.md.lock ────┤
       │                         │
       └── src/featureA.ts.lock ─┘
```

**When to use:** Large features, multiple components

**File locking:**
```python
# Claude locks documentation
acquire_lock("docs/architecture.md", "claude-001")

# Jules locks code files
acquire_lock("src/auth/AuthService.ts", "jules-001")

# No conflicts because different files
```

---

## **Pattern 3: Review Loop**

```
   ┌─────────────┐
   │    Jules    │ → Implement feature
   │             │
   └──────┬──────┘
          │
          │ Request review
          ▼
   ┌─────────────┐
   │   Claude    │ → Review code
   │             │   • Security analysis
   └──────┬──────┘   • Best practices
          │           • Suggestions
          │
          │ Feedback
          ▼
   ┌─────────────┐
   │    Jules    │ → Refine based on feedback
   │             │
   └──────┬──────┘
          │
          │ Final approval
          ▼
      [Merge to main]
```

**When to use:** Quality-critical code, security features

---

## **Coordination Mechanisms**

### **1. State Files (.state/ directory)**

```json
// .state/claude-status.json
{
  "agent_id": "claude-20251104-001",
  "status": "active",
  "task": "Design authentication system",
  "locked_resources": [
    "docs/auth-architecture.md"
  ],
  "last_heartbeat": "2025-11-04T10:15:00Z"
}

// .state/jules-status.json
{
  "agent_id": "jules-20251104-002",
  "status": "waiting",
  "waiting_for": "claude-20251104-001",
  "task": "Implement authentication",
  "last_heartbeat": "2025-11-04T10:16:00Z"
}
```

### **2. Message Passing**

```json
// .state/ai-messages.json
{
  "messages": [
    {
      "id": "msg-001",
      "from": "claude",
      "to": "jules",
      "type": "handoff",
      "content": {
        "action": "begin_implementation",
        "reference_docs": ["docs/planning.md"],
        "priority": "high"
      },
      "timestamp": "2025-11-04T10:30:00Z",
      "status": "unread"
    }
  ]
}
```

### **3. Memory Banks**

```json
// memory-banks/SERVICE_auth.json
{
  "service_name": "authentication",
  "ai_contributors": {
    "claude": {
      "role": "architect",
      "contributions": ["Architecture design", "Security specs"],
      "files": ["docs/auth-architecture.md"]
    },
    "jules": {
      "role": "implementer",
      "contributions": ["Auth service", "JWT tokens"],
      "files": ["src/auth/AuthService.ts"]
    }
  },
  "collaboration_notes": {
    "design_approved": "2025-11-04T10:30:00Z",
    "implementation_started": "2025-11-04T11:00:00Z",
    "review_completed": "2025-11-04T14:30:00Z"
  }
}
```

---

## **Authentication Strategy**

### **Separate Keys (Recommended)**

```typescript
// auth-config.ts
interface AICredentials {
  claude: {
    apiKey: string;      // sk-ant-api03-xxx
    mcpToken: string;    // JWT for MCP access
    permissions: string[]; // ["read", "write", "review"]
    rateLimit: number;   // 100,000 tokens/hour
  };
  jules: {
    apiKey: string;      // AQ.Ab8RN6IjejxlqvM0...
    mcpToken: string;    // JWT for MCP access
    permissions: string[]; // ["read", "write", "implement"]
    rateLimit: number;   // 60 requests/minute
  };
}

// Benefits:
// ✅ Audit trail (know which AI did what)
// ✅ Independent revocation
// ✅ Separate cost tracking
// ✅ Different permission levels
```

### **Shared Resources Authentication**

```typescript
// For shared resources (git, database, etc.)
interface SharedCredentials {
  github: {
    appToken: string;  // Shared for git operations
    allowedBranches: string[];  // Both can access
  };
  stateDatabase: {
    connectionString: string;  // Shared coordination DB
    readWriteAccess: boolean;
  };
}
```

---

## **Cost & Security Optimization**

### **Role-Based Work Distribution**

```typescript
// Cost optimization by using right AI for right task
const aiWorkDistribution = {
  claude: {
    tasks: [
      "Architecture design",    // High-value, low-cost
      "Code review",           // High-value, low-cost
      "Documentation",         // Low-cost
      "Planning"              // Low-cost
    ],
    avgCost: "$0.001 per task",
    avgTime: "5-10 minutes"
  },

  jules: {
    tasks: [
      "Code implementation",   // High-value, higher-cost
      "Bug fixing",           // Specialized
      "Refactoring"           // Specialized
    ],
    avgCost: "$0.10 per task",
    avgTime: "15-30 minutes"
  }
};

// Strategy: Use Claude for cheap design/review,
//           Jules for expensive implementation
```

### **Security Best Practices**

```typescript
// Security checklist for multi-AI coordination
const securityChecklist = {
  keyManagement: [
    "✅ Separate API keys for each AI",
    "✅ Store keys in environment variables",
    "✅ Never commit keys to git",
    "✅ Rotate keys quarterly",
    "✅ Use secret management (Vault, AWS Secrets)"
  ],

  accessControl: [
    "✅ Jules can only write to feature branches",
    "✅ Claude can only write to docs/ and review files",
    "✅ Both require human approval for main branch",
    "✅ Rate limiting per AI",
    "✅ Cost limits per AI per day"
  ],

  auditLogging: [
    "✅ Log every AI action with agent_id",
    "✅ Track file modifications per AI",
    "✅ Monitor API usage per key",
    "✅ Alert on unusual patterns"
  ]
};
```

---

## **Real-World Implementation**

### **Complete Workflow Script**

```python
# multi-ai-orchestrator.py
class MultiAIOrchestrator:
    def __init__(self):
        self.claude = ClaudeAgent(api_key=os.getenv("CLAUDE_API_KEY"))
        self.jules = JulesMCPClient(api_key=os.getenv("JULES_API_KEY"))
        self.coordinator = CoordinationManager()

    async def implement_feature(self, feature_description):
        """Orchestrate Claude + Jules for feature implementation"""

        # Phase 1: Claude designs architecture
        print("Phase 1: Claude designing architecture...")
        design = await self.claude.design_architecture(feature_description)
        await self.coordinator.save_artifact("docs/architecture.md", design)

        # Phase 2: Claude creates implementation plan
        print("Phase 2: Claude creating plan...")
        plan = await self.claude.create_plan(design)
        await self.coordinator.save_artifact("docs/planning.md", plan)

        # Phase 3: Handoff to Jules
        print("Phase 3: Handing off to Jules...")
        await self.coordinator.send_message(
            from_agent="claude",
            to_agent="jules",
            message={"action": "implement", "plan": plan}
        )

        # Phase 4: Jules implements
        print("Phase 4: Jules implementing...")
        jules_session = await self.jules.create_worker({
            "task_description": plan,
            "source": "sources/github/yourcompany/project"
        })

        # Monitor Jules' progress
        while True:
            status = await self.jules.get_activities(jules_session["session_id"])
            if status[-1]["status"] == "complete":
                break
            await asyncio.sleep(5)

        # Phase 5: Claude reviews
        print("Phase 5: Claude reviewing code...")
        code = await self.coordinator.get_latest_code()
        review = await self.claude.review_code(code)

        # Phase 6: Jules refines based on feedback
        if review["suggestions"]:
            print("Phase 6: Jules refining based on feedback...")
            await self.jules.send_message(
                jules_session["session_id"],
                f"Implement these improvements: {review['suggestions']}"
            )

        # Phase 7: Final approval
        print("Phase 7: Final approval...")
        await self.coordinator.request_human_approval({
            "design_by": "claude",
            "implementation_by": "jules",
            "review_by": "claude",
            "status": "ready_for_merge"
        })

# Usage
orchestrator = MultiAIOrchestrator()
await orchestrator.implement_feature("User authentication with JWT")
```

---

## **Summary**

### **Version Control:** Separate branches → Merge when complete
### **Authentication:** Separate keys for audit trail and security
### **Coordination:** Shared state files + message passing
### **Workflow:** Sequential (Claude designs → Jules implements → Claude reviews)

### **Key Benefits:**
- ✅ No merge conflicts (different files/branches)
- ✅ Clear audit trail (who did what)
- ✅ Cost optimized (right AI for right task)
- ✅ High quality (built-in review process)
- ✅ Secure (separate credentials, limited permissions)
- ✅ Scalable (can add more AIs with same pattern)

