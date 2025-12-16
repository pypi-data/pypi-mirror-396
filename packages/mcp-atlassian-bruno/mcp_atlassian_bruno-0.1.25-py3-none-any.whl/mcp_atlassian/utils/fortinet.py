"""Utility to detect and handle Fortinet FortiGate SSL inspection issues."""

import logging
import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from requests import Session

logger = logging.getLogger("mcp-jira.fortinet")

# Global storage for FortiGate authentication cookie
_fortinet_cookie: dict[str, str] = {}


def set_fortinet_cookie(cookie_value: str) -> None:
    """
    Store a FortiGate authentication cookie for automatic injection.

    This cookie will be automatically added to all Jira API requests
    to bypass FortiGate SSL inspection without manual re-authentication.

    Args:
        cookie_value: The FortiGate cookie value (e.g., from browser DevTools)
    """
    _fortinet_cookie["value"] = cookie_value
    logger.info("FortiGate authentication cookie set. Will be injected in requests.")


def get_fortinet_cookie() -> str | None:
    """
    Retrieve the stored FortiGate authentication cookie.

    Returns:
        The cookie value if set, None otherwise
    """
    return _fortinet_cookie.get("value")


def clear_fortinet_cookie() -> None:
    """Clear the stored FortiGate authentication cookie."""
    _fortinet_cookie.clear()
    logger.info("FortiGate authentication cookie cleared.")



def extract_fgtauth_url(response_text: str) -> str | None:
    """
    Extract the FortiGate authentication URL from HTML response.

    Looks for patterns like:
    - window.location="https://192.168.11.118/fgtauth?070e0b8d9bf6c39d"
    - <meta http-equiv="refresh" content="0;url=https://...">

    Args:
        response_text: The HTML response body

    Returns:
        The authentication URL if found, None otherwise
    """
    # Pattern 1: window.location="URL"
    match = re.search(
        r'window\.location\s*=\s*["\']([^"\']*fgtauth[^"\']*)["\']',
        response_text,
        re.IGNORECASE,
    )
    if match:
        return match.group(1)

    # Pattern 2: meta refresh redirect
    match = re.search(
        r'<meta[^>]*url=([^"\'>\s]*fgtauth[^"\'>\s]*)',
        response_text,
        re.IGNORECASE,
    )
    if match:
        return match.group(1)

    # Pattern 3: href with fgtauth
    match = re.search(
        r'href\s*=\s*["\']([^"\']*fgtauth[^"\']*)["\']',
        response_text,
        re.IGNORECASE,
    )
    if match:
        return match.group(1)

    return None


def extract_cookie_from_fgtauth_url(fgtauth_url: str) -> str | None:
    """
    Extract the authentication token/cookie from FortiGate URL.

    FortiGate URLs typically look like:
    - https://192.168.11.118/fgtauth?070e0b8d9bf6c39d
    - https://fortigate.domain.com/fgtauth?token=abc123

    Args:
        fgtauth_url: The FortiGate authentication URL

    Returns:
        The authentication token if found, None otherwise
    """
    if not fgtauth_url:
        return None

    # Extract token from query string parameter
    # Pattern 1: /fgtauth?<token> (direct token as query param)
    match = re.search(r'fgtauth\?([a-f0-9]+)', fgtauth_url, re.IGNORECASE)
    if match:
        return match.group(1)

    # Pattern 2: fgtauth?token=<value>
    match = re.search(r'fgtauth\?token=([^&\s"]+)', fgtauth_url, re.IGNORECASE)
    if match:
        return match.group(1)

    # Pattern 3: fgtauth?... with other params, extract token param
    match = re.search(r'[?&]token=([^&\s"]+)', fgtauth_url, re.IGNORECASE)
    if match:
        return match.group(1)

    return None


def is_fortinet_response(response_text: str) -> bool:
    """
    Detect if response is from Fortinet FortiGate SSL inspection.

    Args:
        response_text: The response body text

    Returns:
        True if response appears to be from Fortinet FortiGate
    """
    fortinet_indicators = [
        "fgtauth",
        "fortigate",
        "fortinet",
        "forticlient",
        "login.cgi",
        "check_fgtauth",
        "window.location",  # Redirection script
    ]

    text_lower = response_text.lower()

    # Check for any fortinet indicator
    has_indicator = any(indicator in text_lower for indicator in fortinet_indicators)

    # Check for specific fgtauth redirect pattern
    has_fgtauth_redirect = "fgtauth?" in text_lower or "/fgtauth" in text_lower

    return has_indicator or has_fgtauth_redirect
def is_html_response(content_type: str | None, response_text: str | None) -> bool:
    """
    Detect if response is HTML (likely error/redirect).

    Args:
        content_type: Content-Type header value
        response_text: Response body text

    Returns:
        True if response appears to be HTML
    """
    if content_type and "text/html" in content_type.lower():
        return True

    if response_text and response_text.strip().startswith("<"):
        return True

    return False


