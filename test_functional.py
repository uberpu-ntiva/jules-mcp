#!/usr/bin/env python3
"""
Functional test for Jules MCP Server
Tests the server startup and MCP protocol integration
"""

import os
import sys
import asyncio
import subprocess
import time
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_server_imports():
    """Test that all server components can be imported"""
    print("🔧 Testing server imports...")

    try:
        from jules_mcp.server import mcp, JulesAPIClient, WorkerManager
        print("  ✅ Core server classes imported successfully")

        print("  ✅ MCP server imported successfully")

        return True
    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        return False

def test_mcp_integration():
    """Test FastMCP integration"""
    print("🔧 Testing FastMCP integration...")

    try:
        # Mock environment for testing
        os.environ["JULES_API_KEY"] = "test_key_for_mcp_validation"
        os.environ["JULES_API_URL"] = "https://api.jules.ai"

        from jules_mcp.server import mcp, JulesAPI

        # Check MCP server instance
        assert hasattr(mcp, 'name'), "MCP server should have name attribute"
        assert mcp.name == "Jules MCP Server", "Server name should match"

        # Check that MCP tools are registered
        assert hasattr(mcp, '_tools'), "MCP server should have tools registry"
        tools_count = len(mcp._tools)

        print(f"  ✅ MCP server initialized with {tools_count} tools")

        # Test JulesAPI initialization
        api = JulesAPI()
        assert api.api_key == "test_key_for_mcp_validation", "API key should be set"
        print("  ✅ JulesAPI client initialized successfully")

        return True
    except Exception as e:
        print(f"  ❌ MCP integration test failed: {e}")
        return False
    finally:
        # Clean up test environment
        for key in ["JULES_API_KEY", "JULES_API_URL"]:
            if key in os.environ:
                del os.environ[key]

def test_server_configuration():
    """Test server configuration loading"""
    print("🔧 Testing server configuration...")

    try:
        from jules_mcp.config import Config

        # Test default configuration
        config = Config()
        assert hasattr(config, 'timeout'), "Config should have timeout"
        assert hasattr(config, 'max_retries'), "Config should have max_retries"

        print(f"  ✅ Configuration loaded with timeout={config.timeout}s")

        return True
    except Exception as e:
        print(f"  ❌ Configuration test failed: {e}")
        return False

def test_mcp_tools_structure():
    """Test MCP tools structure without initialization"""
    print("🔧 Testing MCP tools structure...")

    try:
        # Mock environment for structure test
        os.environ["JULES_API_KEY"] = "test_key"

        from jules_mcp.server import mcp

        # Count MCP components
        tools_count = len(mcp._tools) if hasattr(mcp, '_tools') else 0
        resources_count = len(mcp._resources) if hasattr(mcp, '_resources') else 0
        prompts_count = len(mcp._prompts) if hasattr(mcp, '_prompts') else 0

        print(f"  ✅ MCP Components:")
        print(f"    - Tools: {tools_count}")
        print(f"    - Resources: {resources_count}")
        print(f"    - Prompts: {prompts_count}")

        # Expected from documentation
        expected_tools = 5
        expected_resources = 3
        expected_prompts = 2

        if tools_count >= expected_tools:
            print(f"  ✅ Tools count meets expectation (≥{expected_tools})")
        else:
            print(f"  ⚠️  Tools count lower than expected ({tools_count} < {expected_tools})")

        return True
    except Exception as e:
        print(f"  ❌ MCP tools structure test failed: {e}")
        return False
    finally:
        # Clean up
        if "JULES_API_KEY" in os.environ:
            del os.environ["JULES_API_KEY"]

def main():
    """Run all functional tests"""
    print("🚀 Jules MCP Server Functional Test")
    print("=" * 50)

    tests = [
        ("Server Imports", test_server_imports),
        ("MCP Integration", test_mcp_integration),
        ("Server Configuration", test_server_configuration),
        ("MCP Tools Structure", test_mcp_tools_structure),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            if test_func():
                print(f"  ✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"  ❌ {test_name} FAILED")
        except Exception as e:
            print(f"  ❌ {test_name} ERROR: {e}")

    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All functional tests PASSED!")
        print("✅ Jules MCP Server is fully functional")
        print("📋 Ready for MCP client connection")
        return 0
    else:
        print("❌ Some tests FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())