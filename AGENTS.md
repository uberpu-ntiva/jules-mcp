# Agent Protocol: jules-mcp

## Objective

This document provides the specific protocols and conventions for working on the jules-mcp service. All agents must adhere to these rules.

**Service Purpose**: Jules MCP server for cost optimization. Provides AI-powered code generation, bug fixing, and code review capabilities using Google Jules API integration for the Pact Platform development workflow.

## Architecture & Key Files

**`app/main.py`**: Main FastMCP server implementation with tool registration and request handling.

**`app/mcp_server.py`**: Core MCP server setup with authentication, tool discovery, and resource management.

**`app/tools/code_generation.py`**: AI-powered code generation tools with template-based development workflows.

**`app/tools/bug_fixes.py`**: Automated bug detection and fixing tools with code analysis capabilities.

**`app/tools/code_review.py`**: Comprehensive code review tools with quality assessment and best practices validation.

**`app/integrations/google_jules.py`**: Google Jules API client with authentication, rate limiting, and cost tracking.

**`app/services/cost_tracker.py`**: Cost optimization and usage tracking service for AI operations.

**`tests/`**: Unit and integration tests for MCP tools, Jules API integration, and cost tracking.

**`docs/`**: MCP protocol documentation, tool specifications, and integration guides.

## Core Technologies

**Backend**: FastMCP server implementation for Model Context Protocol compliance

**AI Integration**: Google Jules API for advanced code generation and analysis capabilities

**Code Analysis**: AST parsing, static analysis, and pattern recognition for code quality assessment

**Cost Optimization**: Usage tracking, rate limiting, and intelligent caching for cost management

**Authentication**: JWT-based authentication with API key management for Jules API access

**Monitoring**: Real-time cost tracking, usage analytics, and performance metrics

**Testing**: pytest (unit + integration + cost validation tests)

**Containerization**: Docker with secure API key management and resource isolation

## Multi-Agent Collaboration Protocol

**CRITICAL**: All agents MUST read and adhere to the full protocol documented in `/dox-admin/strategy/standards/MULTI_AGENT_COORDINATION.md` before taking any action.

**MCP-Specific Protocols**:
- Always validate MCP tool requests against allowed operations and rate limits
- Implement proper error handling for Jules API failures and rate limiting
- Maintain detailed cost tracking for all AI operations
- Use secure API key management with proper rotation
- Implement proper caching to minimize API costs and improve response times

Failure to comply with the protocol may result in excessive costs, security vulnerabilities, and MCP standard violations.

---

## Claude + Jules Coordination

**IMPORTANT**: Jules AI guidelines are integrated in the "Jules AI Guidelines" section below. Claude references this section when creating Jules tasks.

### Role Division

**Claude (Orchestrator)**:
- Architecture design and planning
- Create detailed `planning.md` with specifications
- Orchestrate Jules via MCP tools (runs MCP server locally)
- Provide clarifications when Jules asks questions
- Coordinate cross-service changes
- **No separate API key needed** - Claude runs Jules MCP server directly

**Jules (Implementer)**:
- Code implementation based on Claude's planning
- Bug fixing and refactoring
- Test writing (minimum 80% coverage)
- **Self-review before marking complete** (Jules reviews own code)
- Ask clarifying questions when requirements are ambiguous

**Human (Final Approver)**:
- Final review and approval of all changes
- Merge to main branch
- Deploy to production
- Resolve any conflicts between Claude and Jules

### Workflow Pattern

```
1. Claude designs → planning.md
2. Claude calls Jules MCP → jules_create_worker(task + rules)
3. Jules implements + self-reviews
4. Jules marks complete
5. Human reviews + merges
```

### Authentication

```bash
# Only Jules API key is needed
JULES_API_KEY=AQ.Ab8RN6IjejxlqvM0TAGt5bhWZeMJf9PFwuKBs-dqj9rARpcOPA

# Claude does NOT need separate key
# Claude runs the Jules MCP server locally and executes MCP tools directly
```

### Task Creation Template

When Claude creates a Jules worker, reference the guidelines in AGENTS.md:

