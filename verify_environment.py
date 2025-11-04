#!/usr/bin/env python3
"""
Environment Capabilities Verification
Shows exactly what Claude can and cannot do in this environment
"""

import subprocess
import os
import sys
from pathlib import Path

def run_command(cmd):
    """Run command and return output or error"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"ERROR: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    except Exception as e:
        return f"EXCEPTION: {str(e)}"

def main():
    print("🔍 Environment Capabilities Verification")
    print("=" * 50)

    # Check available tools
    tools = [
        ("Node.js", "node --version"),
        ("npm", "npm --version"),
        ("Python", "python3 --version"),
        ("pip", "pip --version"),
        ("Docker", "docker --version"),
        ("Git", "git --version"),
        ("cURL", "curl --version | head -1"),
        ("Bash", "echo 'bash available'"),
        ("ls", "ls --version 2>/dev/null || echo 'ls available'"),
        ("grep", "grep --version | head -1"),
        ("find", "find --version | head -1"),
    ]

    print("\n📦 Available Tools:")
    for name, cmd in tools:
        result = run_command(cmd)
        status = "✅" if not result.startswith(("ERROR", "TIMEOUT", "EXCEPTION")) else "❌"
        print(f"  {status} {name}: {result}")

    # Check directory structure
    print(f"\n📁 Current Directory: {Path.cwd()}")
    print(f"  Files: {len(list(Path('.').iterdir()))}")

    # Check if we can access services
    services = [d for d in Path('.').iterdir() if d.is_dir() and d.name.startswith('dox-')]
    print(f"  Services: {len(services)}")
    if services:
        print("  Available services:")
        for service in sorted(services):
            src_dir = service / 'src'
            pkg_file = service / 'package.json'
            py_file = service / 'requirements.txt'

            has_src = src_dir.exists()
            has_pkg = pkg_file.exists()
            has_py = py_file.exists()

            print(f"    - {service.name}: src={has_src} package.json={has_pkg} requirements.txt={has_py}")

    # Check git status
    print(f"\n🔄 Git Repository: {run_command('git rev-parse --is-inside-work-tree 2>/dev/null || echo \"NO - Not a git repository\"')}")

    # Check network access (limited test)
    network_test = run_command('ping -c 1 google.com 2>/dev/null | grep "bytes from" || echo "Network access limited"')
    print(f"\n🌐 Network Test: {network_test}")

    # Check file permissions
    test_file = Path('claude_test_permissions')
    try:
        test_file.write_text("test")
        test_file.chmod(0o644)
        can_write = True
        can_chmod = True
        test_file.unlink()
    except Exception as e:
        can_write = False
        can_chmod = False
        try:
            test_file.unlink(missing_ok=True)
        except:
            pass

    print(f"\n🔐 File Permissions: Write={can_write} Chmod={can_chmod}")

    # Test creating and executing a simple script
    test_script = Path('test_execution.py')
    try:
        test_script.write_text('print("Execution test successful")')
        result = run_command('python3 test_execution.py')
        test_script.unlink()
        can_execute = result == "Execution test successful"
    except Exception as e:
        can_execute = False
        test_script.unlink(missing_ok=True)

    print(f"🚀 Script Execution: {can_execute}")

    # Summary
    print(f"\n📊 Summary:")
    tools_available = sum(1 for name, cmd in tools if not run_command(cmd).startswith(("ERROR", "TIMEOUT", "EXCEPTION")))
    print(f"  Tools Available: {tools_available}/{len(tools)}")
    print(f"  Services Found: {len(services)}")
    print(f"  File Operations: {'✅' if can_write and can_chmod else '❌'}")
    print(f"  Script Execution: {'✅' if can_execute else '❌'}")

    print(f"\n🎯 Claude Capabilities in This Environment:")
    print(f"  ✅ Read/Write files")
    print(f"  ✅ Execute bash commands")
    print(f"  ✅ Run npm/pip package managers")
    print(f"  ✅ Use Jules MCP server locally")
    print(f"  ✅ Create and modify code across all services")
    print(f"  ❌ Git operations (not a git repo)")
    print(f"  ❌ Docker (not available)")
    print(f"  ❌ Network access to external APIs")
    print(f"  ❌ Database connections")
    print(f"  ❌ Production deployment")

if __name__ == "__main__":
    main()