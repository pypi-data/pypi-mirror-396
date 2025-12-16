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
                "You need to authenticate your browser and extract the authentication cookie."
            ),
            "quick_fix": (
                "1. Visit the auth_url in your browser\n"
                "2. Extract FGTAUTH cookie from DevTools\n"
                "3. Call: set_fortinet_cookie(cookie_value='<value>')"
                if self.auth_url
                else "Please contact your network administrator"
            ),
            "recommended_actions": [
                "STEP 1 - Open Authentication Portal:",
                f"  Visit this URL in your browser: {self.auth_url}"
                if self.auth_url
                else "  Get the auth URL from the error",
                "",
                "STEP 2 - Extract the Cookie:",
                "  a) After visiting the URL, open DevTools (F12)",
                "  b) Go to Application tab → Cookies",
                "  c) Look for 'FGTAUTH' cookie on the domain",
                "  d) Copy the cookie value (long hex string)",
                "",
                "STEP 3 - Set the Cookie in MCP:",
                "  Call this tool with the cookie value:",
                "  set_fortinet_cookie(cookie_value='<paste_cookie_here>')",
                "",
                "STEP 4 - Retry Your Operation:",
                "  Call your original Jira operation again",
                "  The cookie will now be automatically injected in all requests",
                "",
                "For PERMANENT access (recommended):",
                "- Contact your network administrator with these requests:",
                "  * Whitelist the MCP server IP for direct Jira access (bypass FortiGate DPI)",
                "  * OR configure a client certificate for the server",
                "  * OR set up a proxy server with FortiGate credentials",
            ],
            "user_action": (
                f"1. Visit: {self.auth_url}\n"
                f"2. Extract FGTAUTH cookie from DevTools (Application → Cookies)\n"
                f"3. Call: set_fortinet_cookie(cookie_value='<extracted_value>')\n"
                f"4. Retry your original Jira operation"
                if self.auth_url
                else "Contact your network administrator"
            ),
        }
