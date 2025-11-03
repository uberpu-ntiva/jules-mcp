# Jules MCP Server - Testing Guide

## Prerequisites

### 1. Install Jules GitHub App
1. Go to https://github.com/apps/jules-ai
2. Click "Install" or "Configure"
3. Select the repository you want Jules to work on
4. Grant the necessary permissions

### 2. Get Your Source Path
After installing Jules on a repository, your source path will be:
```
sources/github/{owner}/{repo}
```

For example:
- `sources/github/mycompany/backend-api`
- `sources/github/username/my-project`

### 3. Verify Jules API Key
Your API key is already configured in `.env`:
```
JULES_API_KEY=AQ.Ab8RN6IjejxlqvM0TAGt5bhWZeMJf9PFwuKBs-dqj9rARpcOPA
```

## Testing the MCP Server

### Option 1: Manual Python Test

```bash
cd /workspace/cmhgo33qe028ytmimhtss1qm0/jules-mcp

python3 << 'SCRIPT'
import asyncio
import sys
sys.path.insert(0, 'src')

from jules_mcp.server import initialize_server, worker_manager, shutdown_server
from dotenv import load_dotenv

load_dotenv('.env')

async def test_with_real_repo():
    await initialize_server()
    
    # Replace with your actual repository
    GITHUB_OWNER = "YOUR_GITHUB_USERNAME"
    GITHUB_REPO = "YOUR_REPO_NAME"
    source = f"sources/github/{GITHUB_OWNER}/{GITHUB_REPO}"
    
    print(f"Creating worker with source: {source}")
    
    try:
        # Create a test worker
        session_id = await worker_manager.create_worker(
            prompt="Add a hello world function to the README",
            source=source,
            title="Test Task",
            github_branch="main"
        )
        
        print(f"✅ Worker created: {session_id}")
        
        # Wait for activities
        print("\nWaiting 10 seconds for Jules to generate a plan...")
        await asyncio.sleep(10)
        
        # Check status
        status = worker_manager.get_worker_status(session_id)
        print(f"\nWorker Status:")
        print(f"  State: {status['state']}")
        print(f"  Blocked: {status['is_blocked']}")
        if status['blocker_reason']:
            print(f"  Reason: {status['blocker_reason']}")
        
        # Get activities
        activities = await worker_manager.get_worker_activities(session_id)
        print(f"\nActivities: {len(activities)} found")
        for activity in activities:
            print(f"  - {activity.type.value}: {activity.title}")
        
        # If plan needs approval
        if status['state'] == 'WAITING_APPROVAL':
            print("\n📋 Plan is ready for approval!")
            print("   Run: await worker_manager.approve_worker_plan(session_id)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    await shutdown_server()

asyncio.run(test_with_real_repo())
SCRIPT
```

### Option 2: Test with Claude Desktop

1. **Add to Claude Desktop config** (Mac):
   ```bash
   # Edit: ~/Library/Application Support/Claude/claude_desktop_config.json
   {
     "mcpServers": {
       "jules-orchestrator": {
         "command": "jules-mcp",
         "cwd": "/workspace/cmhgo33qe028ytmimhtss1qm0/jules-mcp"
       }
     }
   }
   ```

2. **Restart Claude Desktop**

3. **Test MCP Tools** in Claude:
   ```
   Use the jules_create_worker tool to create a worker for:
   - Task: "Add unit tests for the authentication module"
   - Source: sources/github/myorg/myrepo
   - Title: "Add Auth Tests"
   - Branch: main
   ```

4. **Monitor with Resources**:
   ```
   Read the workers://all resource to see all active workers
   ```

5. **Check worker status**:
   ```
   Read worker://{session_id}/status to see detailed status
   ```

6. **Approve plans when ready**:
   ```
   Use jules_approve_plan with the session_id
   ```

## Example Complete Workflow

```python
# 1. Create multiple workers
worker1 = jules_create_worker(
    task_description="Refactor authentication to use JWT",
    source="sources/github/myorg/backend",
    title="Auth Refactor"
)

worker2 = jules_create_worker(
    task_description="Update frontend to use new auth endpoints",
    source="sources/github/myorg/frontend",
    title="Frontend Auth Update"
)

# 2. Monitor all workers
Read resource: workers://all

# 3. When a worker reaches WAITING_APPROVAL state
Read resource: worker://{session_id}/activities  # Review the plan

# 4. Approve the plan
jules_approve_plan(session_id="{session_id}")

# 5. Monitor progress
jules_get_activities(session_id="{session_id}", limit=5)

# 6. Send guidance if needed
jules_send_message(
    session_id="{session_id}",
    message="Please add comprehensive error handling"
)
```

## Common Issues

### Issue: "Requested entity was not found" (404)
**Cause**: Source path doesn't exist or Jules app not installed
**Solution**: 
- Verify Jules GitHub app is installed on the repository
- Check source format: `sources/github/{owner}/{repo}`
- Owner and repo names must match exactly (case-sensitive)

### Issue: "Unauthorized" (401)
**Cause**: Invalid or expired API key
**Solution**:
- Get a new API key from https://jules.google.com/settings#api
- Update `.env` file with new key
- Restart the server

### Issue: Workers stuck in PLANNING
**Cause**: Jules is still analyzing the repository or generating a plan
**Solution**:
- Wait 30-60 seconds for plan generation
- Check activities for progress updates
- If stuck for >5 minutes, check Jules web UI for errors

### Issue: No activities showing up
**Cause**: Polling hasn't run yet or session just created
**Solution**:
- Wait 5-10 seconds for first poll cycle
- Check server logs for polling errors
- Verify session was created successfully

## Debugging

### Enable verbose logging
Edit `src/jules_mcp/server.py`:
```python
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO to DEBUG
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)
```

### Check logs
When running as MCP server, logs go to stderr:
- Claude Desktop logs: `~/Library/Logs/Claude/mcp*.log` (Mac)
- Check for polling activity, API errors, and state changes

### Test API directly
```python
from jules_mcp import JulesAPIClient
import asyncio

client = JulesAPIClient(api_key="...", base_url="...", api_version="...")
response = await client.create_session(...)
print(response)
```

## Success Indicators

✅ Server starts without errors
✅ Background polling loop is running (check logs)
✅ Workers created successfully with session IDs
✅ State transitions: PLANNING → WAITING_APPROVAL → EXECUTING → COMPLETED
✅ Activities populated and updating every 5 seconds
✅ Plans can be approved and workers continue execution

## Next Steps

Once everything is working:
1. Orchestrate multiple workers for complex tasks
2. Use the `delegate_task` prompt for guidance
3. Monitor workers in real-time with resources
4. Approve plans and provide guidance as needed
5. Let Jules instances work in parallel on different parts of your codebase!

Happy orchestrating! 🎉
