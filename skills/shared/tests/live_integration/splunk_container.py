#!/usr/bin/env python3
"""
Splunk Docker Container for Integration Testing

Provides a testcontainers-based Splunk Enterprise container with:
- Automatic startup and health checking
- License acceptance and admin password configuration
- Port mapping for management (8089) and web (8000) ports
- HTTP Event Collector (HEC) token setup
- Configurable Splunk version
"""

import logging
import os
import threading
import time
from typing import Optional
from urllib.parse import urlparse

import requests
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs

logger = logging.getLogger(__name__)


class SplunkContainer(DockerContainer):
    """
    Splunk Enterprise container for integration testing.

    Environment Variables:
        SPLUNK_TEST_IMAGE: Docker image (default: splunk/splunk:latest)
        SPLUNK_TEST_PASSWORD: Admin password (default: testpassword123)
        SPLUNK_TEST_HEC_TOKEN: HEC token (default: test-hec-token)
        SPLUNK_TEST_STARTUP_TIMEOUT: Max startup wait in seconds (default: 300)
        SPLUNK_TEST_HEALTH_INTERVAL: Health check interval in seconds (default: 5)
        SPLUNK_TEST_MEM_LIMIT: Container memory limit (default: 4g)

    Example:
        with SplunkContainer() as splunk:
            client = splunk.get_client()
            # Run tests...
    """

    # Default configuration
    DEFAULT_IMAGE = "splunk/splunk:latest"
    # ==========================================================================
    # WARNING: LOCAL TESTING ONLY - DO NOT USE IN PRODUCTION
    # ==========================================================================
    # These are intentionally obvious placeholder credentials for local Docker
    # testing. They MUST be replaced via environment variables for any real use:
    #   - SPLUNK_TEST_PASSWORD: Override the admin password
    #   - SPLUNK_TEST_HEC_TOKEN: Override the HEC token
    # ==========================================================================
    DEFAULT_PASSWORD = "REPLACE_ME_testpassword123"  # nosec - test credential only
    DEFAULT_HEC_TOKEN = "REPLACE_ME_test-hec-token"  # nosec - test credential only
    MANAGEMENT_PORT = 8089
    WEB_PORT = 8000
    HEC_PORT = 8088

    # Startup configuration - configurable via environment variables
    STARTUP_TIMEOUT = int(os.environ.get("SPLUNK_TEST_STARTUP_TIMEOUT", "300"))
    HEALTH_CHECK_INTERVAL = int(os.environ.get("SPLUNK_TEST_HEALTH_INTERVAL", "5"))

    def __init__(
        self,
        image: Optional[str] = None,
        password: Optional[str] = None,
        hec_token: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize Splunk container.

        Args:
            image: Docker image (default: splunk/splunk:latest)
            password: Admin password (default: testpassword123)
            hec_token: HTTP Event Collector token
            **kwargs: Additional arguments for DockerContainer
        """
        self.splunk_image = image or os.environ.get(
            "SPLUNK_TEST_IMAGE", self.DEFAULT_IMAGE
        )
        self.splunk_password = password or os.environ.get(
            "SPLUNK_TEST_PASSWORD", self.DEFAULT_PASSWORD
        )
        self.hec_token = hec_token or os.environ.get(
            "SPLUNK_TEST_HEC_TOKEN", self.DEFAULT_HEC_TOKEN
        )

        super().__init__(image=self.splunk_image, **kwargs)

        # Configure container
        self._configure()

    def _configure(self) -> None:
        """Configure container environment and ports."""
        # Environment variables for Splunk
        # Note: Both SPLUNK_GENERAL_TERMS and SPLUNK_START_ARGS are required
        # for newer Splunk Docker images (9.x+)
        self.with_env("SPLUNK_GENERAL_TERMS", "--accept-sgt-current-at-splunk-com")
        self.with_env("SPLUNK_START_ARGS", "--accept-license")
        self.with_env("SPLUNK_PASSWORD", self.splunk_password)
        self.with_env("SPLUNK_HEC_TOKEN", self.hec_token)

        # Enable HEC
        self.with_env("SPLUNK_HEC_SSL", "false")

        # Expose ports
        self.with_exposed_ports(
            self.MANAGEMENT_PORT,
            self.WEB_PORT,
            self.HEC_PORT,
        )

        # Resource limits (Splunk needs memory)
        # Configurable via SPLUNK_TEST_MEM_LIMIT env var
        mem_limit = os.environ.get("SPLUNK_TEST_MEM_LIMIT", "4g")
        self.with_kwargs(mem_limit=mem_limit)

        # Reference counting for shared container support
        # Lock ensures thread-safe access for pytest-xdist parallel execution
        self._lock = threading.Lock()
        self._ref_count = 0
        self._is_started = False

    def start(self) -> "SplunkContainer":
        """Start the container and wait for Splunk to be ready.

        Uses reference counting to support sharing across pytest sessions.
        Thread-safe for parallel test execution with pytest-xdist.
        """
        with self._lock:
            self._ref_count += 1

            if self._is_started:
                logger.info(
                    f"Reusing already-started Splunk container (ref_count={self._ref_count})"
                )
                return self

            logger.info(f"Starting Splunk container ({self.splunk_image})...")
            super().start()

            # Wait for Splunk to be fully ready
            self._wait_for_splunk_ready()

            self._is_started = True
            logger.info(f"Splunk ready at {self.get_management_url()}")
            return self

    def stop(self, **kwargs) -> None:
        """Stop the container only when all references are released.

        Thread-safe for parallel test execution with pytest-xdist.
        """
        with self._lock:
            self._ref_count -= 1

            if self._ref_count > 0:
                logger.info(
                    f"Keeping Splunk container running (ref_count={self._ref_count})"
                )
                return

            if self._is_started:
                logger.info("Stopping Splunk container (ref_count=0)")
                self._is_started = False
                super().stop(**kwargs)

    def _wait_for_splunk_ready(self) -> None:
        """Wait for Splunk to be fully initialized and accepting connections."""
        start_time = time.time()

        # First, wait for the "Ansible playbook complete" log message
        # This indicates Splunk has finished initial setup
        # Use half the timeout for logs, reserve half for health checks
        log_timeout = self.STARTUP_TIMEOUT // 2
        try:
            wait_for_logs(
                self,
                "Ansible playbook complete",
                timeout=log_timeout,
            )
        except TimeoutError:
            # Fallback: some versions may not have this exact message
            logger.warning("Did not find Ansible complete message, checking health...")

        # Calculate remaining timeout for health checks
        elapsed = time.time() - start_time
        remaining_timeout = max(30, self.STARTUP_TIMEOUT - elapsed)  # At least 30s for health

        # Then verify the management port is actually responding
        management_url = self.get_management_url()
        health_start = time.time()
        while time.time() - health_start < remaining_timeout:
            try:
                response = requests.get(
                    f"{management_url}/services/server/info",
                    auth=("admin", self.splunk_password),
                    verify=False,
                    timeout=10,
                )
                if response.status_code == 200:
                    logger.info("Splunk management API is responding")
                    return
            except requests.exceptions.RequestException:
                pass

            time.sleep(self.HEALTH_CHECK_INTERVAL)

        raise TimeoutError(
            f"Splunk did not become ready within {self.STARTUP_TIMEOUT} seconds"
        )

    def get_management_url(self) -> str:
        """Get the management API URL (port 8089)."""
        host = self.get_container_host_ip()
        port = self.get_exposed_port(self.MANAGEMENT_PORT)
        return f"https://{host}:{port}"

    def get_web_url(self) -> str:
        """Get the web UI URL (port 8000)."""
        host = self.get_container_host_ip()
        port = self.get_exposed_port(self.WEB_PORT)
        return f"http://{host}:{port}"

    def get_hec_url(self) -> str:
        """Get the HTTP Event Collector URL (port 8088)."""
        host = self.get_container_host_ip()
        port = self.get_exposed_port(self.HEC_PORT)
        return f"http://{host}:{port}"

    def get_client(self):
        """
        Get a configured SplunkClient instance.

        Returns:
            SplunkClient: Client configured for this container
        """
        from splunk_as import SplunkClient

        # Parse host and port from management URL using urlparse for IPv6 support
        url = self.get_management_url()
        parsed = urlparse(url)
        host = parsed.hostname or "localhost"
        port = parsed.port or 8089

        return SplunkClient(
            base_url=f"{parsed.scheme}://{host}",
            port=port,
            username="admin",
            password=self.splunk_password,
            verify_ssl=False,
        )

    def get_connection_info(self) -> dict:
        """Get connection information for external tools."""
        return {
            "management_url": self.get_management_url(),
            "web_url": self.get_web_url(),
            "hec_url": self.get_hec_url(),
            "username": "admin",
            "password": self.splunk_password,
            "hec_token": self.hec_token,
        }

    def create_test_index(self, index_name: str = "test_index") -> bool:
        """
        Create a test index.

        Args:
            index_name: Name of the index to create

        Returns:
            True if created successfully
        """
        client = self.get_client()
        try:
            client.post(
                "/data/indexes",
                data={"name": index_name},
                operation=f"create index {index_name}",
            )
            logger.info(f"Created test index: {index_name}")
            return True
        except Exception as e:
            logger.warning(f"Failed to create index {index_name}: {e}")
            return False

    def delete_test_index(self, index_name: str = "test_index") -> bool:
        """
        Delete a test index.

        Args:
            index_name: Name of the index to delete

        Returns:
            True if deleted successfully
        """
        client = self.get_client()
        try:
            client.delete(
                f"/data/indexes/{index_name}",
                operation=f"delete index {index_name}",
            )
            logger.info(f"Deleted test index: {index_name}")
            return True
        except Exception as e:
            logger.warning(f"Failed to delete index {index_name}: {e}")
            return False

    def execute_search(self, spl: str, **kwargs) -> list:
        """
        Execute a search and return results.

        Args:
            spl: SPL query
            **kwargs: Additional search parameters

        Returns:
            List of result dictionaries
        """
        client = self.get_client()
        response = client.post(
            "/search/jobs/oneshot",
            data={
                "search": spl,
                "output_mode": "json",
                "earliest_time": kwargs.get("earliest_time", "-24h"),
                "latest_time": kwargs.get("latest_time", "now"),
            },
            timeout=kwargs.get("timeout", 60),
            operation="execute search",
        )
        return response.get("results", [])


class ExternalSplunkConnection:
    """
    Connection to an external Splunk instance (non-Docker).

    Used when SPLUNK_TEST_URL is set in the environment.
    """

    def __init__(
        self,
        url: str,
        token: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        """
        Initialize external connection.

        Args:
            url: Splunk management URL (e.g., https://splunk.example.com:8089)
            token: Bearer token for authentication
            username: Username for basic auth
            password: Password for basic auth
        """
        self.url = url.rstrip("/")
        self.token = token
        self.username = username
        self.password = password

        # Parse host and port using urlparse for IPv6 support
        parsed = urlparse(self.url)
        self.host = parsed.hostname or "localhost"
        self.port = parsed.port or 8089
        self.scheme = parsed.scheme or "https"

    def get_management_url(self) -> str:
        """Get the management API URL."""
        return self.url

    def get_client(self):
        """Get a configured SplunkClient instance."""
        from splunk_as import SplunkClient

        kwargs = {
            "base_url": f"{self.scheme}://{self.host}",
            "port": self.port,
            "verify_ssl": False,  # Default to False for testing with self-signed certs
        }

        if self.token:
            kwargs["token"] = self.token
        elif self.username and self.password:
            kwargs["username"] = self.username
            kwargs["password"] = self.password

        return SplunkClient(**kwargs)

    def get_connection_info(self) -> dict:
        """Get connection information."""
        return {
            "management_url": self.url,
            "username": self.username,
            "token": "***" if self.token else None,
        }

    def create_test_index(self, index_name: str = "test_index") -> bool:
        """Create a test index."""
        client = self.get_client()
        try:
            client.post(
                "/data/indexes",
                data={"name": index_name},
                operation=f"create index {index_name}",
            )
            return True
        except Exception:
            return False

    def delete_test_index(self, index_name: str = "test_index") -> bool:
        """Delete a test index."""
        client = self.get_client()
        try:
            client.delete(
                f"/data/indexes/{index_name}",
                operation=f"delete index {index_name}",
            )
            return True
        except Exception:
            return False

    def execute_search(self, spl: str, **kwargs) -> list:
        """Execute a search and return results."""
        client = self.get_client()
        response = client.post(
            "/search/jobs/oneshot",
            data={
                "search": spl,
                "output_mode": "json",
                "earliest_time": kwargs.get("earliest_time", "-24h"),
                "latest_time": kwargs.get("latest_time", "now"),
            },
            timeout=kwargs.get("timeout", 60),
            operation="execute search",
        )
        return response.get("results", [])


# Global singletons for connection reuse across pytest sessions
# Lock ensures thread-safe singleton creation for pytest-xdist
_shared_container = None
_shared_external = None
_container_lock = threading.Lock()


def get_splunk_connection():
    """
    Get a Splunk connection, preferring external if configured.

    Uses a singleton pattern to ensure only one connection is created
    across all pytest sessions/conftest files. Thread-safe for parallel
    test execution with pytest-xdist.

    Environment Variables:
        SPLUNK_TEST_URL: External Splunk URL (skips Docker)
        SPLUNK_TEST_TOKEN: Bearer token for external Splunk
        SPLUNK_TEST_USERNAME: Username for external Splunk
        SPLUNK_TEST_PASSWORD: Password for external Splunk

    Returns:
        SplunkContainer or ExternalSplunkConnection
    """
    global _shared_container, _shared_external

    external_url = os.environ.get("SPLUNK_TEST_URL")

    if external_url:
        # Use double-checked locking for thread-safe singleton
        if _shared_external is None:
            with _container_lock:
                if _shared_external is None:
                    logger.info(f"Creating external Splunk connection: {external_url}")
                    _shared_external = ExternalSplunkConnection(
                        url=external_url,
                        token=os.environ.get("SPLUNK_TEST_TOKEN"),
                        username=os.environ.get("SPLUNK_TEST_USERNAME"),
                        password=os.environ.get("SPLUNK_TEST_PASSWORD"),
                    )
                else:
                    logger.info("Reusing existing external Splunk connection")
        else:
            logger.info("Reusing existing external Splunk connection")
        return _shared_external
    else:
        # Use double-checked locking for thread-safe singleton
        if _shared_container is None:
            with _container_lock:
                # Check again inside lock (double-checked locking)
                if _shared_container is None:
                    logger.info("Creating new Docker Splunk container (singleton)")
                    _shared_container = SplunkContainer()
                else:
                    logger.info("Reusing existing Docker Splunk container (singleton)")
        else:
            logger.info("Reusing existing Docker Splunk container (singleton)")
        return _shared_container
