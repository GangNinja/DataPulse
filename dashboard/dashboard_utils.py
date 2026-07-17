"""Formatting and parsing utilities for the Streamlit dashboard."""

from typing import Any


HEALTH_CATEGORY_ORDER = {
    "Excellent": 1,
    "Very Good": 2,
    "Good": 3,
    "Average": 4,
    "Needs Attention": 5,
}


def format_number(value: int | float | None) -> str:
    """
    Format a numeric dashboard value.

    Args:
        value: Numeric value from the warehouse.

    Returns:
        str: Human-friendly display value.
    """
    if value is None:
        return "0"

    numeric_value = float(value)

    if abs(numeric_value) >= 1_000_000:
        return f"{numeric_value / 1_000_000:.1f}M"
    if abs(numeric_value) >= 1_000:
        return f"{numeric_value / 1_000:.1f}K"
    if numeric_value.is_integer():
        return f"{int(numeric_value)}"

    return f"{numeric_value:.2f}"


def format_percent(value: int | float | str | None) -> str:
    """Format a value as a percentage string."""
    if value is None:
        return "0%"
    if isinstance(value, str):
        return value if value.endswith("%") else f"{value}%"

    numeric_value = float(value)
    if numeric_value.is_integer():
        return f"{int(numeric_value)}%"

    return f"{numeric_value:.2f}%"


def sort_health_distribution(
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Sort health distribution rows by category quality."""
    return sorted(
        rows,
        key=lambda row: HEALTH_CATEGORY_ORDER.get(
            str(row.get("health_category")),
            99,
        ),
    )


def build_kpi_cards(kpis: dict[str, Any]) -> list[dict[str, str]]:
    """
    Build homepage KPI card values.

    Args:
        kpis: Raw KPI values from dashboard data access.

    Returns:
        list[dict[str, str]]: Label/value pairs for Streamlit metrics.
    """
    return [
        {
            "label": "Total Repositories",
            "value": format_number(kpis.get("total_repositories")),
        },
        {
            "label": "Average Stars",
            "value": format_number(kpis.get("average_stars")),
        },
        {
            "label": "Average Forks",
            "value": format_number(kpis.get("average_forks")),
        },
        {
            "label": "Average Health",
            "value": format_number(kpis.get("average_health_score")),
        },
    ]


def _normalize_report_key(value: str) -> str:
    """Convert a report label into a snake_case key."""
    return value.strip().lower().replace(" ", "_")


def parse_quality_report(report_text: str | None) -> dict[str, str]:
    """
    Parse a plain-text quality report into key/value pairs.

    Args:
        report_text: Text content from the latest data quality report.

    Returns:
        dict[str, str]: Parsed quality report fields.
    """
    if not report_text:
        return {}

    parsed_report: dict[str, str] = {}
    for line in report_text.splitlines():
        if ":" not in line or line.strip().startswith("-"):
            continue

        key, value = line.split(":", maxsplit=1)
        parsed_report[_normalize_report_key(key)] = value.strip()

    return parsed_report


def build_quality_summary_cards(
    parsed_report: dict[str, str],
) -> list[dict[str, str]]:
    """Build KPI cards from parsed quality report data."""
    return [
        {
            "label": "Records Processed",
            "value": parsed_report.get("records_processed", "0"),
        },
        {
            "label": "Valid Records",
            "value": parsed_report.get("valid_records", "0"),
        },
        {
            "label": "Rejected Records",
            "value": parsed_report.get("rejected_records", "0"),
        },
        {
            "label": "Quality Score",
            "value": format_percent(parsed_report.get("quality_score", "0%")),
        },
    ]
