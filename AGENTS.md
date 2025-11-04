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

## Claude's Limitations (CRITICAL REMINDER)

**IMPORTANT**: Claude (the orchestrator) has significant limitations. Both Jules and humans must understand what Claude CANNOT do.

### What Claude CANNOT Do

#### ❌ Cannot Execute Code
- **Cannot run** the code Jules generates
- **Cannot test** the actual functionality
- **Cannot verify** that code actually works
- **Cannot execute** commands that Jules implements
- **Cannot validate** runtime behavior

**Example:**
```
Claude can: Read code and understand logic
Claude CANNOT: Run `npm test` or execute the code to verify it works
```

#### ❌ Cannot Access Live Systems
- **Cannot connect** to databases
- **Cannot query** production systems
- **Cannot access** live APIs
- **Cannot verify** deployed services
- **Cannot test** in real environments

**Example:**
```
Claude can: Design database schema
Claude CANNOT: Connect to PostgreSQL and verify the schema exists
```

#### ❌ Cannot Verify Test Results
- **Cannot run** test suites
- **Cannot see** test output
- **Cannot verify** test coverage
- **Cannot execute** integration tests
- **Cannot validate** that tests actually pass

**Example:**
```
Claude can: Review test code for completeness
Claude CANNOT: Run pytest and see if tests pass
```

#### ❌ Cannot Perform Runtime Validation
- **Cannot verify** API responses
- **Cannot test** authentication flows
- **Cannot validate** error handling in practice
- **Cannot check** performance metrics
- **Cannot monitor** system behavior

**Example:**
```
Claude can: Design error handling logic
Claude CANNOT: Make actual API calls to verify errors are handled correctly
```

#### ❌ Cannot Review Implementation Quality (Thoroughly)
- **Cannot run** linters
- **Cannot execute** type checkers
- **Cannot verify** code compiles
- **Cannot test** in browsers
- **Cannot validate** runtime dependencies

**Example:**
```
Claude can: Read code and spot obvious issues
Claude CANNOT: Run `tsc` to verify TypeScript types are correct
```

### What Claude CAN Do

#### ✅ Architecture & Design
- Design system architecture
- Create planning documents
- Specify requirements
- Define APIs and interfaces

#### ✅ Code Review (Limited)
- Read and understand code
- Spot logical errors
- Identify security concerns
- Suggest improvements
- **BUT**: Cannot verify code actually works

#### ✅ Orchestration
- Create Jules workers via MCP
- Monitor Jules' progress
- Provide clarifications
- Coordinate across services
- Manage workflow

#### ✅ Documentation
- Write architecture docs
- Create planning documents
- Document decisions
- Explain concepts

### Why This Matters

#### For Jules:
You **MUST** perform thorough self-review because Claude cannot:
- ❌ Run your tests
- ❌ Execute your code
- ❌ Verify it works
- ❌ Catch runtime errors

**Your self-review is the ONLY validation before human review.**

#### For Humans:
You are the final validator because:
- ❌ Claude cannot test
- ❌ Jules is self-reviewing
- ✅ You MUST verify code works
- ✅ You MUST run tests
- ✅ You MUST validate functionality

### Workflow Implications

```
1. Claude: Designs architecture
   ✅ Can do this well

2. Jules: Implements code + self-reviews
   ⚠️ Must be thorough - Claude cannot verify

3. Claude: Reads code, spots obvious issues
   ⚠️ Limited - cannot run/test

4. Human: Final validation
   ✅ CRITICAL - runs tests, validates, approves
```

### Critical Reminders

**To Jules:**
> Since Claude cannot test your code, your self-review checklist
> is critical. Complete ALL items before marking work done.

**To Claude (self-reminder):**
> I cannot verify that code works. I can only orchestrate,
> design, and provide limited code review. Trust Jules'
> self-review and defer to human for final validation.

**To Humans:**
> Neither Claude nor Jules can fully validate the code works
> in practice. You must run tests, verify functionality,
> and approve/reject based on actual execution.

---

## Environment Limitations & Boundaries (CRITICAL)

**IMPORTANT**: Understanding what Claude and Jules can and cannot do in this specific environment is critical to avoid common mistakes and failed expectations.

### Claude's Environment Capabilities

#### ✅ Claude CAN Do in This Environment:
- **Read/Write Files**: Full filesystem access to `/workspace/` and all services
- **Edit Code**: Modify any source files across all services
- **Create Files**: New files, documentation, configuration
- **Delete Files**: Remove files (with caution)
- **Execute Commands**: Run bash commands via Bash tool (with limitations)
- **Install Packages**: npm, pip, and other package managers
- **Run Tests**: Execute test suites via bash commands
- **Read Git History**: Examine code changes and patterns
- **Use MCP Tools**: Run Jules MCP server locally and call tools
- **Write Documentation**: Create comprehensive documentation
- **Generate Code**: Create new implementations across services