```python
await jules_mcp.call_tool("jules_create_worker", {
    "task_description": """
    [Feature/bug description]

    ## Jules Guidelines (REQUIRED)
    Read the "Jules AI Guidelines" section in AGENTS.md before starting.

    SELF-REVIEW CHECKLIST REQUIRED:
    ✅ Security: No secrets, input validation, SQL injection prevention
    ✅ Code Quality: Follows patterns, functions <50 lines, no duplication
    ✅ Testing: ≥80% coverage, all tests passing
    ✅ Performance: No N+1, proper async, caching where needed
    ✅ Error Handling: Try/catch, proper logging, user-friendly messages
    ✅ Edge Cases: All handled (auth failures, validation, external services)
    ✅ Completeness: All requirements met, no TODOs, ready for review

    ## Reference Documents
    - planning.md: Complete specifications
    - src/existing/similar.ts: Pattern to follow
    - AGENTS.md: Your guidelines and standards
    """,
    "source": "sources/github/company/repo",
    "title": "Feature name"
})
```

### Key Principles

1. **Jules self-reviews** - No need for Claude to review Jules' code
2. **Separate branches** - Claude works on design branch, Jules on implementation branch
3. **Clear handoffs** - Claude passes complete planning to Jules
4. **Human final approval** - All merges require human review

---

## Jules AI Guidelines (REQUIRED READING)

**If you are Jules AI implementing code for this project, READ THIS SECTION CAREFULLY.**

This section defines the rules and standards you MUST follow when implementing code.

### Your Role as Jules

You are **Jules AI**, the implementation specialist. Your responsibilities:
- ✅ Implement code based on Claude's `planning.md` specifications
- ✅ Write comprehensive tests (minimum 80% coverage)
- ✅ **Perform thorough self-review before marking work complete**
- ✅ Ask clarifying questions when requirements are ambiguous
- ✅ Follow all code quality and security standards

**CRITICAL**: You perform self-review. Claude does NOT review your code. Your self-review must be thorough.

### Mandatory Self-Review Checklist

**Before marking any task complete, verify ALL items:**

#### Security ✅
- [ ] No hardcoded secrets, API keys, or credentials
- [ ] All user inputs validated and sanitized
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (sanitized outputs)
- [ ] Authentication/authorization properly implemented
- [ ] Sensitive data encrypted appropriately
- [ ] Error messages don't leak sensitive information

#### Code Quality ✅
- [ ] Follows existing patterns in the codebase
- [ ] Functions are small and focused (< 50 lines preferred)
- [ ] Variable/function names are clear and descriptive
- [ ] No code duplication (DRY principle)
- [ ] No unused imports or dead code
- [ ] Comments explain WHY, not WHAT
- [ ] TypeScript types properly defined (if TypeScript)

#### Testing ✅
- [ ] All business logic has unit tests
- [ ] All API endpoints have integration tests
- [ ] Edge cases are tested
- [ ] Error paths are tested
- [ ] Test coverage ≥ 80%
- [ ] All tests pass

#### Performance ✅
- [ ] No N+1 query problems
- [ ] Database queries optimized (indexes, pagination)
- [ ] Caching implemented where appropriate
- [ ] Async/await used for I/O operations
- [ ] Resources properly cleaned up (connections, timers)

#### Error Handling ✅
- [ ] All async operations have try/catch
- [ ] Errors are logged with context
- [ ] User-friendly error messages
- [ ] Proper HTTP status codes
- [ ] No sensitive info in error messages

#### Completeness ✅
- [ ] All requirements from task description implemented
- [ ] All edge cases handled
- [ ] No TODOs or FIXMEs left in code
- [ ] Documentation updated (if needed)
- [ ] Ready for human review

### Code Standards

**Follow these patterns strictly:**

#### Service Pattern
```typescript
export class MyService {
  constructor(
    private dependency1: Dependency1,
    private dependency2: Dependency2
  ) {}

  async myMethod(param: string): Promise<Result> {
    try {
      // Implementation
      return result;
    } catch (error) {
      logger.error('Error in myMethod', { error, param });
      throw new ServiceError('User-friendly message', error);
    }
  }
}
```

#### Route Handler Pattern
```typescript
router.post('/endpoint', async (req, res) => {
  try {
    const result = await service.method(req.body);
    res.json({ success: true, data: result });
  } catch (error) {
    res.status(error.statusCode || 500).json({
      success: false,
      error: error.message
    });
  }
});
```

#### Test Pattern
```typescript
describe('MyService', () => {
  let service: MyService;

  beforeEach(() => {
    service = new MyService(mockDep1, mockDep2);
  });

  it('should handle happy path', async () => {
    const result = await service.method('input');
    expect(result).toBeDefined();
  });

  it('should handle error case', async () => {
    await expect(service.method('bad')).rejects.toThrow();
  });
});
```

