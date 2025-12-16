#!/usr/bin/env python3
"""Diagnostic script for Fortinet FortiGate SSL inspection issues."""

import requests
import urllib3
from pathlib import Path
from dotenv import load_dotenv
import os

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

print("=" * 80)
print("FORTINET FORTIGATE SSL INSPECTION DIAGNOSTIC")
print("=" * 80)

jira_url = os.getenv("JIRA_URL")
jira_username = os.getenv("JIRA_USERNAME")
jira_api_token = os.getenv("JIRA_API_TOKEN")
jira_ssl_verify = os.getenv("JIRA_SSL_VERIFY", "true").lower() in ("true", "1", "yes")

print(f"\n[CONFIGURATION]")
print(f"  JIRA_URL: {jira_url}")
print(f"  JIRA_USERNAME: {jira_username}")
print(f"  JIRA_SSL_VERIFY: {jira_ssl_verify}")

if not jira_url or not jira_username or not jira_api_token:
    print("\n[ERROR] Missing required environment variables")
    exit(1)

# Test 1: HTTP request without SSL verification
print(f"\n[TEST 1] GET /rest/api/2/project - SSL_VERIFY=False")
try:
    response = requests.get(
        f"{jira_url}/rest/api/2/project",
        auth=(jira_username, jira_api_token),
        verify=False,
        timeout=10,
    )
    print(f"  Status Code: {response.status_code}")
    print(f"  Content-Type: {response.headers.get('Content-Type', 'N/A')}")
    print(f"  Content Length: {len(response.text)}")
    print(f"  First 200 chars: {response.text[:200]}")
    
    if response.status_code == 200 and "application/json" in response.headers.get("Content-Type", ""):
        print(f"  ✅ Got JSON response (likely successful)")
    elif response.status_code in (301, 302, 303, 307, 308):
        print(f"  ⚠️  Got redirect to: {response.headers.get('Location', 'N/A')}")
    elif "fgtauth" in response.text.lower() or "fortigate" in response.text.lower():
        print(f"  ❌ Got Fortinet FortiGate auth portal (SSL inspection active)")
    elif "<html" in response.text.lower():
        print(f"  ❌ Got HTML response (not JSON API response)")
    else:
        print(f"  ⚠️  Unexpected response")
        
except Exception as e:
    print(f"  ❌ Error: {e}")

# Test 2: HTTP request with SSL verification
print(f"\n[TEST 2] GET /rest/api/2/project - SSL_VERIFY=True")
try:
    response = requests.get(
        f"{jira_url}/rest/api/2/project",
        auth=(jira_username, jira_api_token),
        verify=True,
        timeout=10,
    )
    print(f"  Status Code: {response.status_code}")
    print(f"  Content-Type: {response.headers.get('Content-Type', 'N/A')}")
    print(f"  ✅ SSL verification passed")
    
except requests.exceptions.SSLError as e:
    print(f"  ❌ SSL Error: {str(e)[:200]}")
    if "certificate verify failed" in str(e).lower():
        print(f"     This indicates a self-signed or intercepted certificate")
    if "wrong version number" in str(e).lower():
        print(f"     This might indicate a proxy/firewall intercepting HTTPS")
        
except Exception as e:
    print(f"  ❌ Error: {e}")

# Test 3: Check certificate
print(f"\n[TEST 3] Certificate Information")
try:
    import ssl
    import socket
    
    # Extract host from URL
    from urllib.parse import urlparse
    parsed = urlparse(jira_url)
    host = parsed.netloc.split(":")[0]
    port = 443
    
    print(f"  Host: {host}")
    print(f"  Port: {port}")
    
    context = ssl.create_default_context()
    try:
        with socket.create_connection((host, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                print(f"  Subject: {dict(x[0] for x in cert['subject'])}")
                print(f"  Issuer: {dict(x[0] for x in cert['issuer'])}")
                print(f"  ✅ Certificate verified")
    except ssl.SSLError as e:
        print(f"  ❌ SSL Error: {e}")
        
except Exception as e:
    print(f"  ⚠️  Could not check certificate: {e}")

# Test 4: Solutions
print(f"\n[SOLUTIONS]")
print(f"""
If you're getting Fortinet FortiGate authentication portal (fgtauth) responses:

1. **Disable SSL Verification (Quick Fix - Not Recommended for Production)**
   - Set JIRA_SSL_VERIFY=false in .env
   - This bypasses SSL certificate validation

2. **Install Fortinet CA Certificate (Recommended)**
   - Export the Fortinet FortiGate's CA certificate
   - Add it to your system's trusted certificates or Python's certifi
   - Set JIRA_CERT=/path/to/fortinet-ca.pem in .env
   
3. **Bypass Fortinet for Jira (Network Configuration)**
   - Configure Fortinet to allow direct access to Jira on port 443
   - Add Jira to SSL inspection exclusion list
   - Contact your network/security team

4. **Use HTTP Proxy (If Available)**
   - Configure a proxy that doesn't inspect HTTPS
   - Set HTTP_PROXY/HTTPS_PROXY environment variables

5. **Use Internal Network Path**
   - If available, use an internal IP that bypasses Fortinet
   - Example: https://jira-internal.local instead of https://192.168.11.118
""")

print("=" * 80)
