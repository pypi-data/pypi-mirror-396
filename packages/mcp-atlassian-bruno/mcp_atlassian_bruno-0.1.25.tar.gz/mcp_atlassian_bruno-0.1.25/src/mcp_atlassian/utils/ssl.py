"""SSL-related utility functions for MCP Atlassian."""

import logging
import ssl
from typing import Any
from urllib.parse import urlparse

from requests.adapters import HTTPAdapter
from requests.sessions import Session
from urllib3.poolmanager import PoolManager

logger = logging.getLogger("mcp-atlassian")


class SSLIgnoreAdapter(HTTPAdapter):
    """HTTP adapter that ignores SSL verification.

    A custom transport adapter that disables SSL certificate verification for specific domains.
    This implementation ensures that both verify_mode is set to CERT_NONE and check_hostname
    is disabled, which is required for properly ignoring SSL certificates.

    This adapter also enables legacy SSL renegotiation which may be required for some older servers.
    Note that this reduces security and should only be used when absolutely necessary.
    """

    def init_poolmanager(
        self, connections: int, maxsize: int, block: bool = False, **pool_kwargs: Any
    ) -> None:
        """Initialize the connection pool manager with SSL verification disabled.

        This method is called when the adapter is created, and it's the proper place to
        disable SSL verification completely.

        Args:
            connections: Number of connections to save in the pool
            maxsize: Maximum number of connections in the pool
            block: Whether to block when the pool is full
            pool_kwargs: Additional arguments for the pool manager
        """
        # Configure SSL context to disable verification completely
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        # Enable legacy SSL renegotiation
        context.options |= 0x4  # SSL_OP_LEGACY_SERVER_CONNECT
        context.options |= 0x40000  # SSL_OP_ALLOW_UNSAFE_LEGACY_RENEGOTIATION

        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=context,
            **pool_kwargs,
        )

    def cert_verify(self, conn: Any, url: str, verify: bool, cert: Any | None) -> None:
        """Override cert verification to disable SSL verification.

        This method is still included for backward compatibility, but the main
        SSL disabling happens in init_poolmanager.

        Args:
            conn: The connection
            url: The URL being requested
            verify: The original verify parameter (ignored)
            cert: Client certificate path
        """
        super().cert_verify(conn, url, verify=False, cert=cert)


class SSLCustomCertAdapter(HTTPAdapter):
    """HTTP adapter that uses a custom CA certificate.

    A custom transport adapter that enables SSL verification using a custom CA certificate file.
    This is useful for self-signed certificates or internal CAs that are not in the system trust store.
    """

    def __init__(self, cert_path: str, **kwargs: Any) -> None:
        """Initialize the adapter with a custom certificate path.

        Args:
            cert_path: Path to the CA certificate file (PEM format)
            **kwargs: Additional arguments passed to HTTPAdapter
        """
        self.cert_path = cert_path
        super().__init__(**kwargs)

    def init_poolmanager(
        self, connections: int, maxsize: int, block: bool = False, **pool_kwargs: Any
    ) -> None:
        """Initialize the connection pool manager with custom CA certificate.

        Args:
            connections: Number of connections to save in the pool
            maxsize: Maximum number of connections in the pool
            block: Whether to block when the pool is full
            pool_kwargs: Additional arguments for the pool manager
        """
        # Configure SSL context to use custom certificate
        context = ssl.create_default_context(cafile=self.cert_path)
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED

        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=context,
            **pool_kwargs,
        )


def configure_ssl_verification(
    service_name: str,
    url: str,
    session: Session,
    ssl_verify: bool,
    cert_path: str | None = None,
) -> None:
    """Configure SSL verification for a specific service.

    If a custom certificate path is provided, this function will configure the session
    to use that certificate for verification. If SSL verification is disabled without
    a certificate path, this function will configure the session to bypass certificate
    validation.

    Args:
        service_name: Name of the service for logging (e.g., "Confluence", "Jira")
        url: The base URL of the service
        session: The requests session to configure
        ssl_verify: Whether SSL verification should be enabled
        cert_path: Optional path to custom CA certificate file
    """
    # Get the domain from the configured URL
    domain = urlparse(url).netloc

    if cert_path:
        logger.info(f"{service_name} using custom CA certificate from: {cert_path}")
        adapter = SSLCustomCertAdapter(cert_path=cert_path)
        session.mount(f"https://{domain}", adapter)
        session.mount(f"http://{domain}", adapter)
    elif not ssl_verify:
        logger.warning(
            f"{service_name} SSL verification disabled. This is insecure and should only be used in testing environments."
        )
        adapter = SSLIgnoreAdapter()
        session.mount(f"https://{domain}", adapter)
        session.mount(f"http://{domain}", adapter)


def get_verify_ssl_for_atlassian_client(
    ssl_verify: bool, cert_path: str | None = None
) -> bool | str:
    """Get the verify_ssl parameter value for atlassian-python-api clients.

    The atlassian-python-api library accepts verify_ssl as either a boolean or
    a string path to a CA certificate file.

    Args:
        ssl_verify: Whether SSL verification should be enabled
        cert_path: Optional path to custom CA certificate file

    Returns:
        bool or str: False if verification disabled, True if enabled without custom cert,
                     or string path to certificate file if custom cert provided
    """
    if cert_path:
        return cert_path
    return ssl_verify
