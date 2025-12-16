class MCPAtlassianAuthenticationError(Exception):
    """Raised when Atlassian API authentication fails (401/403)."""

    pass


class FortiGateAuthenticationRequiredError(Exception):
    """Raised when FortiGate SSL inspection requires authentication.

    This exception is raised when the MCP receives an HTML response from
    FortiGate instead of JSON from the Jira API. This indicates that a
    Fortinet FortiGate SSL inspection appliance is intercepting HTTPS
    connections and redirecting to an authentication portal.

    Attributes:
        auth_url: The FortiGate authentication URL to open in a browser
        message: Human-readable error message with instructions
    """

    def __init__(self, auth_url: str | None = None, message: str | None = None) -> None:
        self.auth_url = auth_url
        if message:
            self.message = message
        elif auth_url:
            self.message = (
                "Fortinet FortiGate SSL inspection is blocking access to Jira. "
                "This is a network-level security appliance intercepting HTTPS connections. "
                "Please contact your network administrator to allow MCP server access. "
                "Authentication in your browser alone will NOT resolve this issue for the server."
            )
        else:
            self.message = (
                "FortiGate SSL inspection detected. "
                "Please contact your network administrator to configure access for the MCP server."
            )
        super().__init__(self.message)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "error": "fortinet_auth_required",
            "auth_required": True,
            "auth_url": self.auth_url,
            "message": self.message,
            "details": (
                "Fortinet FortiGate is performing Deep Packet Inspection (DPI) on HTTPS traffic. "
                "You need to authenticate to proceed."
            ),
            "quick_fix": (
                "TRY AUTOMATIC AUTHENTICATION FIRST:\n"
                "1. Call: auto_authenticate_fortigate(auth_url='<url>', username='<user>', password='<pass>')\n"
                "2. Or set env vars: FORTIGATE_USERNAME, FORTIGATE_PASSWORD\n"
                "3. Then retry your original operation\n\n"
                "IF THAT FAILS, use manual extraction (see recommended_actions)"
                if self.auth_url
                else "Please contact your network administrator"
            ),
            "recommended_actions": [
                "OPTION 1 - AUTOMATIC AUTHENTICATION (RECOMMENDED, No 2FA):",
                "  Step 1: Set environment variables (or provide as parameters):",
                "    export FORTIGATE_USERNAME='your_username'",
                "    export FORTIGATE_PASSWORD='your_password'",
                "",
                "  Step 2: Call the auto-authentication tool:",
                f"    auto_authenticate_fortigate(auth_url='{self.auth_url}')"
                if self.auth_url
                else "    auto_authenticate_fortigate(auth_url='<your_auth_url>')",
                "",
                "  Step 3: If successful, retry your original Jira operation",
                "    The cookie will be automatically injected in all requests",
                "",
                "",
                "OPTION 2 - MANUAL COOKIE EXTRACTION (if OPTION 1 fails or you have 2FA):",
                "  Step 1 - Open Authentication Portal:",
                f"    Visit this URL in your browser: {self.auth_url}"
                if self.auth_url
                else "    Visit the auth URL in your browser",
                "",
                "  Step 2 - Extract the Cookie:",
                "    a) After visiting the URL, open DevTools (F12)",
                "    b) Go to Application tab → Cookies",
                "    c) Look for 'FGTAUTH' cookie on the domain",
                "    d) Copy the cookie value (long hex string)",
                "",
                "  Step 3 - Set the Cookie in MCP:",
                "    Call: set_fortinet_cookie(cookie_value='<paste_cookie_here>')",
                "",
                "  Step 4 - Retry Your Operation:",
                "    Call your original Jira operation again",
                "",
                "",
                "OPTION 3 - PERMANENT SOLUTION (recommended for DevOps/CI):",
                "  Contact your network administrator with these requests:",
                "  * Whitelist the MCP server IP for direct Jira access (bypass FortiGate DPI)",
                "  * OR configure a client certificate for the server",
                "  * OR set up a proxy server with FortiGate credentials",
            ],
            "user_action": (
                f"# Try automatic authentication first:\n"
                f"auto_authenticate_fortigate(auth_url='{self.auth_url}')\n\n"
                f"# If that fails, manually extract cookie:\n"
                f"1. Visit: {self.auth_url}\n"
                f"2. Extract FGTAUTH cookie from DevTools (Application → Cookies)\n"
                f"3. Call: set_fortinet_cookie(cookie_value='<extracted_value>')\n"
                f"4. Retry your original Jira operation"
                if self.auth_url
                else "Contact your network administrator"
            ),
        }
