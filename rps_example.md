
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