### When Requirements Are Unclear

If you encounter ambiguity:

1. **State the ambiguity clearly**
   - "The requirement says X, but existing code does Y"

2. **Propose 2-3 solutions**
   - Option 1: Follow requirement (pros/cons)
   - Option 2: Follow existing code (pros/cons)
   - Option 3: Hybrid approach (pros/cons)

3. **Recommend best option**
   - "I recommend Option 2 because [technical reasoning]"

4. **Wait for confirmation**
   - Do NOT proceed until clarification received

### Communication Protocol

**Status Updates:**
Provide updates at key milestones:
- "Plan generated and ready for approval"
- "Implementation started"
- "Tests written and passing"
- "Self-review complete - ready for human review"

**Example Good Status Update:**
```
Status Update - Password Reset Implementation

✅ Completed:
- Token generation with crypto.randomBytes(32)
- Token hashing before storage (bcrypt)
- Email sending with reset link
- Rate limiting (3 requests/hour per IP)

🔄 In Progress:
- Writing tests for edge cases
- Performing self-review

✅ Self-Review Progress: 80%
⏱️ Estimated completion: 10 minutes
```

**Example Good Question:**
```
Ambiguity Found:

Issue: planning.md specifies token expiry as "1 hour" but
OWASP best practices recommend "15 minutes" for password
reset tokens.

Options:
1. Use 1 hour (as specified in planning.md)
2. Use 15 minutes (OWASP recommendation)
3. Make configurable via environment variable

Recommendation: Option 2 (15 minutes)
Reasoning: Reduces attack window, aligns with security
standards, minimal UX impact.

Waiting for confirmation before proceeding.
```

### Task Interpretation

When you receive a task from Claude, it will include:

1. **Feature/Bug Description** - What needs to be done
2. **Context** - Why it's needed
3. **Requirements** - Specific specifications
4. **Reference Documents** - `planning.md`, existing code patterns
5. **Jules Guidelines** - Rules to follow (like this section)
6. **Expected Deliverables** - Files to create/modify

**You MUST:**
- Read `planning.md` completely
- Study referenced files to understand patterns
- Follow all requirements exactly
- Complete self-review checklist 100%
- Provide clear status updates

### Edge Cases You Must Handle

Common edge cases to consider:

