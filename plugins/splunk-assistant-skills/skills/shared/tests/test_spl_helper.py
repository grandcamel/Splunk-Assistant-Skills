#!/usr/bin/env python3
"""Unit tests for spl_helper module."""

import pytest
from splunk_assistant_skills_lib import (
    add_field_extraction,
    add_head_limit,
    add_time_bounds,
    build_search,
    estimate_search_complexity,
    optimize_spl,
    parse_spl_commands,
    validate_spl_syntax,
)


class TestBuildSearch:
    """Tests for build_search."""

    def test_simple_search(self):
        result = build_search("index=main")
        assert result == "index=main"

    def test_with_time_bounds(self):
        result = build_search("index=main", earliest_time="-1h", latest_time="now")
        assert "earliest=-1h" in result
        assert "latest=now" in result

    def test_with_fields(self):
        result = build_search("index=main", fields=["host", "status"])
        assert "| fields host, status" in result

    def test_with_head(self):
        result = build_search("index=main", head=100)
        assert "| head 100" in result


class TestAddTimeBounds:
    """Tests for add_time_bounds."""

    def test_adds_earliest(self):
        result = add_time_bounds("index=main", earliest="-1h")
        assert "earliest=-1h" in result

    def test_adds_latest(self):
        result = add_time_bounds("index=main", latest="now")
        assert "latest=now" in result

    def test_no_duplicate_if_present(self):
        result = add_time_bounds("earliest=-1h index=main", earliest="-2h")
        assert result.count("earliest") == 1


class TestAddFieldExtraction:
    """Tests for add_field_extraction."""

    def test_adds_fields(self):
        result = add_field_extraction("index=main", ["host", "status"])
        assert "| fields host, status" in result

    def test_no_duplicate_if_present(self):
        result = add_field_extraction("index=main | fields host", ["status"])
        assert result.count("fields") == 1


class TestAddHeadLimit:
    """Tests for add_head_limit."""

    def test_adds_head(self):
        result = add_head_limit("index=main", 100)
        assert "| head 100" in result

    def test_no_duplicate_if_present(self):
        result = add_head_limit("index=main | head 50", 100)
        assert result.count("head") == 1


class TestValidateSplSyntax:
    """Tests for validate_spl_syntax."""

    def test_valid_simple(self):
        is_valid, issues = validate_spl_syntax("index=main")
        assert is_valid is True
        assert len(issues) == 0

    def test_valid_complex(self):
        is_valid, issues = validate_spl_syntax(
            "index=main | stats count by host | sort -count"
        )
        assert is_valid is True

    def test_unbalanced_parens(self):
        is_valid, issues = validate_spl_syntax("index=main | eval x=(1+2")
        assert is_valid is False
        assert "Unbalanced parentheses" in issues[0]

    def test_empty_pipe(self):
        is_valid, issues = validate_spl_syntax("index=main || head")
        assert is_valid is False

    def test_trailing_pipe(self):
        is_valid, issues = validate_spl_syntax("index=main |")
        assert is_valid is False


class TestParseSplCommands:
    """Tests for parse_spl_commands."""

    def test_simple_search(self):
        commands = parse_spl_commands("index=main")
        assert len(commands) == 1
        assert commands[0][0] == "search"

    def test_pipeline(self):
        commands = parse_spl_commands("index=main | stats count | sort -count")
        assert len(commands) == 3
        assert commands[0][0] == "search"
        assert commands[1][0] == "stats"
        assert commands[2][0] == "sort"

    def test_generating_command(self):
        commands = parse_spl_commands("| rest /services/server/info")
        assert commands[0][0] == "rest"


class TestEstimateSearchComplexity:
    """Tests for estimate_search_complexity."""

    def test_simple(self):
        assert estimate_search_complexity("index=main | head 100") == "simple"

    def test_medium(self):
        assert (
            estimate_search_complexity("index=main | stats count by host | sort -count")
            == "medium"
        )

    def test_complex_transaction(self):
        assert estimate_search_complexity("index=main | transaction host") == "complex"

    def test_complex_join(self):
        assert (
            estimate_search_complexity(
                "index=main | join type=left host [search index=other]"
            )
            == "complex"
        )


class TestOptimizeSpl:
    """Tests for optimize_spl."""

    def test_suggests_time_bounds(self):
        _, suggestions = optimize_spl("index=main")
        assert any("time bounds" in s.lower() for s in suggestions)

    def test_suggests_fields(self):
        _, suggestions = optimize_spl("search index=main | head 100")
        assert any("fields" in s.lower() for s in suggestions)
