"""
Splunk Assistant Skills - Shared Library

This module provides common utilities for interacting with the Splunk REST API.

Components:
    - splunk_client: HTTP client with retry logic and dual auth support
    - config_manager: Multi-source configuration management
    - error_handler: Exception hierarchy and error handling
    - validators: Input validation for Splunk-specific formats
    - formatters: Output formatting utilities
    - spl_helper: SPL query building and parsing
    - job_poller: Async job state polling
    - time_utils: Splunk time modifier handling
"""

try:
    from .config_manager import ConfigManager, get_config, get_splunk_client
    from .error_handler import (
        AuthenticationError,
        AuthorizationError,
        JobFailedError,
        NotFoundError,
        RateLimitError,
        SearchQuotaError,
        ServerError,
        SplunkError,
        ValidationError,
        handle_errors,
        handle_splunk_error,
        print_error,
    )
    from .formatters import (
        export_csv,
        format_job_status,
        format_json,
        format_metadata,
        format_saved_search,
        format_search_results,
        format_table,
        print_info,
        print_success,
        print_warning,
    )
    from .job_poller import (
        JobState,
        cancel_job,
        finalize_job,
        get_dispatch_state,
        poll_job_status,
    )
    from .spl_helper import (
        add_field_extraction,
        add_time_bounds,
        build_search,
        estimate_search_complexity,
        optimize_spl,
        parse_spl_commands,
        validate_spl_syntax,
    )
    from .splunk_client import SplunkClient
    from .time_utils import (
        format_splunk_time,
        get_relative_time,
        parse_splunk_time,
        validate_time_range,
    )
    from .validators import (
        validate_app_name,
        validate_index_name,
        validate_output_mode,
        validate_port,
        validate_sid,
        validate_spl,
        validate_time_modifier,
        validate_url,
    )
except ImportError:
    from config_manager import ConfigManager, get_config, get_splunk_client
    from error_handler import (
        AuthenticationError,
        AuthorizationError,
        JobFailedError,
        NotFoundError,
        RateLimitError,
        SearchQuotaError,
        ServerError,
        SplunkError,
        ValidationError,
        handle_errors,
        handle_splunk_error,
        print_error,
    )
    from formatters import (
        export_csv,
        format_job_status,
        format_json,
        format_metadata,
        format_saved_search,
        format_search_results,
        format_table,
        print_info,
        print_success,
        print_warning,
    )
    from job_poller import (
        JobState,
        cancel_job,
        finalize_job,
        get_dispatch_state,
        poll_job_status,
    )
    from spl_helper import (
        add_field_extraction,
        add_time_bounds,
        build_search,
        estimate_search_complexity,
        optimize_spl,
        parse_spl_commands,
        validate_spl_syntax,
    )
    from splunk_client import SplunkClient
    from time_utils import (
        format_splunk_time,
        get_relative_time,
        parse_splunk_time,
        validate_time_range,
    )
    from validators import (
        validate_app_name,
        validate_index_name,
        validate_output_mode,
        validate_port,
        validate_sid,
        validate_spl,
        validate_time_modifier,
        validate_url,
    )

__version__ = "1.0.0"
__all__ = [
    # Client
    "SplunkClient",
    # Config
    "get_splunk_client",
    "get_config",
    "ConfigManager",
    # Errors
    "SplunkError",
    "AuthenticationError",
    "AuthorizationError",
    "ValidationError",
    "NotFoundError",
    "RateLimitError",
    "SearchQuotaError",
    "JobFailedError",
    "ServerError",
    "handle_errors",
    "handle_splunk_error",
    "print_error",
    # Validators
    "validate_sid",
    "validate_spl",
    "validate_time_modifier",
    "validate_index_name",
    "validate_app_name",
    "validate_port",
    "validate_url",
    "validate_output_mode",
    # Formatters
    "format_search_results",
    "format_job_status",
    "format_metadata",
    "format_saved_search",
    "format_table",
    "format_json",
    "export_csv",
    "print_success",
    "print_warning",
    "print_info",
    # SPL Helper
    "build_search",
    "add_time_bounds",
    "add_field_extraction",
    "validate_spl_syntax",
    "parse_spl_commands",
    "estimate_search_complexity",
    "optimize_spl",
    # Job Poller
    "poll_job_status",
    "get_dispatch_state",
    "JobState",
    "cancel_job",
    "finalize_job",
    # Time Utils
    "parse_splunk_time",
    "format_splunk_time",
    "validate_time_range",
    "get_relative_time",
]
