#!/usr/bin/env python3
"""Unit tests for time_utils module."""

import sys
from pathlib import Path
from datetime import datetime
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts' / 'lib'))

from time_utils import (
    parse_splunk_time,
    format_splunk_time,
    validate_time_range,
    get_relative_time,
    get_time_range_presets,
)


class TestParseSplunkTime:
    """Tests for parse_splunk_time."""

    def test_now(self):
        ref = datetime(2024, 1, 1, 12, 0, 0)
        result = parse_splunk_time('now', reference=ref)
        assert result == ref

    def test_relative_hour(self):
        ref = datetime(2024, 1, 1, 12, 0, 0)
        result = parse_splunk_time('-1h', reference=ref)
        assert result == datetime(2024, 1, 1, 11, 0, 0)

    def test_relative_day(self):
        ref = datetime(2024, 1, 1, 12, 0, 0)
        result = parse_splunk_time('-1d', reference=ref)
        assert result == datetime(2023, 12, 31, 12, 0, 0)

    def test_epoch(self):
        result = parse_splunk_time('1704067200')
        assert result.year == 2024

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            parse_splunk_time('invalid')


class TestFormatSplunkTime:
    """Tests for format_splunk_time."""

    def test_epoch_format(self):
        dt = datetime(2024, 1, 1, 12, 0, 0)
        result = format_splunk_time(dt, format_type='epoch')
        assert result.isdigit()

    def test_iso_format(self):
        dt = datetime(2024, 1, 1, 12, 0, 0)
        result = format_splunk_time(dt, format_type='iso')
        assert '2024-01-01' in result


class TestValidateTimeRange:
    """Tests for validate_time_range."""

    def test_valid_range(self):
        is_valid, error = validate_time_range('-1h', 'now')
        assert is_valid is True
        assert error is None

    def test_invalid_range(self):
        is_valid, error = validate_time_range('now', '-1h')
        assert is_valid is False
        assert error is not None


class TestGetRelativeTime:
    """Tests for get_relative_time."""

    def test_negative_hour(self):
        result = get_relative_time(-1, 'h')
        assert result == '-1h'

    def test_with_snap(self):
        result = get_relative_time(-1, 'd', snap_to='d')
        assert result == '-1d@d'


class TestGetTimeRangePresets:
    """Tests for get_time_range_presets."""

    def test_has_common_presets(self):
        presets = get_time_range_presets()
        assert 'last_hour' in presets
        assert 'last_24_hours' in presets
        assert 'today' in presets

    def test_preset_format(self):
        presets = get_time_range_presets()
        earliest, latest = presets['last_hour']
        assert earliest == '-1h'
        assert latest == 'now'
