#!/usr/bin/env python3
"""Unit tests for time_utils module."""

from datetime import datetime

import pytest
from splunk_assistant_skills_lib import (
    format_splunk_time,
    get_relative_time,
    get_time_range_presets,
    parse_splunk_time,
    validate_time_range,
)


class TestParseSplunkTime:
    """Tests for parse_splunk_time."""

    def test_now(self):
        ref = datetime(2024, 1, 1, 12, 0, 0)
        result = parse_splunk_time("now", reference=ref)
        assert result == ref

    def test_relative_hour(self):
        ref = datetime(2024, 1, 1, 12, 0, 0)
        result = parse_splunk_time("-1h", reference=ref)
        assert result == datetime(2024, 1, 1, 11, 0, 0)

    def test_relative_day(self):
        ref = datetime(2024, 1, 1, 12, 0, 0)
        result = parse_splunk_time("-1d", reference=ref)
        assert result == datetime(2023, 12, 31, 12, 0, 0)

    def test_epoch(self):
        # Epoch timestamp for Jan 1, 2024 00:00:00 UTC
        # Result is in local timezone, so we just check it's a valid datetime
        result = parse_splunk_time("1704067200")
        assert result.year in (2023, 2024)  # Depends on timezone
        assert result is not None

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            parse_splunk_time("invalid")


class TestFormatSplunkTime:
    """Tests for format_splunk_time."""

    def test_epoch_format(self):
        # format_splunk_time takes a time_str and returns human-readable format
        result = format_splunk_time("1704067200")
        assert result is not None
        assert len(result) > 0

    def test_relative_format(self):
        result = format_splunk_time("-1h")
        assert result is not None
        assert len(result) > 0


class TestValidateTimeRange:
    """Tests for validate_time_range."""

    def test_valid_range(self):
        is_valid, error = validate_time_range("-1h", "now")
        assert is_valid is True
        assert error is None

    def test_invalid_range(self):
        is_valid, error = validate_time_range("now", "-1h")
        assert is_valid is False
        assert error is not None


class TestGetRelativeTime:
    """Tests for get_relative_time."""

    def test_negative_hour(self):
        result = get_relative_time(-1, "h")
        assert result == "-1h"

    def test_with_snap(self):
        result = get_relative_time(-1, "d", snap_to="d")
        assert result == "-1d@d"


class TestGetTimeRangePresets:
    """Tests for get_time_range_presets."""

    def test_has_common_presets(self):
        presets = get_time_range_presets()
        assert "last_hour" in presets
        assert "last_24_hours" in presets
        assert "today" in presets

    def test_preset_format(self):
        presets = get_time_range_presets()
        earliest, latest = presets["last_hour"]
        assert earliest == "-1h"
        assert latest == "now"
