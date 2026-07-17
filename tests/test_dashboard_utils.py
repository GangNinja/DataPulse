"""Tests for dashboard utility functions."""

from dashboard.dashboard_utils import (
    build_kpi_cards,
    build_quality_summary_cards,
    format_number,
    format_percent,
    parse_quality_report,
    sort_health_distribution,
)


def test_format_number_creates_dashboard_friendly_values() -> None:
    """Large numbers should be compact for KPI cards."""
    assert format_number(1_250_000) == "1.2M"
    assert format_number(12_500) == "12.5K"
    assert format_number(125) == "125"
    assert format_number(12.3456) == "12.35"
    assert format_number(None) == "0"


def test_format_percent_handles_strings_and_numbers() -> None:
    """Percent values should keep a consistent suffix."""
    assert format_percent(96) == "96%"
    assert format_percent(96.55) == "96.55%"
    assert format_percent("96%") == "96%"
    assert format_percent("96") == "96%"


def test_sort_health_distribution_uses_business_order() -> None:
    """Health categories should appear from best to worst."""
    rows = [
        {"health_category": "Average", "repository_count": 10},
        {"health_category": "Excellent", "repository_count": 1},
        {"health_category": "Needs Attention", "repository_count": 20},
    ]

    sorted_rows = sort_health_distribution(rows)

    assert [row["health_category"] for row in sorted_rows] == [
        "Excellent",
        "Average",
        "Needs Attention",
    ]


def test_build_kpi_cards_formats_dashboard_metrics() -> None:
    """Dashboard KPI cards should expose formatted label/value pairs."""
    cards = build_kpi_cards(
        {
            "total_repositories": 8195,
            "average_stars": 1234.56,
            "average_forks": 44.4,
            "average_health_score": 18.9,
        }
    )

    assert cards[0] == {"label": "Total Repositories", "value": "8.2K"}
    assert cards[1] == {"label": "Average Stars", "value": "1.2K"}
    assert cards[2] == {"label": "Average Forks", "value": "44.40"}
    assert cards[3] == {"label": "Average Health", "value": "18.90"}


def test_parse_quality_report_extracts_summary_values() -> None:
    """Plain-text quality reports should parse into dashboard values."""
    report_text = """
DATA QUALITY REPORT
Records Processed   : 250
Valid Records       : 241
Rejected Records    : 2
Quality Score       : 96%
"""

    parsed_report = parse_quality_report(report_text)

    assert parsed_report["records_processed"] == "250"
    assert parsed_report["valid_records"] == "241"
    assert parsed_report["rejected_records"] == "2"
    assert parsed_report["quality_score"] == "96%"


def test_build_quality_summary_cards_uses_parsed_report_values() -> None:
    """Quality summary cards should be ready for Streamlit metrics."""
    cards = build_quality_summary_cards(
        {
            "records_processed": "250",
            "valid_records": "241",
            "rejected_records": "2",
            "quality_score": "96%",
        }
    )

    assert cards == [
        {"label": "Records Processed", "value": "250"},
        {"label": "Valid Records", "value": "241"},
        {"label": "Rejected Records", "value": "2"},
        {"label": "Quality Score", "value": "96%"},
    ]
