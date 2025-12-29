#!/usr/bin/env python3
"""Unit tests for validators module."""

import pytest

from splunk_assistant_skills_lib import (
    ValidationError,
    validate_app_name,
    validate_index_name,
    validate_output_mode,
    validate_port,
    validate_sid,
    validate_spl,
    validate_time_modifier,
    validate_url,
)


class TestValidateSid:
    """Tests for validate_sid."""

    def test_valid_sid(self):
        assert validate_sid("1703779200.12345") == "1703779200.12345"

    def test_valid_sid_with_user(self):
        assert validate_sid("1703779200.12345_admin") == "1703779200.12345_admin"

    def test_empty_sid_raises(self):
        with pytest.raises(ValidationError):
            validate_sid("")

    def test_none_sid_raises(self):
        with pytest.raises(ValidationError):
            validate_sid(None)


class TestValidateSpl:
    """Tests for validate_spl."""

    def test_valid_simple_search(self):
        assert validate_spl("index=main | head 10") == "index=main | head 10"

    def test_valid_complex_search(self):
        spl = "index=main sourcetype=access | stats count by status | sort -count"
        assert validate_spl(spl) == spl

    def test_unbalanced_parentheses_raises(self):
        with pytest.raises(ValidationError):
            validate_spl("index=main | eval x=(1+2")

    def test_empty_pipe_raises(self):
        with pytest.raises(ValidationError):
            validate_spl("index=main || stats count")

    def test_trailing_pipe_raises(self):
        with pytest.raises(ValidationError):
            validate_spl("index=main |")

    def test_empty_spl_raises(self):
        with pytest.raises(ValidationError):
            validate_spl("")


class TestValidateTimeModifier:
    """Tests for validate_time_modifier."""

    def test_relative_hour(self):
        assert validate_time_modifier("-1h") == "-1h"

    def test_relative_day(self):
        assert validate_time_modifier("-7d") == "-7d"

    def test_snap_to_hour(self):
        assert validate_time_modifier("@h") == "@h"

    def test_snap_to_day(self):
        assert validate_time_modifier("@d") == "@d"

    def test_combined(self):
        assert validate_time_modifier("-1d@d") == "-1d@d"

    def test_now(self):
        assert validate_time_modifier("now") == "now"

    def test_epoch(self):
        assert validate_time_modifier("1703779200") == "1703779200"

    def test_invalid_raises(self):
        with pytest.raises(ValidationError):
            validate_time_modifier("invalid")


class TestValidateIndexName:
    """Tests for validate_index_name."""

    def test_valid_index(self):
        assert validate_index_name("main") == "main"

    def test_index_with_underscore(self):
        assert validate_index_name("my_index") == "my_index"

    def test_internal_index(self):
        assert validate_index_name("_internal") == "_internal"

    def test_too_long_raises(self):
        with pytest.raises(ValidationError):
            validate_index_name("a" * 100)


class TestValidateAppName:
    """Tests for validate_app_name."""

    def test_valid_app(self):
        assert validate_app_name("search") == "search"

    def test_app_with_underscore(self):
        assert validate_app_name("my_app") == "my_app"

    def test_starts_with_number_raises(self):
        with pytest.raises(ValidationError):
            validate_app_name("123app")


class TestValidatePort:
    """Tests for validate_port."""

    def test_valid_port(self):
        assert validate_port(8089) == 8089

    def test_string_port(self):
        assert validate_port("8089") == 8089

    def test_invalid_port_raises(self):
        with pytest.raises(ValidationError):
            validate_port(0)

    def test_too_high_port_raises(self):
        with pytest.raises(ValidationError):
            validate_port(70000)


class TestValidateUrl:
    """Tests for validate_url."""

    def test_valid_https_url(self):
        result = validate_url("https://splunk.example.com")
        assert result == "https://splunk.example.com"

    def test_adds_https_scheme(self):
        result = validate_url("splunk.example.com")
        assert result == "https://splunk.example.com"

    def test_require_https_fails_http(self):
        with pytest.raises(ValidationError):
            validate_url("http://splunk.example.com", require_https=True)


class TestValidateOutputMode:
    """Tests for validate_output_mode."""

    def test_json(self):
        assert validate_output_mode("json") == "json"

    def test_csv(self):
        assert validate_output_mode("csv") == "csv"

    def test_invalid_raises(self):
        with pytest.raises(ValidationError):
            validate_output_mode("invalid")