#### ✅ Claude CAN Do in This Environment:
- **Git Operations**: Read git status, history, and files (this IS a git repository)
- **Network Requests**: Can make HTTP requests to external APIs (GitHub, web search)
- **Web Search**: Can search DuckDuckGo and extract search results
- **External APIs**: Can call real public APIs (GitHub, weather, etc.)
- **Request Patterns**: Can create RPS (Request Pattern Specifications)
- **Live Testing**: Can test code against real external systems
- **File Operations**: Full filesystem access within allowed repositories
- **Script Execution**: Run Python, Node.js, bash scripts

#### ❌ Claude CANNOT Do in This Environment:
- **Docker Operations**: Docker is not available
- **Production Database Access**: Cannot connect to production databases
- **CI/CD Integration**: Cannot interact with GitHub Actions, etc.
- **Production Deployment**: Cannot deploy to production systems
- **Internal Company Systems**: Cannot access internal company systems
- **File Outside Repos**: Cannot create files outside the 24 approved repositories

### Jules MCP Server Capabilities

#### ✅ Jules MCP Server CAN Do:
- **Local Execution**: Run locally with proper Python environment
- **Tool Registration**: All 5 tools, 3 resources, 2 prompts available
- **MCP Protocol**: Full MCP compliance for tool discovery and execution
- **Cost Tracking**: Monitor and track API usage
- **Error Handling**: Comprehensive error handling and recovery
- **Async Operations**: Full async/await support
- **Worker Management**: Create and manage Jules workers
- **Activity Monitoring**: Track worker progress and status

#### ❌ Jules MCP Server CANNOT Do:
- **Real API Calls**: Without valid JULES_API_KEY
- **Production Access**: No access to production systems
- **Database Operations**: Cannot connect to production databases
- **External Integrations**: Limited access to external services
- **Network Operations**: Limited network access in this environment
- **Real-time Processing**: No real production workload

### Common Mistakes to Avoid

#### ❌ Claude Mistakes:
1. **Trying Docker Operations**
   ```bash
   # ❌ Claude will try this and fail
   docker build -t app .
   docker run app

   # ✅ Claude should do this instead
   npm install
   npm run build
   node dist/index.js
   ```

2. **Assuming Production Deployment**
   ```
   # ❌ Claude will assume this works
   "Deploy to production by running deploy.sh"

   # ✅ Claude should do this instead
   "Code changes ready for deployment"
   "Human must deploy manually to production"
   ```

3. **Assuming Unlimited File Access**
   ```
   # ❌ Claude will try this and fail
   touch /root/file.txt  # Cannot write outside approved repos

   # ✅ Claude should do this instead
   touch jules-mcp/file.txt  # Within approved repositories
   ```

#### ❌ Jules MCP Mistakes:
1. **Assuming Real Jules API**
   ```
   # ❌ Jules will try this and fail without real key
   "Call Google Jules API for code generation"

   # ✅ Jules should do this instead
   "Code generation requires valid JULES_API_KEY"
   "Local testing with mock responses only"
   ```

2. **Production Database Access**
   ```python
   # ❌ Jules will try this and fail
   connection = psycopg2.connect("postgresql://prod-db...")

   # ✅ Jules should do this instead
   # Use database configuration patterns
   # Actual connection requires production access
   ```

### Safe Working Patterns

#### ✅ Safe Claude Workflow:
```bash
# 1. Read and understand existing code
find . -name "*.py" -o -name "*.ts" | head -10

# 2. Make changes locally
npm install
npm run dev

# 3. Test locally (if possible)
npm test

# 4. Create comprehensive documentation
echo "Implementation complete. Human review required for deployment."

# 5. Note deployment requirements
echo "Deployment requires:"
echo "- Valid JULES_API_KEY in environment"
echo "- Production database access"
echo "- CI/CD pipeline execution"
```

#### ✅ Safe Jules MCP Workflow:
```python
# 1. Local development only
if os.getenv("JULES_API_KEY"):
    jules_client = JulesAPIClient()
else:
    print("Development mode - no real API calls")
    return mock_response

# 2. Error handling for missing resources
try:
    result = await database.query(query)
except DatabaseConnectionError:
    print("Database not available in this environment")
    return mock_data

# 3. Clear communication about limitations
print("✅ Code implemented correctly")
print("⚠️  Production access required for testing")
print("👤 Human review needed before deployment")
```

### Environment Verification Commands

When working in this environment, Claude should run these verification commands:

```bash
# Check what's available
echo "=== Environment Check ==="
echo "Node.js: $(node --version)"
echo "npm: $(npm --version)"
echo "Python: $(python3 --version)"
echo "pip: $(pip --version 2>/dev/null || echo 'not available')"
echo "Docker: $(docker --version 2>/dev/null || echo 'not available')"
echo "Git: $(git --version 2>/dev/null || echo 'not available')"
echo "cURL: $(curl --version | head -1)"

# Check file structure
echo ""
echo "=== File Structure ==="
pwd
ls -la | head -20

# Check current working directory contents
echo ""
echo "=== Current Services ==="
ls -1 | grep "^dox-" | sort
```

### Deployment Reality Check

Before suggesting deployment, Claude should run:

