"""Repository data cleaning helpers."""

from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Any


DEFAULT_DESCRIPTION = "No description available"
DEFAULT_LANGUAGE = "Unknown"


@dataclass(frozen=True)
class CleaningResult:
    """Result from cleaning one repository record."""

    record: dict[str, Any]
    missing_values_fixed: int


def _clean_string(value: Any) -> str | None:
    """Trim a string value and convert empty strings to None."""
    if value is None:
        return None
    if not isinstance(value, str):
        value = str(value)

    cleaned = value.strip()
    return cleaned or None


def normalize_repository_name(value: Any) -> str | None:
    """
    Normalize a repository name.

    GitHub repository names should not contain whitespace. If whitespace appears
    in incoming data, replace it with hyphens after trimming.
    """
    cleaned = _clean_string(value)
    if cleaned is None:
        return None

    return re.sub(r"\s+", "-", cleaned)


def coerce_datetime(value: Any) -> datetime | Any:
    """
    Convert timestamp strings to UTC datetimes when possible.

    Args:
        value: Existing datetime or timestamp-like value.

    Returns:
        datetime | Any: Parsed datetime, original value if parsing fails.
    """
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    if not isinstance(value, str) or not value.strip():
        return value

    normalized_value = value.strip().replace("Z", "+00:00")
    try:
        parsed_value = datetime.fromisoformat(normalized_value)
    except ValueError:
        return value

    if parsed_value.tzinfo is None:
        return parsed_value.replace(tzinfo=timezone.utc)

    return parsed_value.astimezone(timezone.utc)


def clean_repository_record(record: dict[str, Any]) -> CleaningResult:
    """
    Clean one repository record before validation and persistence.

    Args:
        record: Raw or transformed repository record.

    Returns:
        CleaningResult: Cleaned record and count of missing values fixed.
    """
    cleaned_record = dict(record)
    missing_values_fixed = 0

    cleaned_record["repo_name"] = normalize_repository_name(
        cleaned_record.get("repo_name")
    )

    for field_name in ("owner", "default_branch", "html_url"):
        cleaned_record[field_name] = _clean_string(cleaned_record.get(field_name))

    description = _clean_string(cleaned_record.get("description"))
    if description is None:
        cleaned_record["description"] = DEFAULT_DESCRIPTION
        missing_values_fixed += 1
    else:
        cleaned_record["description"] = description

    language = _clean_string(cleaned_record.get("language"))
    if language is None:
        cleaned_record["language"] = DEFAULT_LANGUAGE
        missing_values_fixed += 1
    else:
        cleaned_record["language"] = language

    for field_name in ("created_at", "updated_at", "last_synced"):
        cleaned_record[field_name] = coerce_datetime(cleaned_record.get(field_name))

    return CleaningResult(
        record=cleaned_record,
        missing_values_fixed=missing_values_fixed,
    )
