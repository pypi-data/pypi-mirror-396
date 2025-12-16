#!/usr/bin/env python3
"""Test FortiGate detection and response handling."""

import json
from mcp_atlassian.utils.fortinet import (
    is_fortinet_response,
    extract_fgtauth_url,
)
from mcp_atlassian.exceptions import FortiGateAuthenticationRequiredError

# Simulate FortiGate HTML response
fortinet_html = '''<html>
<body>
<script>
window.location="https://192.168.11.118/fgtauth?010e0781ab0bcd68"
</script>
</body>
</html>'''

print("=" * 60)
print("Testing FortiGate Detection")
print("=" * 60)

# Test 1: Detection
print("\n1. Testing FortiGate detection:")
is_fortinet = is_fortinet_response(fortinet_html)
print(f"   is_fortinet_response(): {is_fortinet}")
assert is_fortinet, "Should detect FortiGate response"
print("   ✅ FortiGate response detected correctly")

# Test 2: URL extraction
print("\n2. Testing URL extraction:")
auth_url = extract_fgtauth_url(fortinet_html)
print(f"   Extracted URL: {auth_url}")
assert auth_url == "https://192.168.11.118/fgtauth?010e0781ab0bcd68"
print("   ✅ URL extracted correctly")

# Test 3: Exception creation and serialization
print("\n3. Testing exception and JSON response:")
exc = FortiGateAuthenticationRequiredError(
    auth_url=auth_url,
    message="FortiGate SSL inspection detected"
)
exc_dict = exc.to_dict()
exc_json = json.dumps(exc_dict, indent=2)
print("   Exception JSON response:")
print(f"   {exc_json}")
assert exc_dict["error"] == "fortinet_auth_required"
assert exc_dict["auth_url"] == auth_url
print("   ✅ Exception serializes to JSON correctly")

# Test 4: Simulating projects.py detection
print("\n4. Testing projects.py error detection:")
response = exc_dict  # Simulate what jira.projects() would return
if isinstance(response, dict) and response.get("error") == "fortinet_auth_required":
    print("   ✅ Error detected in response")
    print(f"   Would raise FortiGateAuthenticationRequiredError")
else:
    print("   ❌ Error NOT detected")
    raise AssertionError("Response error detection failed")

print("\n" + "=" * 60)
print("All tests passed! ✅")
print("=" * 60)
