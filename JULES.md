# Jules AI Agent Guidelines

## Purpose
This document defines the rules, expectations, and coordination guidelines for Jules AI when working on Pact Platform projects through the Jules MCP server.

---

## Core Rules for Jules

### 1. Self-Review Requirement
**Jules MUST perform self-review before marking work complete:**

```
✅ Required Self-Review Checklist:
- Code follows existing patterns in the codebase
- All edge cases are handled
- Error handling is comprehensive
- Tests are written and passing
- Security best practices followed
- No unused imports or dead code
- Documentation/comments for complex logic
- Breaking changes are documented
```

### 2. Code Quality Standards

**Security:**
- Never hardcode secrets, API keys, or credentials
- Use environment variables for sensitive data
- Implement proper input validation
- Follow OWASP security guidelines
- Use parameterized queries (prevent SQL injection)
- Sanitize user inputs

**Testing:**
- Minimum 80% code coverage
- Unit tests for all business logic
- Integration tests for API endpoints
- Edge cases must be tested
- Test error handling paths

**Performance:**
- Optimize database queries (avoid N+1)
- Implement caching where appropriate
- Use async/await for I/O operations
- Consider rate limiting for public endpoints

**Code Style:**
- Follow existing project patterns
- Use TypeScript strict mode
- Meaningful variable/function names
- Keep functions small and focused
- DRY principle (Don't Repeat Yourself)

### 3. Communication Protocol

**Status Updates:**
Jules should provide clear status updates at key milestones:
- Plan generated → Wait for approval
- Implementation started
- Tests written and passing
- Self-review complete
- Ready for final review

**Questions:**
If requirements are ambiguous, Jules should:
1. State the ambiguity clearly
2. Propose 2-3 solution options
3. Recommend the best option with reasoning
4. Wait for confirmation before proceeding

### 4. Coordination with Claude

**Claude's Role:**
- Architecture design and planning
- Complex decision-making
- Cross-service coordination
- Cost optimization strategies

**Jules' Role:**
- Code implementation based on Claude's plans
- Bug fixing
- Test writing
- Self-review and quality assurance

**Handoff Pattern:**
```
1. Claude creates planning.md with detailed specifications
2. Jules receives task with reference to planning.md
3. Jules implements following the plan exactly
4. Jules performs self-review
5. Jules marks work complete
6. Human performs final review and merge
```

---

## Task Request Template

When Claude (or human) creates a Jules worker, include these instructions:

```python
task_description = """
[FEATURE/BUG DESCRIPTION]

## Context
[Brief context about what needs to be done]

## Requirements
[Specific requirements from planning.md]

## Jules Guidelines
IMPORTANT: Follow these rules strictly:

1. SELF-REVIEW REQUIRED
   - Review your own code before marking complete
   - Check security, performance, tests, and code quality
   - Verify all edge cases are handled

2. CODE QUALITY
   - Follow existing patterns in the codebase
   - Write comprehensive tests (minimum 80% coverage)
   - Handle all errors gracefully
   - No hardcoded secrets or credentials

3. REFERENCE DOCUMENTS
   - Architecture: docs/architecture.md
   - Planning: docs/planning.md
   - Code patterns: Review existing code in src/

4. COMMUNICATION
   - If unclear, ask questions with proposed solutions
   - Provide status updates at milestones
   - Document any assumptions made

5. COMPLETION CRITERIA
   - All requirements implemented
   - Tests written and passing
   - Self-review checklist complete
   - No security vulnerabilities
   - Ready for human review

## Expected Deliverables
- [ ] Implementation in src/
- [ ] Tests in tests/
- [ ] Updated documentation (if needed)
- [ ] Self-review checklist completed

## Reference Files
- planning.md: [Full specifications]
- src/existing/similar.ts: [Pattern to follow]
"""
```

---

## Example Task Requests

### Example 1: New Feature Implementation

```python
await client.call_tool("jules_create_worker", {
    "task_description": """
# Implement Password Reset Feature

## Context
Users need ability to reset forgotten passwords via email.

## Requirements (from planning.md)
1. POST /api/v1/auth/password-reset - Generate reset token
2. POST /api/v1/auth/password-reset/confirm - Verify token and set new password
3. Token expires after 1 hour
4. Rate limit: 3 requests per hour per user
5. Send email with reset link

## Jules Guidelines
SELF-REVIEW REQUIRED:
✅ Security: Token generation uses crypto.randomBytes(32)
✅ Security: Tokens are hashed before storage
✅ Security: Password validation (min 8 chars, complexity)
✅ Rate limiting implemented (3/hour per IP)
✅ Email sending with error handling
✅ Token expiry checked
✅ Tests cover all edge cases
✅ Error messages are user-friendly

## Code Quality Requirements
- Follow pattern in src/auth/AuthService.ts
- Use existing EmailService from src/services/EmailService.ts
- Write tests in tests/auth/passwordReset.test.ts
- Minimum 85% test coverage

## Edge Cases to Handle
- User doesn't exist → Generic message (security)
- Token expired → Clear error message
- Token already used → Prevent reuse
- Email service down → Queue for retry
- Invalid new password → Validation errors

## Expected Deliverables
- [ ] src/auth/PasswordResetService.ts
- [ ] src/routes/passwordReset.ts
- [ ] tests/auth/passwordReset.test.ts
- [ ] Email template: templates/password-reset-email.html

## Reference Files
- planning.md: Complete specifications
- src/auth/AuthService.ts: Pattern to follow
- tests/auth/auth.test.ts: Test pattern to follow
""",
    "source": "sources/github/yourcompany/webapp",
    "title": "Password Reset Feature",
    "github_branch": "feature/password-reset"
})
```

### Example 2: Bug Fix

```python
await client.call_tool("jules_create_worker", {
    "task_description": """
# Fix: API Rate Limiting Not Working on /api/v1/users Endpoint

## Context
Rate limiting middleware is not being applied to user endpoints.
Users can make unlimited requests, causing server overload.

## Root Cause Analysis Needed
1. Check if middleware is registered
2. Verify middleware order in app setup
3. Check if rate limit config is correct

## Jules Guidelines
SELF-REVIEW REQUIRED:
✅ Bug is fully fixed and tested
✅ Root cause identified and documented
✅ No regressions introduced
✅ Tests added to prevent future occurrence
✅ Code follows existing patterns

## Fix Requirements
- Apply rate limiting: 100 requests per 15 minutes per IP
- Use existing RateLimiterMiddleware
- Add tests to verify rate limiting works
- Document the fix in commit message

## Testing Requirements
- [ ] Test: Rate limit is enforced (should reject after 100 requests)
- [ ] Test: Rate limit resets after 15 minutes
- [ ] Test: Different IPs have independent limits
- [ ] Test: Existing functionality not broken

## Expected Deliverables
- [ ] Fixed code in src/routes/users.ts or src/app.ts
- [ ] Tests in tests/middleware/rateLimiter.test.ts
- [ ] Brief explanation of root cause in commit message

## Reference Files
- src/middleware/RateLimiterMiddleware.ts: Existing middleware
- src/app.ts: Middleware registration
""",
    "source": "sources/github/yourcompany/webapp",
    "title": "Fix rate limiting on user endpoints",
    "github_branch": "bugfix/rate-limiting"
})
```

### Example 3: Refactoring

```python
await client.call_tool("jules_create_worker", {
    "task_description": """
# Refactor: Extract Email Logic into Reusable Service

## Context
Email sending logic is duplicated across multiple services.
Need to extract into a centralized EmailService.

## Current State
- auth/AuthService.ts: Has sendVerificationEmail()
- notifications/NotificationService.ts: Has sendNotificationEmail()
- password/PasswordService.ts: Has sendResetEmail()

## Target State
- Create services/EmailService.ts with unified email sending
- All services use EmailService
- Support templates, attachments, retry logic

## Jules Guidelines
SELF-REVIEW REQUIRED:
✅ All duplicate code removed
✅ No functionality lost or changed
✅ All existing tests still pass
✅ New tests for EmailService added
✅ All services updated to use EmailService
✅ Backward compatibility maintained

## Refactoring Requirements
1. Create EmailService with methods:
   - sendEmail(to, subject, htmlBody, textBody)
   - sendTemplateEmail(to, template, data)
   - sendWithAttachment(to, subject, body, attachments)

2. Update all services to use EmailService:
   - AuthService
   - NotificationService
   - PasswordService

3. Maintain existing behavior (no breaking changes)

4. Add comprehensive tests

## Testing Requirements
- [ ] Unit tests for EmailService (all methods)
- [ ] Integration tests for each service using EmailService
- [ ] All existing tests still pass
- [ ] Test error handling (email service down, invalid email, etc.)

## Expected Deliverables
- [ ] src/services/EmailService.ts (new)
- [ ] Updated: src/auth/AuthService.ts
- [ ] Updated: src/notifications/NotificationService.ts
- [ ] Updated: src/password/PasswordService.ts
- [ ] tests/services/EmailService.test.ts
- [ ] All existing tests passing

## Reference Files
- src/auth/AuthService.ts: Current email implementation
- src/notifications/NotificationService.ts: Another implementation
""",
    "source": "sources/github/yourcompany/webapp",
    "title": "Refactor email logic into service",
    "github_branch": "refactor/email-service"
})
```

---

## Jules Self-Review Checklist Template

Jules should use this checklist before marking work complete:

```markdown
## Self-Review Checklist

### Code Quality
- [ ] Code follows existing patterns and conventions
- [ ] Functions are small and focused (< 50 lines)
- [ ] Variable/function names are clear and descriptive
- [ ] No code duplication (DRY principle)
- [ ] No unused imports or dead code
- [ ] Comments explain WHY, not WHAT

### Security
- [ ] No hardcoded secrets or API keys
- [ ] Input validation on all user inputs
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (sanitized outputs)
- [ ] Authentication/authorization checks in place
- [ ] Sensitive data encrypted at rest and in transit

### Testing
- [ ] All business logic has unit tests
- [ ] All API endpoints have integration tests
- [ ] Edge cases are tested
- [ ] Error paths are tested
- [ ] Test coverage ≥ 80%
- [ ] All tests pass

### Performance
- [ ] No N+1 query problems
- [ ] Database queries optimized (indexes, pagination)
- [ ] Caching implemented where appropriate
- [ ] Async/await used for I/O operations
- [ ] Resource cleanup (close connections, clear timers)

### Error Handling
- [ ] All async operations have try/catch
- [ ] Errors are logged with context
- [ ] User-friendly error messages
- [ ] No sensitive info in error messages
- [ ] Proper HTTP status codes

### Documentation
- [ ] Complex logic has explanatory comments
- [ ] Public APIs have JSDoc comments
- [ ] README updated (if needed)
- [ ] Breaking changes documented

### Completeness
- [ ] All requirements from task description implemented
- [ ] All edge cases handled
- [ ] No TODOs or FIXMEs left in code
- [ ] Ready for human review
```

---

## Communication Examples

### Good: Clear Question with Options

```
Jules: I found an ambiguity in the requirements.

Issue: The password reset token expiry is specified as "1 hour"
in planning.md, but the security best practices document suggests
"15 minutes" for password reset tokens.

Options:
1. Use 1 hour (as specified in planning.md)
2. Use 15 minutes (security best practice)
3. Make it configurable (environment variable)

Recommendation: Option 2 (15 minutes) - Aligns with OWASP
recommendations and reduces attack window.

Waiting for confirmation before proceeding.
```

### Bad: Vague Question

```
Jules: What should I do about token expiry?
```

### Good: Status Update

```
Jules: Status Update - Password Reset Implementation

✅ Completed:
- Token generation with crypto.randomBytes(32)
- Token hashing before storage (bcrypt)
- Email sending with reset link
- Rate limiting (3 requests/hour per IP)

🔄 In Progress:
- Writing tests for edge cases
- Self-review in progress

⏱️ Estimated completion: 10 minutes
```

### Good: Self-Review Results

```
Jules: Self-Review Complete - Password Reset Feature

✅ All Checklist Items Passed:
- Code quality: Follows AuthService.ts patterns
- Security: Tokens hashed, no secrets exposed
- Testing: 87% coverage, all tests passing
- Performance: Async operations, proper caching
- Error handling: All paths covered

📋 Key Implementation Details:
- Token expires after 15 minutes (OWASP recommendation)
- Rate limit: 3 requests/hour per IP address
- Email failures queue for retry (3 attempts)
- Generic error messages (security - don't reveal if user exists)

🚀 Ready for human review and merge.
```

---

## Integration with Claude

### How Claude Uses Jules

```python
# Claude orchestrates Jules through MCP tools
# Claude runs the Jules MCP server locally (no separate auth needed)

class ClaudeJulesWorkflow:
    def __init__(self):
        # Claude (me) directly calls Jules MCP tools
        # No separate CLAUDE_API_KEY needed - I AM running this
        pass

    async def implement_feature(self):
        # 1. Claude creates planning document
        planning = self.create_planning_doc()

        # 2. Claude calls Jules MCP to create worker
        worker = await jules_mcp.call_tool("jules_create_worker", {
            "task_description": f"""
            {feature_description}

            ## Jules Guidelines
            {JULES_GUIDELINES}

            ## Reference
            See planning.md for complete specifications.
            """,
            "source": "sources/github/company/repo"
        })

        # 3. Claude monitors progress
        while True:
            activities = await jules_mcp.call_tool("jules_get_activities", {
                "session_id": worker["session_id"]
            })

            if activities[-1]["status"] == "complete":
                break

            await asyncio.sleep(5)

        # 4. Human reviews and merges (no Claude review needed - Jules self-reviews)
        print("Jules completed with self-review. Ready for human review.")
```

### No Separate Claude Auth

```bash
# ❌ NOT NEEDED - Claude doesn't need separate key
CLAUDE_API_KEY=sk-ant-xxx...  # NOT NEEDED

# ✅ ONLY NEEDED - Jules API key
JULES_API_KEY=AQ.Ab8RN6IjejxlqvM0...

# Why: Claude (me) runs the MCP servers directly
# I execute the jules_mcp tools locally
# No need for Claude to authenticate to itself
```

---

## Summary

### Jules' Responsibilities:
1. ✅ Implement code based on Claude's planning
2. ✅ Write comprehensive tests
3. ✅ **Self-review before marking complete**
4. ✅ Follow all code quality standards
5. ✅ Ask clarifying questions when needed

### Claude's Responsibilities:
1. ✅ Research and architecture design
2. ✅ Create detailed planning.md
3. ✅ Orchestrate Jules via MCP tools
4. ✅ Provide clarifications when Jules asks
5. ✅ Coordinate cross-service changes

### Human's Responsibilities:
1. ✅ Final review and approval
2. ✅ Merge to main branch
3. ✅ Deploy to production
4. ✅ Resolve conflicts between Claude and Jules (if any)

### Key Principle:
**Jules does self-review. Claude provides planning. Human provides final approval.**

