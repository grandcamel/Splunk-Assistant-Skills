#!/usr/bin/env python3
"""
Configuration Manager for Splunk Skills

Provides multi-source configuration management with profile support.
Configuration priority (highest to lowest):
    1. Environment variables
    2. .claude/settings.local.json (personal, gitignored)
    3. .claude/settings.json (team defaults)
    4. Built-in defaults

Environment Variables:
    SPLUNK_TOKEN - JWT Bearer token (preferred auth)
    SPLUNK_USERNAME - Username for Basic Auth
    SPLUNK_PASSWORD - Password for Basic Auth
    SPLUNK_SITE_URL - Splunk host URL
    SPLUNK_MANAGEMENT_PORT - Management port (default: 8089)
    SPLUNK_PROFILE - Profile name to use
    SPLUNK_VERIFY_SSL - SSL verification (true/false)
    SPLUNK_DEFAULT_APP - Default app context
    SPLUNK_DEFAULT_INDEX - Default search index
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from .splunk_client import SplunkClient


class ConfigManager:
    """Manages configuration from multiple sources with profile support."""

    DEFAULT_CONFIG = {
        'splunk': {
            'default_profile': 'default',
            'profiles': {
                'default': {
                    'url': '',
                    'port': 8089,
                    'auth_method': 'bearer',
                    'default_app': 'search',
                    'default_index': 'main',
                    'verify_ssl': True,
                    'deployment_type': 'on-prem',
                }
            },
            'api': {
                'timeout': 30,
                'search_timeout': 300,
                'max_retries': 3,
                'retry_backoff': 2.0,
                'default_output_mode': 'json',
                'prefer_v2_api': True,
            },
            'search_defaults': {
                'earliest_time': '-24h',
                'latest_time': 'now',
                'max_count': 50000,
                'status_buckets': 300,
                'auto_cancel': 300,
            },
        }
    }

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize configuration manager.

        Args:
            config_dir: Path to .claude directory (auto-detected if not provided)
        """
        self.config_dir = config_dir or self._find_config_dir()
        self._config: Optional[Dict[str, Any]] = None

    def _find_config_dir(self) -> Path:
        """Find the .claude configuration directory."""
        # Start from current directory and walk up
        current = Path.cwd()
        while current != current.parent:
            config_path = current / '.claude'
            if config_path.is_dir():
                return config_path
            current = current.parent

        # Default to current directory's .claude
        return Path.cwd() / '.claude'

    def _load_json_file(self, path: Path) -> Dict[str, Any]:
        """Load JSON file if it exists."""
        if path.is_file():
            try:
                with open(path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from all sources with proper priority.

        Returns:
            Merged configuration dictionary
        """
        if self._config is not None:
            return self._config

        # Start with defaults
        config = self.DEFAULT_CONFIG.copy()

        # Load settings.json (team defaults)
        settings_path = self.config_dir / 'settings.json'
        settings = self._load_json_file(settings_path)
        config = self._deep_merge(config, settings)

        # Load settings.local.json (personal overrides)
        local_path = self.config_dir / 'settings.local.json'
        local_settings = self._load_json_file(local_path)
        config = self._deep_merge(config, local_settings)

        self._config = config
        return config

    def get_profile_config(self, profile_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get configuration for a specific profile.

        Args:
            profile_name: Profile name (uses default if not specified)

        Returns:
            Profile configuration dictionary
        """
        config = self.load_config()
        splunk_config = config.get('splunk', {})

        # Determine profile to use
        if profile_name is None:
            profile_name = os.environ.get('SPLUNK_PROFILE') or splunk_config.get('default_profile', 'default')

        profiles = splunk_config.get('profiles', {})
        profile = profiles.get(profile_name, {})

        # Merge with default profile if exists
        if profile_name != 'default' and 'default' in profiles:
            profile = self._deep_merge(profiles['default'], profile)

        # Apply environment variable overrides
        env_overrides = self._get_env_overrides()
        profile = self._deep_merge(profile, env_overrides)

        # Add API and search defaults
        profile['api'] = splunk_config.get('api', self.DEFAULT_CONFIG['splunk']['api'])
        profile['search_defaults'] = splunk_config.get('search_defaults', self.DEFAULT_CONFIG['splunk']['search_defaults'])

        return profile

    def _get_env_overrides(self) -> Dict[str, Any]:
        """Get configuration overrides from environment variables."""
        overrides = {}

        if os.environ.get('SPLUNK_SITE_URL'):
            overrides['url'] = os.environ['SPLUNK_SITE_URL']

        if os.environ.get('SPLUNK_MANAGEMENT_PORT'):
            try:
                overrides['port'] = int(os.environ['SPLUNK_MANAGEMENT_PORT'])
            except ValueError:
                pass

        if os.environ.get('SPLUNK_TOKEN'):
            overrides['token'] = os.environ['SPLUNK_TOKEN']
            overrides['auth_method'] = 'bearer'

        if os.environ.get('SPLUNK_USERNAME'):
            overrides['username'] = os.environ['SPLUNK_USERNAME']

        if os.environ.get('SPLUNK_PASSWORD'):
            overrides['password'] = os.environ['SPLUNK_PASSWORD']
            if not os.environ.get('SPLUNK_TOKEN'):
                overrides['auth_method'] = 'basic'

        if os.environ.get('SPLUNK_VERIFY_SSL'):
            overrides['verify_ssl'] = os.environ['SPLUNK_VERIFY_SSL'].lower() in ('true', '1', 'yes')

        if os.environ.get('SPLUNK_DEFAULT_APP'):
            overrides['default_app'] = os.environ['SPLUNK_DEFAULT_APP']

        if os.environ.get('SPLUNK_DEFAULT_INDEX'):
            overrides['default_index'] = os.environ['SPLUNK_DEFAULT_INDEX']

        return overrides

    def get_client_kwargs(self, profile_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get keyword arguments for SplunkClient initialization.

        Args:
            profile_name: Profile name to use

        Returns:
            Dictionary of kwargs for SplunkClient
        """
        profile = self.get_profile_config(profile_name)
        api_config = profile.get('api', {})

        kwargs = {
            'base_url': profile.get('url', ''),
            'port': profile.get('port', 8089),
            'timeout': api_config.get('timeout', 30),
            'verify_ssl': profile.get('verify_ssl', True),
            'max_retries': api_config.get('max_retries', 3),
            'retry_backoff': api_config.get('retry_backoff', 2.0),
        }

        # Add authentication
        auth_method = profile.get('auth_method', 'bearer')
        if auth_method == 'bearer' and profile.get('token'):
            kwargs['token'] = profile['token']
        elif profile.get('username') and profile.get('password'):
            kwargs['username'] = profile['username']
            kwargs['password'] = profile['password']
        elif profile.get('token'):
            kwargs['token'] = profile['token']

        return kwargs

    def validate_config(self, profile_name: Optional[str] = None) -> list:
        """
        Validate configuration and return list of issues.

        Args:
            profile_name: Profile name to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        profile = self.get_profile_config(profile_name)

        if not profile.get('url'):
            errors.append("Missing Splunk URL. Set SPLUNK_SITE_URL or configure in settings.json")

        auth_method = profile.get('auth_method', 'bearer')
        if auth_method == 'bearer':
            if not profile.get('token'):
                errors.append("Missing Splunk token. Set SPLUNK_TOKEN or configure in settings.local.json")
        else:
            if not profile.get('username'):
                errors.append("Missing Splunk username. Set SPLUNK_USERNAME or configure in settings.local.json")
            if not profile.get('password'):
                errors.append("Missing Splunk password. Set SPLUNK_PASSWORD or configure in settings.local.json")

        return errors


# Global config manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get or create global ConfigManager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config(profile: Optional[str] = None) -> Dict[str, Any]:
    """
    Get configuration for specified profile.

    Args:
        profile: Profile name (uses default if not specified)

    Returns:
        Profile configuration dictionary
    """
    return get_config_manager().get_profile_config(profile)


def get_splunk_client(profile: Optional[str] = None) -> SplunkClient:
    """
    Create SplunkClient instance from configuration.

    Args:
        profile: Profile name (uses default if not specified)

    Returns:
        Configured SplunkClient instance

    Raises:
        ValidationError: If configuration is invalid
    """
    from .error_handler import ValidationError

    manager = get_config_manager()

    # Validate configuration
    errors = manager.validate_config(profile)
    if errors:
        raise ValidationError('\n'.join(errors))

    # Get client kwargs and create client
    kwargs = manager.get_client_kwargs(profile)
    return SplunkClient(**kwargs)


def get_search_defaults(profile: Optional[str] = None) -> Dict[str, Any]:
    """
    Get search default settings.

    Args:
        profile: Profile name

    Returns:
        Search defaults dictionary
    """
    config = get_config(profile)
    return config.get('search_defaults', ConfigManager.DEFAULT_CONFIG['splunk']['search_defaults'])


def get_api_settings(profile: Optional[str] = None) -> Dict[str, Any]:
    """
    Get API settings.

    Args:
        profile: Profile name

    Returns:
        API settings dictionary
    """
    config = get_config(profile)
    return config.get('api', ConfigManager.DEFAULT_CONFIG['splunk']['api'])
