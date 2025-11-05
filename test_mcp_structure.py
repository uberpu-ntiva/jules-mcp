#!/usr/bin/env python3
"""
Test MCP server structure and tools registration
"""

import os
import sys
import inspect
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_mcp_detailed_structure():
    """Test detailed MCP server structure"""
    print("🔧 Analyzing MCP server structure...")

    # Set minimal environment
    os.environ["JULES_API_KEY"] = "test_key"

    try:
        from jules_mcp.server import mcp

        print(f"  ✅ MCP server type: {type(mcp)}")
        print(f"  ✅ MCP server name: {getattr(mcp, 'name', 'N/A')}")

        # Analyze MCP server attributes
        attributes = dir(mcp)
        tool_related = [attr for attr in attributes if 'tool' in attr.lower()]
        resource_related = [attr for attr in attributes if 'resource' in attr.lower()]
        prompt_related = [attr for attr in attributes if 'prompt' in attr.lower()]

        print(f"  🔍 Tool-related attributes: {tool_related}")
        print(f"  🔍 Resource-related attributes: {resource_related}")
        print(f"  🔍 Prompt-related attributes: {prompt_related}")

        # Check for common FastMCP attributes
        fastmcp_attrs = ['_tools', '_resources', '_prompts', 'tools', 'resources', 'prompts']
        for attr in fastmcp_attrs:
            if hasattr(mcp, attr):
                value = getattr(mcp, attr)
                print(f"  ✅ Found attribute '{attr}': {type(value)} - {len(value) if hasattr(value, '__len__') else 'N/A'}")

        # Check all attributes for completeness
        all_attrs = sorted([attr for attr in attributes if not attr.startswith('_')])
        print(f"  📋 Public attributes: {all_attrs}")

        return True
    except Exception as e:
        print(f"  ❌ MCP structure analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up
        if "JULES_API_KEY" in os.environ:
            del os.environ["JULES_API_KEY"]

def test_decorator_registration():
    """Test if decorators are registering correctly"""
    print("🔧 Testing decorator registration...")

    try:
        # Import the module and check decorated functions
        from jules_mcp import server

        # Get all functions in the server module
        functions = inspect.getmembers(server, inspect.isfunction)
        tool_functions = [name for name, func in functions if hasattr(func, '__mcp_tool__')]
        resource_functions = [name for name, func in functions if hasattr(func, '__mcp_resource__')]
        prompt_functions = [name for name, func in functions if hasattr(func, '__mcp_prompt__')]

        print(f"  🔍 Total functions found: {len(functions)}")
        print(f"  ✅ Tool functions found: {tool_functions}")
        print(f"  ✅ Resource functions found: {resource_functions}")
        print(f"  ✅ Prompt functions found: {prompt_functions}")

        # Check function names that should be decorated
        expected_tools = [
            'jules_create_worker',
            'jules_send_message',
            'jules_approve_plan',
            'jules_cancel_session',
            'jules_get_activities'
        ]

        expected_resources = [
            'get_worker_status',
            'get_all_workers',
            'get_worker_activities_resource'
        ]

        expected_prompts = [
            'delegate_task',
            'review_plan'
        ]

        print(f"\n📋 Expected tools:")
        for tool in expected_tools:
            found = tool in [name for name, _ in functions]
            print(f"  {'✅' if found else '❌'} {tool}")

        print(f"\n📋 Expected resources:")
        for resource in expected_resources:
            found = resource in [name for name, _ in functions]
            print(f"  {'✅' if found else '❌'} {resource}")

        print(f"\n📋 Expected prompts:")
        for prompt in expected_prompts:
            found = prompt in [name for name, _ in functions]
            print(f"  {'✅' if found else '❌'} {prompt}")

        return True
    except Exception as e:
        print(f"  ❌ Decorator registration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run detailed structure analysis"""
    print("🔬 Jules MCP Server Detailed Structure Analysis")
    print("=" * 60)

    tests = [
        ("MCP Server Structure", test_mcp_detailed_structure),
        ("Decorator Registration", test_decorator_registration),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            if test_func():
                print(f"  ✅ {test_name} COMPLETED")
                passed += 1
            else:
                print(f"  ❌ {test_name} FAILED")
        except Exception as e:
            print(f"  ❌ {test_name} ERROR: {e}")

    print("\n" + "=" * 60)
    print(f"Analysis Results: {passed}/{total} tests completed")

    return passed == total

if __name__ == "__main__":
    main()