```bash
# Check deployment prerequisites
echo "=== Deployment Prerequisites ==="
echo "Git repository: $(git rev-parse --is-inside-work-tree 2>/dev/null || echo 'NO - This is not a git repository')"
echo "Docker: $(docker --version >/dev/null 2>&1 && echo 'YES' || echo 'NO')"
echo "Production config: $([ -f .env.production ] && echo 'YES' || echo 'NO')"
echo "CI/CD pipeline: $([ -f .github/workflows/ ] && echo 'YES' || echo 'NO')"

echo ""
echo "=== Deployment Reality ==="
echo "Manual deployment required - No automated deployment available"
echo "Production deployment requires human intervention"
```

### File System Rights and Permissions

#### ✅ Safe File Operations:
```bash
# Claude can do these safely
mkdir new-feature
touch new-feature/code.ts
echo "implementation" > new-feature/code.ts
cp existing-pattern.ts new-feature/
rm old-file.ts  # After confirmation

# These are always safe
read_file.py
list_files.sh
create_documentation.md
```

#### ❌ Risky File Operations:
```bash
# Claude should avoid or be very careful
rm -rf /  # NEVER do this
chmod -R 777 .  # Dangerous
sudo commands  # Not available anyway
systemd services  # Not available in this environment
```

### Testing Realities

#### ✅ Testing Claude Can Do:
```bash
# Unit tests
npm test
pytest tests/

# Build verification
npm run build
tsc --noEmit

# Linting
npm run lint
eslint src/

# Type checking
npm run type-check
```

#### ❌ Testing Claude Cannot Do:
```bash
# Integration tests requiring external services
npm run test:integration  # If it calls real APIs

# End-to-end tests
npm run test:e2e  # Requires real browser/services

# Database tests
npm run test:db  # Requires real database connection

# Network tests
npm run test:api  # Requires real server deployment
```

#### ❌ Repository Restrictions:
Claude is RESTRICTED to only these repositories and cannot create files outside them:
- **DOX**
- **dox-tmpl-pdf-recognizer**
- **dox-pact-manual-upload**
- **dox-batch-assembly**
- **jules-mcp**
- **dox-admin**
- **dox-rtns-barcode-matcher**
- **dox-gtwy-main**
- **dox-tmpl-field-mapper**
- **dox-data-etl-service**
- **dox-core-auth**
- **dox-auto-workflow-engine**
- **dox-core-rec-engine**
- **dox-data-distrib-service**
- **dox-data-aggregation-service**
- **dox-auto-lifecycle-service**
- **dox-actv-service**
- **dox-actv-listener**
- **dox-core-store**
- **dox-esig-webhook-listener**
- **dox-esig-service**
- **dox-rtns-manual-upload**
- **dox-tmpl-pdf-upload**
- **dox-tmpl-service**
- **test-jules**
- **dox-mcp-server**

**Important**: Claude cannot create files in `/workspace/` root or anywhere outside these approved repositories.

---

## Jules AI Guidelines (REQUIRED READING)

**If you are Jules AI implementing code for this project, READ THE CENTRALIZED STANDARDS FIRST.**

### Centralized Standards (MUST READ)

**PRIMARY DOCUMENT**: `/dox-admin/strategy/standards/JULES_AI_STANDARDS.md`

This document contains:
- ✅ Your role as Jules
- ✅ Mandatory self-review checklist (Security, Code Quality, Testing, Performance, Error Handling, Completeness)
- ✅ Code standards and patterns (TypeScript, Python)
- ✅ Communication protocol
- ✅ Edge cases to handle
- ✅ Completion criteria

**CRITICAL**: You perform self-review. Claude does NOT review your code. Your self-review must be thorough.

### Service-Specific Guidelines for jules-mcp

**In addition to the centralized standards, follow these jules-mcp specific requirements:**

#### Jules MCP Service Context
- This service provides MCP (Model Context Protocol) server functionality
- Integrates with Google Jules API for AI-powered code generation
- Cost optimization and tracking is critical
- All MCP tools must follow protocol specifications

#### Specific Standards for This Service
- **Cost Tracking**: Every Jules API call must be tracked and logged
- **Rate Limiting**: Respect Google Jules API rate limits
- **MCP Protocol**: Strict adherence to MCP specifications
- **Error Recovery**: Graceful handling of Jules API failures
- **Caching**: Implement intelligent caching to reduce API costs

#### Reference Files
- Study existing MCP tools in `src/jules_mcp/server.py`
- Follow patterns from existing Jules API client code
- Reference `TESTING_GUIDE.md` for testing approach

### Quick Checklist Summary

**Before marking complete** (Full checklist in JULES_AI_STANDARDS.md):
- ✅ Security: No secrets, input validation, SQL injection prevention
- ✅ Code Quality: Follows patterns, <50 line functions, no duplication
- ✅ Testing: ≥80% coverage, all tests passing
- ✅ Performance: No N+1, proper async, caching
- ✅ Error Handling: Try/catch, logging, user-friendly messages
- ✅ Completeness: All requirements, no TODOs, ready for review

**Full details**: See `/dox-admin/strategy/standards/JULES_AI_STANDARDS.md`

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