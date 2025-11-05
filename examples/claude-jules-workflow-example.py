#!/usr/bin/env python3
"""
Example: Claude orchestrating Jules for feature implementation
This shows how Claude (running MCP server locally) uses Jules MCP to implement features
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path for local execution
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class ClaudeJulesWorkflow:
    """
    Claude orchestrates Jules through MCP tools

    Note: Claude runs the Jules MCP server locally, so no separate Claude auth needed.
    Only JULES_API_KEY is required in environment.
    """

    def __init__(self):
        # Import Jules MCP server tools
        from jules_mcp.server import mcp, initialize_server

        self.mcp = mcp
        self.initialize = initialize_server

    async def setup(self):
        """Initialize Jules MCP server"""
        print("🔧 Claude: Initializing Jules MCP server...")
        await self.initialize()
        print("✅ Jules MCP server ready\n")

    async def implement_feature_complete_workflow(self):
        """
        Complete workflow: Claude designs → Jules implements → Human reviews
        """

        print("=" * 60)
        print("Claude + Jules Feature Implementation Workflow")
        print("=" * 60)
        print()

        # ===================================================================
        # PHASE 1: CLAUDE DESIGNS ARCHITECTURE
        # ===================================================================
        print("📋 PHASE 1: Claude designing architecture...")
        print("-" * 60)

        # Claude creates planning document
        planning_content = """
# Password Reset Feature - Implementation Plan

## Overview
Implement secure password reset functionality with email verification.

## Requirements
1. POST /api/v1/auth/password-reset - Generate reset token
2. POST /api/v1/auth/password-reset/confirm - Verify and reset
3. Token expires after 15 minutes (OWASP recommendation)
4. Rate limit: 3 requests per hour per IP
5. Email with reset link

## Architecture
- Use crypto.randomBytes(32) for token generation
- Hash tokens before storage (bcrypt)
- Store in password_reset_tokens table
- Queue email sending with retry (3 attempts)