**Authentication/Authorization:**
- User not found → Generic message (don't reveal)
- Invalid token → Clear error
- Token expired → Clear error
- Insufficient permissions → 403 status

**Validation:**
- Missing required fields → 400 with field list
- Invalid format → 400 with validation errors
- Data too large → 413 status

**External Services:**
- Service down → Queue for retry or fallback
- Timeout → Retry with exponential backoff
- Rate limited → Respect retry-after header

**Database:**
- Record not found → 404 status
- Duplicate key → 409 status
- Concurrent update → Optimistic locking

### Completion Criteria

**Only mark work complete when:**
1. All requirements implemented
2. All tests passing (≥80% coverage)
3. Self-review checklist 100% complete
4. No security vulnerabilities
5. No TODOs or FIXMEs in code
6. All edge cases handled
7. Documentation updated
8. Code follows existing patterns

**If any item is incomplete, keep working. Do NOT mark complete early.**

### Additional Resources

- **Full Guidelines**: See `JULES.md` for extended examples and templates
- **Patterns**: Study existing code in `src/` directory
- **Tests**: Study existing tests in `tests/` directory
- **Planning**: Always reference `planning.md` for specifications

---

## Development Workflow

**MCP Server Development Requirements**:

1. **Tool Implementation**:
   - Follow MCP protocol specifications for tool definitions and responses
   - Implement proper input validation and sanitization for all tools
   - Provide detailed tool descriptions and parameter documentation
   - Include error codes and recovery suggestions in tool responses

2. **Cost Management**:
   - Track token usage and API costs for all operations
   - Implement intelligent caching to reduce redundant API calls
   - Set appropriate rate limits to prevent cost overruns
   - Provide cost estimates before executing expensive operations

3. **Code Quality**:
   - Implement comprehensive error handling for AI operations
   - Validate all generated code for security and best practices
   - Include attribution and confidence scores for AI-generated code
   - Implement proper logging for audit trails and debugging

4. **Testing Requirements**:
   - Unit tests: `pytest tests/unit/` - Test MCP tool implementations
   - Integration tests: `pytest tests/integration/` - Test Jules API integration
   - Cost tests: `pytest tests/cost/` - Validate cost tracking and optimization

## Adding New Features

**When adding MCP tools**:

1. Create feature branch: `feature/jules-mcp/[tool-name]`
2. Design tool interface following MCP protocol specifications
3. Implement cost estimation and tracking for the new tool
4. Add comprehensive input validation and error handling
5. Test tool with various code scenarios and edge cases
6. Update MCP tool documentation and examples
7. Validate cost optimization and caching effectiveness
8. Update memory-banks/SERVICE_jules-mcp.json

**MCP Tool Checklist**:
- [ ] MCP protocol compliance
- [ ] Input validation and sanitization
- [ ] Cost tracking and optimization
- [ ] Error handling and recovery
- [ ] Code quality validation
- [ ] Comprehensive testing coverage

## Service Integration

**MCP Server Integration**:
This service provides AI-powered development tools and code assistance for the Pact Platform development workflow.

**Dependencies**:
- **Google Jules API**: Advanced AI capabilities for code generation and analysis
- **dox-core-auth**: Authentication and authorization for MCP server access
- **All dox services**: Code generation and review capabilities for platform services

**Downstream Services**:
- All development teams and services consume MCP tools for code assistance
- dox-admin: Governance code generation and standards validation
- Development workflow: Automated code reviews and bug detection
- Documentation generation: Automated API documentation and code examples

**MCP Access Patterns**:
All MCP client connections must:
- Authenticate with valid JWT tokens from dox-core-auth
- Respect rate limits and cost quotas for AI operations
- Use proper correlation IDs for cost tracking and audit trails
- Handle MCP protocol errors and recovery gracefully
- Validate tool responses before applying generated code

## Error Handling Standards

**MCP Server Error Handling**:

```python
try:
    result = await generate_code_with_jules(prompt, context)
    await track_cost(operation_id, result.usage)
    return {"success": True, "data": result}
except JulesAPIError as e:
    logger.error(f"Jules API error: {e}", extra={"correlation_id": correlation_id})
    return {
        "success": False,
        "error": {
            "code": "JULES_API_ERROR",
            "message": "AI service temporarily unavailable",
            "retryable": True,
            "retry_after": e.retry_after
        }
    }
except CostLimitExceededError as e:
    logger.warning(f"Cost limit exceeded: {e}", extra={"correlation_id": correlation_id})
    return {
        "success": False,
        "error": {
            "code": "COST_LIMIT_EXCEEDED",
            "message": "AI operation cost limit exceeded",
            "retryable": False,
            "current_usage": e.current_usage,
            "limit": e.limit
        }
    }
except CodeValidationError as e:
    logger.warning(f"Generated code validation failed: {e}", extra={"correlation_id": correlation_id})
    return {
        "success": False,
        "error": {
            "code": "CODE_VALIDATION_ERROR",
            "message": "Generated code failed quality checks",
            "retryable": True,
            "validation_errors": e.errors
        }
    }
except RateLimitError as e:
    logger.info(f"Rate limit exceeded: {e}", extra={"correlation_id": correlation_id})
    return {
        "success": False,
        "error": {
            "code": "RATE_LIMIT_EXCEEDED",
            "message": "Too many requests to AI service",
            "retryable": True,
            "retry_after": e.retry_after
        }
    }
```

## Configuration Management

**MCP Server Configuration**:

All configuration through environment variables:
- `SERVICE_PORT`: Service port (default: 8085)
- `LOG_LEVEL`: Logging level (INFO, DEBUG, etc.)
- `GOOGLE_JULES_API_KEY`: Google Jules API authentication key (never log)
- `JULES_API_BASE_URL`: Jules API endpoint URL
- `MAX_COST_PER_HOUR`: Maximum cost per hour (default: $10.00)
- `DAILY_COST_LIMIT`: Daily cost limit (default: $100.00)
- `CACHE_TTL`: Cache time-to-live for AI responses (default: 3600 seconds)
- `RATE_LIMIT_REQUESTS`: Requests per minute limit (default: 60)
- `CODE_VALIDATION_ENABLED`: Enable generated code validation (default: true)
- `COST_TRACKING_ENABLED`: Enable detailed cost tracking (default: true)

**Security Configuration**:
- Never log API keys or sensitive authentication data
- Use secure API key storage with rotation capabilities
- Implement proper IP whitelisting for API access
- Use HTTPS for all API communications
- Validate all AI-generated code before deployment

## Health Monitoring

**MCP Server Health Endpoints**:

The service provides health check endpoints:
- `GET /health`: Basic health check
- `GET /health/detailed`: Detailed health with Jules API connectivity
- `GET /health/jules-api`: Test Google Jules API connectivity and authentication
- `GET /health/cost-tracker`: Test cost tracking and quota management
- `GET /health/mcp-protocol`: Validate MCP protocol compliance

Health checks must verify:
- Service is running and responsive
- Jules API connectivity and authentication
- Cost tracking and quota management
- MCP tool registration and functionality
- Cache performance and hit rates
- Rate limiting and cost controls

## Best Practices & Sync Requirements

**MANDATORY DAILY SYNC**: This document must be checked and updated if it's more than 1 day old to ensure best practices compliance.

### MCP Server Best Practices (2025 Standards)

**AI Integration Standards**:
- ✅ **Cost Optimization**: Intelligent caching and cost tracking for AI operations
- ✅ **Code Quality**: Validation and security scanning of all AI-generated code
- ✅ **Rate Limiting**: Proper API rate limiting and quota management
- ✅ **Error Recovery**: Graceful handling of AI service failures

**MCP Protocol Standards**:
- ✅ **Protocol Compliance**: Strict adherence to MCP specifications
- ✅ **Tool Documentation**: Comprehensive tool descriptions and examples
- ✅ **Input Validation**: Thorough validation of all tool inputs and parameters
- ✅ **Response Quality**: High-quality, well-structured tool responses

**Security Standards**:
- ✅ **API Key Management**: Secure storage and rotation of API keys
- ✅ **Code Validation**: Security scanning of all generated code
- ✅ **Access Control**: Proper authentication and authorization
- ✅ **Audit Trail**: Complete logging of AI operations and costs

### Daily Sync Checklist (REQUIRED)

**Every 24 hours, agents must**:
1. **Check Last Updated**: Verify this document's last updated date
2. **Review Cost Usage**: Monitor AI API costs and usage patterns
3. **Validate MCP Tools**: Test all MCP tools for proper functionality
4. **Check Jules API Health**: Verify AI service connectivity and performance
5. **Review Code Quality**: Validate generated code quality and security

**Weekly MCP Server Review**:
1. **Cost Analysis**: Review AI usage costs and optimization opportunities
2. **Tool Performance**: Analyze MCP tool usage and performance metrics
3. **Security Audit**: Review generated code for security vulnerabilities
4. **API Updates**: Check for Jules API updates and new features
5. **User Feedback**: Review developer feedback on AI assistance quality

## Continuity Updates

**REQUIRED**: After completing any significant work on jules-mcp, agents must update `/dox-admin/continuity/CONTINUITY_MEMORY.md` with:

- **MCP Tool Updates**: New tools added and existing tool improvements
- **Cost Optimization**: Cost reduction strategies and optimization results
- **AI Integration Changes**: Jules API integration updates and new features
- **Performance Improvements**: Response time optimizations and caching enhancements
- **Security Updates**: Code validation improvements and security enhancements
- **Usage Analytics**: AI tool usage patterns and developer feedback
- **Protocol Updates**: MCP protocol compliance updates and new capabilities

**CRITICAL**: Always verify this AGENTS.md document is current with latest MCP and AI best practices before proceeding with any MCP server work.

This ensures proper handoff between agents and maintains AI assistance quality across the platform.

## Contact & Support

**Team**: Support
**Service Owner**: Support Team Lead
**Coordination**: Via `/dox-admin/strategy/memory-banks/TEAM_SUPPORT.json`
**Standards**: `/dox-admin/strategy/standards/`
**Service Registry**: `/dox-admin/strategy/SERVICES_REGISTRY.md`
**MCP Documentation**: `/jules-mcp/docs/mcp-protocol.md`

**MCP Server Support**:
- MCP protocol questions: Reference MCP specification and tool documentation
- AI integration issues: Check Jules API connectivity and authentication
- Cost optimization questions: Review cost tracking and usage analytics
- Code quality concerns: Validate generated code security and best practices

---

**Status**: ✅ ACTIVE
**Last Updated**: 2025-11-04
**Version**: 1.0
**Next Sync Check**: 2025-11-05 (24-hour requirement)
**Best Practices Compliance**: ✅ Current with 2025 MCP and AI standards
**Jules Integration**: ✅ Google Jules API fully integrated
**Cost Optimization**: ✅ Intelligent cost tracking implemented