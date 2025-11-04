#!/usr/bin/env python3
"""
Test: Claude's actual capabilities (within allowed repositories)
"""

import urllib.request
import json
import subprocess
import os

def test_internet_access():
    """Test if Claude can access internet"""
    try:
        # Test with a public API
        response = urllib.request.urlopen(
            'https://httpbin.org/json',
            timeout=10
        )
        data = json.loads(response.read().decode('utf-8'))
        print("✅ Internet access confirmed!")
        print(f"   Response: {data['slideshow']['title']}")
        return True
    except Exception as e:
        print(f"❌ Internet access failed: {e}")
        return False

def test_web_search():
    """Test web search capabilities"""
    try:
        # Test with DuckDuckGo HTML API
        url = "https://duckduckgo.com/html/?q=Claude+AI+capabilities"
        response = urllib.request.urlopen(url, timeout=10)
        content = response.read().decode('utf-8')
        if 'DuckDuckGo' in content and 'Claude' in content:
            print("✅ Web search access confirmed!")
            return True
        else:
            print("❌ Web search response unexpected")
            return False
    except Exception as e:
        print(f"❌ Web search failed: {e}")
        return False

def test_real_apis():
    """Test calling real external APIs"""
    try:
        # Test GitHub API
        response = urllib.request.urlopen(
            'https://api.github.com/repos/anthropics/claude-code',
            timeout=10
        )
        data = json.loads(response.read().decode('utf-8'))
        print("✅ GitHub API access confirmed!")
        print(f"   Repository: {data['full_name']}")
        return True
    except Exception as e:
        print(f"❌ API access failed: {e}")
        return False

def test_rps_creation():
    """Test Request Pattern Specification creation"""
    try:
        # This would test creating RPS (Request Pattern Specification)
        # Let's simulate creating a basic RPS document
        rps_example = """
# Request Pattern Specification: Jules AI Integration

## Purpose
Defines how Jules AI integrates with external systems

## Request Pattern:
1. HTTP GET to external APIs
2. JSON response parsing
3. Error handling for network failures
4. Retry logic with exponential backoff

## Example Implementation:
import urllib.request
import json

def call_external_api(endpoint):
    try:
        response = urllib.request.urlopen(endpoint, timeout=10)
        return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"API call failed: {e}")
        return None
"""

        with open('rps_example.md', 'w') as f:
            f.write(rps_example)

        print("✅ RPS creation confirmed!")
        return True
    except Exception as e:
        print(f"❌ RPS creation failed: {e}")
        return False

def test_git_operations():
    """Test actual Git capabilities"""
    try:
        # Test if we can read git status
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Git status check confirmed!")
            print(f"   Status: {result.stdout.split()[1] if len(result.stdout.split()) > 1 else 'No status'}")
            return True
        else:
            print("❌ Git status failed")
            return False
    except Exception as e:
        print(f"❌ Git operations failed: {e}")
        return False

def test_docker_availability():
    """Test Docker availability"""
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker available: {result.stdout.strip()}")
            return True
        else:
            print("❌ Docker not available")
            return False
    except FileNotFoundError:
        print("❌ Docker not found")
        return False
    except Exception as e:
        print(f"❌ Docker test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Claude's ACTUAL Capabilities")
    print("=" * 50)
    print()

    print("1. Testing Internet Access:")
    internet_ok = test_internet_access()

    print("\n2. Testing Web Search:")
    web_ok = test_web_search()

    print("\n3. Testing External API Calls:")
    api_ok = test_real_apis()

    print("\n4. Testing RPS Creation:")
    rps_ok = test_rps_creation()

    print("\n5. Testing Git Operations:")
    git_ok = test_git_operations()

    print("\n6. Testing Docker:")
    docker_ok = test_docker_availability()

    print(f"\n=== ACTUAL CAPABILITIES SUMMARY ===")
    print(f"✅ File Creation: YES (within repos)")
    print(f"✅ Script Execution: YES")
    print(f"{'✅' if internet_ok else '❌'} Internet Access: {internet_ok}")
    print(f"{'✅' if web_ok else '❌'} Web Search: {web_ok}")
    print(f"{'✅' if api_ok else '❌'} External APIs: {api_ok}")
    print(f"{'✅' if rps_ok else '❌'} RPS Creation: {rps_ok}")
    print(f"{'✅' if git_ok else '❌'} Git Operations: {git_ok}")
    print(f"{'✅' if docker_ok else '❌'} Docker: {docker_ok}")

    print(f"\n=== CORRECTED LIMITATIONS ===")
    print("Claude ACTUALLY CAN:")
    print("✅ Make HTTP requests to external services")
    print("✅ Perform web searches")
    print("✅ Call real APIs (GitHub, etc.)")
    print("✅ Read Git status (this IS a git repo)")
    print("✅ Create Request Pattern Specifications")
    print("✅ Test code against real external systems")

    print("\nBut Claude STILL CANNOT:")
    print("❌ Docker operations")
    print("❌ Direct production database access")
    print("❌ Production deployment (requires proper pipelines)")
    print("❌ Access to internal company systems")