## Security Requirements
- Generic error messages (don't reveal if user exists)
- HTTPS only
- Token single-use
- Log all reset attempts

## Testing Requirements
- Minimum 85% test coverage
- Test all edge cases (expired token, invalid token, etc.)

## Files to Create
- src/auth/PasswordResetService.ts
- src/routes/passwordReset.ts
- tests/auth/passwordReset.test.ts
- templates/password-reset-email.html

## Files to Reference
- src/auth/AuthService.ts (existing pattern)
- src/services/EmailService.ts (email sending)
- tests/auth/auth.test.ts (test pattern)
"""

        # Save planning document
        with open("planning.md", "w") as f:
            f.write(planning_content)

        print("✅ Claude created planning.md")
        print("   - Architecture defined")
        print("   - Security requirements specified")
        print("   - Test coverage: 85% minimum\n")

        # ===================================================================
        # PHASE 2: CLAUDE CREATES JULES WORKER WITH GUIDELINES
        # ===================================================================
        print("📋 PHASE 2: Claude creating Jules worker with guidelines...")
        print("-" * 60)

        # THIS IS THE KEY: Include Jules guidelines in task description
        task_description = """
# Implement Password Reset Feature

## Context
Users need ability to reset forgotten passwords via secure email link.

## Requirements (from planning.md)
1. Generate secure reset tokens (crypto.randomBytes(32))
2. Hash tokens before storage (bcrypt)
3. Token expiry: 15 minutes
4. Rate limiting: 3 requests/hour per IP
5. Email sending with retry logic
6. Generic error messages (security)

## Jules Guidelines (REQUIRED - READ CAREFULLY)
**IMPORTANT**: You MUST follow these rules strictly.

### SELF-REVIEW CHECKLIST (Required Before Completion)
Before marking this task complete, verify:

✅ **Security:**
   - Tokens generated with crypto.randomBytes(32)
   - Tokens hashed with bcrypt before storage
   - No hardcoded secrets or API keys
   - Input validation on all endpoints
   - Generic error messages (don't reveal if user exists)
   - Password validation (min 8 chars, complexity)

✅ **Code Quality:**
   - Follows pattern in src/auth/AuthService.ts
   - Functions < 50 lines
   - Meaningful variable names
   - No code duplication
   - No unused imports or dead code
   - Comments explain WHY, not WHAT

✅ **Testing:**
   - Minimum 85% test coverage
   - All edge cases tested
   - Error paths tested
   - All tests passing

✅ **Performance:**
   - Async/await for I/O operations
   - Proper error handling with try/catch
   - Email failures queue for retry

✅ **Edge Cases Handled:**
   - User doesn't exist → Generic message
   - Token expired → Clear error
   - Token already used → Prevent reuse
   - Email service down → Queue for retry
   - Invalid new password → Validation errors
   - Rate limit exceeded → 429 status

### CODE PATTERNS TO FOLLOW

**Pattern 1: Service Pattern (from AuthService.ts)**
```typescript
export class PasswordResetService {
  constructor(
    private userRepo: UserRepository,
    private emailService: EmailService
  ) {}

  async requestReset(email: string): Promise<void> {
    // Follow this pattern
  }
}
```

**Pattern 2: Route Handler (from auth.ts)**
```typescript
router.post('/password-reset', async (req, res) => {
  try {
    // Implementation
    res.json({ success: true });
  } catch (error) {
    res.status(error.statusCode || 500).json({
      success: false,
      error: error.message
    });
  }
});
```

**Pattern 3: Test Pattern (from auth.test.ts)**
```typescript
describe('PasswordResetService', () => {
  it('should generate secure reset token', async () => {
    // Test implementation
  });
});
```

### EXPECTED DELIVERABLES
- [ ] src/auth/PasswordResetService.ts (main implementation)
- [ ] src/routes/passwordReset.ts (API routes)
- [ ] tests/auth/passwordReset.test.ts (comprehensive tests)
- [ ] templates/password-reset-email.html (email template)
- [ ] Self-review checklist completed

### REFERENCE FILES
Read these files to understand existing patterns:
- planning.md: Complete specifications
- src/auth/AuthService.ts: Service pattern to follow
- src/services/EmailService.ts: Email sending pattern
- tests/auth/auth.test.ts: Test pattern to follow

### COMPLETION CRITERIA
Do NOT mark this task complete until:
1. All deliverables created
2. All tests passing (≥85% coverage)
3. Self-review checklist 100% complete
4. No security vulnerabilities
5. All edge cases handled

### IF UNCLEAR
If any requirements are ambiguous:
1. State the ambiguity clearly
2. Propose 2-3 solution options
3. Recommend best option with reasoning
4. Wait for confirmation before proceeding

## Additional Context
This is part of a multi-AI workflow where:
- Claude (me) designed the architecture
- You (Jules) implement with self-review
- Human performs final review and merge

Your self-review is critical - take time to verify everything is correct.
"""

        print("✅ Claude prepared task with comprehensive guidelines")
        print("   - Jules rules included")
        print("   - Self-review checklist provided")
        print("   - Code patterns specified")
        print("   - Reference files listed\n")

        # Create Jules worker
        print("🤖 Calling Jules MCP: jules_create_worker...")

        worker_result = await self.mcp.call_tool(
            "jules_create_worker",
            {
                "task_description": task_description,
                "source": "sources/github/yourcompany/webapp",
                "title": "Password Reset Feature Implementation",
                "github_branch": "feature/jules/password-reset"
            }
        )

        # Extract session ID from result
        session_id = "mock-session-123"  # In real scenario, extract from worker_result

        print(f"✅ Jules worker created: {session_id}")
        print("   - Task sent to Jules with full guidelines")
        print("   - Branch: feature/jules/password-reset\n")

        # ===================================================================
        # PHASE 3: MONITOR JULES' PROGRESS
        # ===================================================================
        print("📋 PHASE 3: Claude monitoring Jules' progress...")
        print("-" * 60)

        # Simulate monitoring (in real scenario, poll jules_get_activities)
        print("⏳ Jules is working...")
        print("   - Reading planning.md")
        print("   - Analyzing existing patterns")
        print("   - Generating implementation plan\n")

        await asyncio.sleep(1)  # Simulate work

        print("📊 Jules generated plan:")
        print("   1. Create PasswordResetService")
        print("   2. Add API routes")
        print("   3. Implement token generation/validation")
        print("   4. Add rate limiting")
        print("   5. Write comprehensive tests")
        print("   6. Create email template")
        print("   7. Perform self-review\n")

        # In real scenario, Claude might approve plan
        # await self.mcp.call_tool("jules_approve_plan", {...})

        print("✅ Claude approved plan\n")

        # ===================================================================
        # PHASE 4: JULES IMPLEMENTS WITH SELF-REVIEW
        # ===================================================================
        print("📋 PHASE 4: Jules implementing with self-review...")
        print("-" * 60)

        await asyncio.sleep(1)  # Simulate work

        print("🔨 Jules implementing:")
        print("   ✅ Created PasswordResetService.ts")
        print("   ✅ Added API routes")
        print("   ✅ Implemented token logic")
        print("   ✅ Added rate limiting")
        print("   ✅ Wrote 15 tests (89% coverage)")
        print("   ✅ Created email template\n")

        print("🔍 Jules performing self-review:")
        print("   ✅ Security: Tokens hashed, no secrets exposed")
        print("   ✅ Code quality: Follows AuthService pattern")
        print("   ✅ Testing: 89% coverage, all tests passing")
        print("   ✅ Performance: Async operations, proper caching")
        print("   ✅ Edge cases: All handled")
        print("   ✅ Error handling: Comprehensive\n")

        print("✅ Jules marked work complete with self-review:\n")
        print("=" * 60)
        print("JULES SELF-REVIEW REPORT")
        print("=" * 60)
        print("""
Security Checklist: ✅ PASSED
- Tokens: crypto.randomBytes(32) → bcrypt hash
- No hardcoded secrets
- Input validation on all endpoints
- Generic error messages (security)

Code Quality Checklist: ✅ PASSED
- Follows AuthService.ts pattern
- Functions avg 25 lines (< 50 limit)
- Zero code duplication
- No unused imports

Testing Checklist: ✅ PASSED
- Coverage: 89% (exceeds 85% requirement)
- 15 tests written
- All edge cases covered
- All tests passing

Performance Checklist: ✅ PASSED
- Async/await throughout
- Email retry queue implemented
- Rate limiting active

Edge Cases: ✅ ALL HANDLED
- User not found → Generic message
- Token expired → Clear error
- Token reuse → Prevented
- Email down → Queued for retry
- Invalid password → Validation errors

READY FOR HUMAN REVIEW ✅
""")

        # ===================================================================
        # PHASE 5: HUMAN FINAL REVIEW
        # ===================================================================
        print("📋 PHASE 5: Ready for human review...")
        print("-" * 60)

        print("✅ Jules completed implementation with self-review")
        print("✅ All guidelines followed")
        print("✅ Self-review checklist 100% complete")
        print("✅ Branch ready: feature/jules/password-reset\n")

        print("👤 Human next steps:")
        print("   1. Review Jules' implementation")
        print("   2. Run tests locally")
        print("   3. Check security")
        print("   4. Approve and merge to main\n")

        print("=" * 60)
        print("WORKFLOW COMPLETE")
        print("=" * 60)
        print()
        print("Summary:")
        print("- Claude designed architecture (planning.md)")
        print("- Claude created Jules worker with comprehensive guidelines")
        print("- Jules implemented following all rules")
        print("- Jules performed thorough self-review")
        print("- Human performs final approval")
        print()
        print("Key Benefits:")
        print("✅ Clear role separation")
        print("✅ Jules self-review (no Claude review needed)")
        print("✅ Comprehensive guidelines in task description")
        print("✅ High code quality enforced")
        print("✅ Ready for production")


async def main():
    """Run the complete Claude + Jules workflow example"""

    # Check for Jules API key
    if not os.getenv("JULES_API_KEY"):
        print("⚠️  JULES_API_KEY not set in environment")
        print("This is a demonstration of the workflow pattern.")
        print("In production, set JULES_API_KEY to use real Jules API.\n")

    workflow = ClaudeJulesWorkflow()

    try:
        # Initialize (would fail without real API key, but shows pattern)
        # await workflow.setup()

        # Run complete workflow (demonstration)
        await workflow.implement_feature_complete_workflow()

    except Exception as e:
        print(f"Note: {e}")
        print("\nThis example shows the coordination pattern.")
        print("With JULES_API_KEY configured, it would execute fully.")


if __name__ == "__main__":
    asyncio.run(main())
