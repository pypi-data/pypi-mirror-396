#!/usr/bin/env python3
"""Integration test for FortiGate handling in get_all_projects tool."""

import asyncio
import json
from unittest.mock import MagicMock, patch, AsyncMock
from mcp_atlassian.servers.jira import get_all_projects
from mcp_atlassian.jira.config import JiraConfig
from fastmcp import Context

# Simulate FortiGate HTML response
fortinet_html = '''<html>
<body>
<script>
window.location="https://192.168.11.118/fgtauth?010e0781ab0bcd68"
</script>
</body>
</html>'''

async def test_fortinet_response_in_tool():
    """Test that get_all_projects returns FortiGate JSON when intercepted."""
    print("\n" + "=" * 70)
    print("Testing FortiGate Response in get_all_projects Tool")
    print("=" * 70)

    # Create mock jira fetcher that returns FortiGate error
    mock_jira = MagicMock()
    mock_jira.config = MagicMock(projects_filter=None)
    
    # Simulate what happens when wrapper replaces HTML with JSON
    fortinet_error_dict = {
        "error": "fortinet_auth_required",
        "auth_required": True,
        "auth_url": "https://192.168.11.118/fgtauth?010e0781ab0bcd68",
        "message": "FortiGate authentication required"
    }
    
    # This is what jira.projects() returns when wrapper modifies response
    mock_jira.get_all_projects.return_value = fortinet_error_dict
    
    # Mock the fetcher
    with patch("mcp_atlassian.servers.jira.get_jira_fetcher") as mock_fetcher:
        mock_fetcher.return_value = AsyncMock(return_value=mock_jira)
        
        # Mock get_context
        with patch("mcp_atlassian.servers.jira.get_context") as mock_ctx:
            mock_ctx.return_value = MagicMock()
            
            print("\n1. Calling get_all_projects with FortiGate error response...")
            result = await get_all_projects(include_archived=False)
            
            print(f"\n2. Result type: {type(result)}")
            print(f"   Result length: {len(result)} characters")
            
            # Parse the JSON response
            try:
                response_json = json.loads(result)
                print(f"\n3. Parsed JSON response:")
                print(f"   {json.dumps(response_json, indent=2)}")
                
                # Verify the response contains FortiGate info
                assert response_json["error"] == "fortinet_auth_required"
                assert response_json["auth_required"] == True
                assert "auth_url" in response_json
                assert "fgtauth" in response_json["auth_url"]
                
                print(f"\n✅ Tool correctly returns FortiGate error JSON!")
                print(f"   Auth URL: {response_json['auth_url']}")
                print(f"   User Action: {response_json.get('user_action', 'N/A')}")
                
                return True
            except json.JSONDecodeError as e:
                print(f"\n❌ Failed to parse response as JSON: {e}")
                print(f"   Response: {result[:200]}")
                return False

# Run the test
if __name__ == "__main__":
    result = asyncio.run(test_fortinet_response_in_tool())
    print("\n" + "=" * 70)
    if result:
        print("Integration test PASSED ✅")
    else:
        print("Integration test FAILED ❌")
    print("=" * 70)