def detect_and_report_fortinet_issue(
    response_text: str, content_type: str | None = None, url: str | None = None
) -> dict[str, Any] | None:
    """
    Detect Fortinet FortiGate SSL inspection issue and provide diagnostic info.

    Args:
        response_text: The response body text
        content_type: Content-Type header value
        url: The requested URL

    Returns:
        Dictionary with diagnostic information if issue detected, None otherwise
    """
    if is_fortinet_response(response_text):
        # Extract the authentication URL
        auth_url = extract_fgtauth_url(response_text)

        logger.error(
            "Fortinet FortiGate SSL Inspection detected! "
            "HTTPS requests are being intercepted and redirected to /fgtauth. "
            f"Authentication URL: {auth_url or 'Not found'}"
        )

        return {
            "issue": "fortinet_ssl_inspection",
            "auth_required": True,
            "auth_url": auth_url,
            "description": (
                "Fortinet FortiGate is intercepting HTTPS requests. "
                "Please authenticate first, then retry."
            ),
            "user_action": (
                f"Open this URL in your browser to authenticate: {auth_url}"
                if auth_url
                else "FortiGate authentication required. Contact admin."
            ),
            "indicators": {
                "is_fortinet": True,
                "is_html": is_html_response(content_type, response_text),
                "url": url,
                "content_type": content_type,
                "response_preview": response_text[:200],
            },
            "recommended_actions": [
                f"1. Authenticate: {auth_url}" if auth_url else "1. Authenticate",
                "2. After authentication, retry the operation",
                "3. If issue persists, request Jira SSL inspection exclusion",
                "4. Alternative: Install Fortinet CA certificate",
            ],
        }

    if is_html_response(content_type, response_text):
        logger.warning(
            f"Received HTML response from {url} instead of JSON. "
            "This might indicate a redirect or authentication issue."
        )

        return {
            "issue": "unexpected_html_response",
            "description": "Received HTML instead of JSON API response",
            "indicators": {
                "is_html": True,
                "is_fortinet": False,
                "url": url,
                "content_type": content_type,
                "response_preview": response_text[:200],
            },
            "recommended_actions": [
                "1. Verify Jira API URL is correct",
                "2. Check authentication credentials",
                "3. Verify SSL certificate (if using HTTPS)",
                "4. Check if Jira is behind a proxy/firewall",
                "5. Check for Fortinet FortiGate SSL inspection",
            ],
        }

    return None


def install_fortinet_hook(session: "Session") -> None:
    """
    Install the FortiGate detection hook on a requests Session.

    This works by wrapping session HTTP methods to:
    1. Inject stored FortiGate cookie if available
    2. Check responses for FortiGate HTML
    3. Replace HTML with JSON error before parsing occurs

    Args:
        session: A requests.Session instance
    """
    def create_wrapped_method(original_method):  # noqa: ANN001
        """Create a wrapper for a session method."""

        def wrapped_method(*args: object, **kwargs: object) -> "Any":  # noqa: ANN002
            """Wrapper that injects cookie and checks for FortiGate HTML."""
            # Step 1: Inject FortiGate cookie if available
            cookie = get_fortinet_cookie()
            if cookie:
                # Add cookie to headers if not already present
                if "headers" not in kwargs:
                    kwargs["headers"] = {}
                if not isinstance(kwargs["headers"], dict):
                    kwargs["headers"] = dict(kwargs["headers"])

                # Add the FortiGate authentication cookie
                # Cookie name is typically "FGTAUTH" but can vary
                existing_cookies = kwargs["headers"].get("Cookie", "")
                if "FGTAUTH" not in existing_cookies:
                    if existing_cookies:
                        kwargs["headers"]["Cookie"] = f"{existing_cookies}; FGTAUTH={cookie}"
                    else:
                        kwargs["headers"]["Cookie"] = f"FGTAUTH={cookie}"
                    logger.debug("Injected FortiGate authentication cookie in request")

            # Step 2: Make the request
            response = original_method(*args, **kwargs)

            # Step 3: Check if response contains FortiGate HTML
            try:
                text = response.text if hasattr(response, "text") else ""
            except (AttributeError, UnicodeDecodeError):
                return response

            if text and is_fortinet_response(text):
                auth_url = extract_fgtauth_url(text)
                
                logger.error(
                    f"FortiGate authentication required! "
                    f"Auth URL: {auth_url or 'Not found in response'}"
                )
                # Replace HTML response with JSON error response
                # This allows atlassian-python-api to process it as JSON
                json_error = (
                    '{"error": "fortinet_auth_required", '
                    '"auth_required": true, '
                    f'"auth_url": "{auth_url or ""}", '
                    '"message": "FortiGate authentication required. '
                    '1. Visit the auth_url in your browser to authenticate. '
                    '2. Extract the FGTAUTH cookie from browser DevTools. '
                    '3. Call set_fortinet_cookie tool with the cookie value. '
                    '4. Retry your original request."}'
                )
                response._content = json_error.encode("utf-8")
                response.headers["Content-Type"] = "application/json"
                return response

            return response

        return wrapped_method

    # Wrap all HTTP methods
    for method_name in ["request", "get", "post", "put", "delete", "patch", "head"]:
        original = getattr(session, method_name, None)
        if original:
            setattr(session, method_name, create_wrapped_method(original))

    logger.debug("FortiGate detection wrapper installed on all session HTTP methods")

