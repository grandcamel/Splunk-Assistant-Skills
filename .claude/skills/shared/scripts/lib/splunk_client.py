#!/usr/bin/env python3
"""
Splunk REST API HTTP Client

Provides a robust HTTP client for interacting with the Splunk REST API.
Supports both JWT Bearer token and Basic Auth authentication.
Includes automatic retry with exponential backoff for transient failures.

Features:
    - Dual authentication: JWT Bearer token (preferred) or Basic Auth
    - Automatic retry on 429/5xx errors with exponential backoff
    - Configurable timeouts for short and long-running operations
    - SSL verification with option to disable for self-signed certs
    - Content negotiation (JSON by default)
    - Streaming support for large result sets
"""

import time
import urllib.parse
from typing import Any, Dict, Generator, Iterator, Optional, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class SplunkClient:
    """HTTP client for Splunk REST API with retry logic and dual auth support."""

    DEFAULT_PORT = 8089
    DEFAULT_TIMEOUT = 30
    DEFAULT_SEARCH_TIMEOUT = 300
    MAX_RETRIES = 3
    RETRY_BACKOFF = 2.0
    RETRY_STATUS_CODES = [429, 500, 502, 503, 504]

    def __init__(
        self,
        base_url: str,
        token: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        port: int = DEFAULT_PORT,
        timeout: int = DEFAULT_TIMEOUT,
        verify_ssl: bool = True,
        max_retries: int = MAX_RETRIES,
        retry_backoff: float = RETRY_BACKOFF,
    ):
        """
        Initialize Splunk client.

        Args:
            base_url: Splunk host URL (e.g., https://splunk.example.com)
            token: JWT Bearer token for authentication (preferred)
            username: Username for Basic Auth (alternative to token)
            password: Password for Basic Auth (alternative to token)
            port: Management port (default: 8089)
            timeout: Request timeout in seconds (default: 30)
            verify_ssl: Verify SSL certificates (default: True)
            max_retries: Maximum retry attempts (default: 3)
            retry_backoff: Exponential backoff multiplier (default: 2.0)

        Raises:
            ValueError: If neither token nor username+password provided
        """
        # Normalize base URL
        base_url = base_url.rstrip("/")
        if not base_url.startswith(("http://", "https://")):
            base_url = f"https://{base_url}"

        self.base_url = f"{base_url}:{port}/services"
        self.port = port
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff

        # Create session with retry strategy
        self.session = requests.Session()

        # Configure retry adapter
        retry_strategy = Retry(
            total=0,  # We handle retries manually for better control
            backoff_factor=retry_backoff,
            status_forcelist=self.RETRY_STATUS_CODES,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        # Set default headers
        self.session.headers.update(
            {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            }
        )

        # Configure authentication
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"
            self.auth_method = "bearer"
        elif username and password:
            self.session.auth = (username, password)
            self.auth_method = "basic"
        else:
            raise ValueError("Must provide either token or username+password")

    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint path."""
        endpoint = endpoint.lstrip("/")
        if not endpoint.startswith("services"):
            return f"{self.base_url}/{endpoint}"
        # Handle full path starting with services
        base = self.base_url.rsplit("/services", 1)[0]
        return f"{base}/{endpoint}"

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        stream: bool = False,
        operation: str = "API request",
    ) -> requests.Response:
        """
        Make HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            params: URL query parameters
            data: Form data for POST/PUT
            json_body: JSON body for POST/PUT
            timeout: Override default timeout
            stream: Enable streaming response
            operation: Description for error messages

        Returns:
            Response object

        Raises:
            SplunkError: On API errors after retries exhausted
        """
        try:
            from .error_handler import handle_splunk_error
        except ImportError:
            from error_handler import handle_splunk_error

        url = self._build_url(endpoint)
        request_timeout = timeout or self.timeout

        # Ensure output_mode=json if not specified
        if params is None:
            params = {}
        if "output_mode" not in params:
            params["output_mode"] = "json"

        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    data=data,
                    json=json_body,
                    timeout=request_timeout,
                    verify=self.verify_ssl,
                    stream=stream,
                )

                # Check for errors
                if response.status_code >= 400:
                    # Retry on specific status codes
                    if response.status_code in self.RETRY_STATUS_CODES:
                        if attempt < self.max_retries:
                            wait_time = self.retry_backoff**attempt
                            time.sleep(wait_time)
                            continue
                    # Handle error
                    handle_splunk_error(response, operation)

                return response

            except requests.exceptions.Timeout as e:
                last_exception = e
                if attempt < self.max_retries:
                    wait_time = self.retry_backoff**attempt
                    time.sleep(wait_time)
                    continue
                raise

            except requests.exceptions.ConnectionError as e:
                last_exception = e
                if attempt < self.max_retries:
                    wait_time = self.retry_backoff**attempt
                    time.sleep(wait_time)
                    continue
                raise

        # Should not reach here, but just in case
        if last_exception:
            raise last_exception

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        operation: str = "GET request",
    ) -> Dict[str, Any]:
        """
        Make GET request and return JSON response.

        Args:
            endpoint: API endpoint path
            params: URL query parameters
            timeout: Override default timeout
            operation: Description for error messages

        Returns:
            Parsed JSON response
        """
        response = self._request(
            method="GET",
            endpoint=endpoint,
            params=params,
            timeout=timeout,
            operation=operation,
        )
        return response.json()

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        operation: str = "POST request",
    ) -> Dict[str, Any]:
        """
        Make POST request and return JSON response.

        Args:
            endpoint: API endpoint path
            data: Form data
            params: URL query parameters
            timeout: Override default timeout
            operation: Description for error messages

        Returns:
            Parsed JSON response
        """
        response = self._request(
            method="POST",
            endpoint=endpoint,
            data=data,
            params=params,
            timeout=timeout,
            operation=operation,
        )
        return response.json()

    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        operation: str = "PUT request",
    ) -> Dict[str, Any]:
        """
        Make PUT request and return JSON response.

        Args:
            endpoint: API endpoint path
            data: Form data
            params: URL query parameters
            timeout: Override default timeout
            operation: Description for error messages

        Returns:
            Parsed JSON response
        """
        response = self._request(
            method="PUT",
            endpoint=endpoint,
            data=data,
            params=params,
            timeout=timeout,
            operation=operation,
        )
        return response.json()

    def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        operation: str = "DELETE request",
    ) -> Dict[str, Any]:
        """
        Make DELETE request and return JSON response.

        Args:
            endpoint: API endpoint path
            params: URL query parameters
            timeout: Override default timeout
            operation: Description for error messages

        Returns:
            Parsed JSON response
        """
        response = self._request(
            method="DELETE",
            endpoint=endpoint,
            params=params,
            timeout=timeout,
            operation=operation,
        )
        return response.json()

    def upload_file(
        self,
        endpoint: str,
        file_path: str,
        file_field: str = "datafile",
        data: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        operation: str = "file upload",
    ) -> Dict[str, Any]:
        """
        Upload file to Splunk.

        Args:
            endpoint: API endpoint path
            file_path: Path to file to upload
            file_field: Form field name for file (default: datafile)
            data: Additional form data
            timeout: Override default timeout
            operation: Description for error messages

        Returns:
            Parsed JSON response
        """
        try:
            from .error_handler import handle_splunk_error
        except ImportError:
            from error_handler import handle_splunk_error

        url = self._build_url(endpoint)
        request_timeout = timeout or self.timeout

        # Remove Content-Type header for multipart
        headers = dict(self.session.headers)
        headers.pop("Content-Type", None)

        with open(file_path, "rb") as f:
            files = {file_field: f}
            response = self.session.post(
                url=url,
                files=files,
                data=data or {},
                params={"output_mode": "json"},
                timeout=request_timeout,
                verify=self.verify_ssl,
                headers=headers,
            )

        if response.status_code >= 400:
            handle_splunk_error(response, operation)

        return response.json()

    def stream_results(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        chunk_size: int = 8192,
        timeout: Optional[int] = None,
        operation: str = "stream results",
    ) -> Generator[bytes, None, None]:
        """
        Stream results from endpoint.

        Args:
            endpoint: API endpoint path
            params: URL query parameters
            chunk_size: Size of chunks to yield
            timeout: Override default timeout
            operation: Description for error messages

        Yields:
            Chunks of response data
        """
        response = self._request(
            method="GET",
            endpoint=endpoint,
            params=params,
            timeout=timeout or self.DEFAULT_SEARCH_TIMEOUT,
            stream=True,
            operation=operation,
        )

        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                yield chunk

    def stream_lines(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        operation: str = "stream lines",
    ) -> Iterator[str]:
        """
        Stream results line by line.

        Args:
            endpoint: API endpoint path
            params: URL query parameters
            timeout: Override default timeout
            operation: Description for error messages

        Yields:
            Lines of response data
        """
        response = self._request(
            method="GET",
            endpoint=endpoint,
            params=params,
            timeout=timeout or self.DEFAULT_SEARCH_TIMEOUT,
            stream=True,
            operation=operation,
        )

        for line in response.iter_lines(decode_unicode=True):
            if line:
                yield line

    def get_server_info(self) -> Dict[str, Any]:
        """Get Splunk server information."""
        response = self.get("/server/info", operation="get server info")
        if "entry" in response and response["entry"]:
            return response["entry"][0].get("content", {})
        return response

    def whoami(self) -> Dict[str, Any]:
        """Get current user information."""
        response = self.get("/authentication/current-context", operation="whoami")
        if "entry" in response and response["entry"]:
            return response["entry"][0].get("content", {})
        return response

    def test_connection(self) -> bool:
        """
        Test connection to Splunk.

        Returns:
            True if connection successful

        Raises:
            SplunkError: If connection fails
        """
        self.get_server_info()
        return True

    @property
    def is_cloud(self) -> bool:
        """Check if connected to Splunk Cloud."""
        return ".splunkcloud.com" in self.base_url

    def __repr__(self) -> str:
        return f"SplunkClient(base_url={self.base_url!r}, auth_method={self.auth_method!r})"
