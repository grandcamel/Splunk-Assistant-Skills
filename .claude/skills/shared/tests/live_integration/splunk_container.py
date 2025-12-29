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

import os
import time
import logging
from typing import Optional

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs
import requests

logger = logging.getLogger(__name__)


class SplunkContainer(DockerContainer):
    """
    Splunk Enterprise container for integration testing.

    Environment Variables:
        SPLUNK_TEST_IMAGE: Docker image (default: splunk/splunk:latest)
        SPLUNK_TEST_PASSWORD: Admin password (default: testpassword123)
        SPLUNK_TEST_HEC_TOKEN: HEC token (default: test-hec-token)

    Example:
        with SplunkContainer() as splunk:
            client = splunk.get_client()
            # Run tests...
    """

    # Default configuration
    DEFAULT_IMAGE = "splunk/splunk:latest"
    DEFAULT_PASSWORD = "testpassword123"
    DEFAULT_HEC_TOKEN = "test-hec-token-12345"
    MANAGEMENT_PORT = 8089
    WEB_PORT = 8000
    HEC_PORT = 8088

    # Startup configuration
    STARTUP_TIMEOUT = 300  # 5 minutes max for Splunk to start
    HEALTH_CHECK_INTERVAL = 5  # Check every 5 seconds

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
        # Note: These are set via Docker, may need adjustment
        self.with_kwargs(mem_limit="4g")

    def start(self) -> "SplunkContainer":
        """Start the container and wait for Splunk to be ready."""
        logger.info(f"Starting Splunk container ({self.splunk_image})...")
        super().start()

        # Wait for Splunk to be fully ready
        self._wait_for_splunk_ready()

        logger.info(f"Splunk ready at {self.get_management_url()}")
        return self

    def _wait_for_splunk_ready(self) -> None:
        """Wait for Splunk to be fully initialized and accepting connections."""
        start_time = time.time()

        # First, wait for the "Ansible playbook complete" log message
        # This indicates Splunk has finished initial setup
        try:
            wait_for_logs(
                self,
                "Ansible playbook complete",
                timeout=self.STARTUP_TIMEOUT,
            )
        except TimeoutError:
            # Fallback: some versions may not have this exact message
            logger.warning("Did not find Ansible complete message, checking health...")

        # Then verify the management port is actually responding
        management_url = self.get_management_url()
        while time.time() - start_time < self.STARTUP_TIMEOUT:
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
        import sys
        from pathlib import Path

        # Add shared lib to path
        lib_path = Path(__file__).parent.parent.parent / "scripts" / "lib"
        if str(lib_path) not in sys.path:
            sys.path.insert(0, str(lib_path))

        from splunk_client import SplunkClient

        # Parse host and port from management URL
        url = self.get_management_url()
        # URL format: https://host:port
        host_port = url.replace("https://", "").replace("http://", "")
        host, port = host_port.rsplit(":", 1)

        return SplunkClient(
            base_url=f"https://{host}",
            port=int(port),
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

        # Parse host and port
        host_port = self.url.replace("https://", "").replace("http://", "")
        if ":" in host_port:
            self.host, port_str = host_port.rsplit(":", 1)
            self.port = int(port_str)
        else:
            self.host = host_port
            self.port = 8089

    def get_management_url(self) -> str:
        """Get the management API URL."""
        return self.url

    def get_client(self):
        """Get a configured SplunkClient instance."""
        import sys
        from pathlib import Path

        lib_path = Path(__file__).parent.parent.parent / "scripts" / "lib"
        if str(lib_path) not in sys.path:
            sys.path.insert(0, str(lib_path))

        from splunk_client import SplunkClient

        kwargs = {
            "base_url": f"https://{self.host}",
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


def get_splunk_connection():
    """
    Get a Splunk connection, preferring external if configured.

    Environment Variables:
        SPLUNK_TEST_URL: External Splunk URL (skips Docker)
        SPLUNK_TEST_TOKEN: Bearer token for external Splunk
        SPLUNK_TEST_USERNAME: Username for external Splunk
        SPLUNK_TEST_PASSWORD: Password for external Splunk

    Returns:
        SplunkContainer or ExternalSplunkConnection
    """
    external_url = os.environ.get("SPLUNK_TEST_URL")

    if external_url:
        logger.info(f"Using external Splunk instance: {external_url}")
        return ExternalSplunkConnection(
            url=external_url,
            token=os.environ.get("SPLUNK_TEST_TOKEN"),
            username=os.environ.get("SPLUNK_TEST_USERNAME"),
            password=os.environ.get("SPLUNK_TEST_PASSWORD"),
        )
    else:
        logger.info("Using Docker Splunk container")
        return SplunkContainer()
