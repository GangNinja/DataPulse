"""Repository data quality validation rules."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlparse


REQUIRED_FIELDS = {
    "repo_name",
    "owner",
    "stars",
    "forks",
    "watchers",
    "open_issues",
    "size_kb",
    "default_branch",
    "created_at",
    "updated_at",
    "html_url",
    "last_synced",
}

NON_NEGATIVE_FIELDS = (
    "stars",
    "forks",
    "watchers",
    "open_issues",
    "size_kb",
)

DATE_FIELDS = ("created_at", "updated_at", "last_synced")


@dataclass(frozen=True)
class ValidationIssue:
    """A single data quality validation issue."""

    field: str
    message: str
    severity: str = "error"


def is_valid_url(value: Any) -> bool:
    """
    Check whether a value is a valid HTTP or HTTPS URL.

    Args:
        value: URL value to validate.

    Returns:
        bool: True when the value is a valid web URL.
    """
    if not isinstance(value, str) or not value.strip():
        return False

    parsed_url = urlparse(value.strip())
    return parsed_url.scheme in {"http", "https"} and bool(parsed_url.netloc)


def _is_missing_string(value: Any) -> bool:
    """Return True when a value is not a useful string."""
    return not isinstance(value, str) or not value.strip()


def _validate_required_fields(record: dict[str, Any]) -> list[ValidationIssue]:
    """Validate required repository fields."""
    issues: list[ValidationIssue] = []

    for field_name in sorted(REQUIRED_FIELDS):
        if field_name not in record or record[field_name] is None:
            issues.append(
                ValidationIssue(field_name, f"{field_name} is required.")
            )

    return issues


def _validate_non_negative_fields(
    record: dict[str, Any],
) -> list[ValidationIssue]:
    """Validate numeric fields that must be non-negative."""
    issues: list[ValidationIssue] = []

    for field_name in NON_NEGATIVE_FIELDS:
        value = record.get(field_name)
        if value is None:
            continue
        if not isinstance(value, int) or value < 0:
            issues.append(
                ValidationIssue(
                    field_name,
                    f"{field_name} must be a non-negative integer.",
                )
            )

    return issues


def _validate_date_fields(record: dict[str, Any]) -> list[ValidationIssue]:
    """Validate repository timestamp fields."""
    issues: list[ValidationIssue] = []
    now = datetime.now(timezone.utc) + timedelta(days=1)

    for field_name in DATE_FIELDS:
        value = record.get(field_name)
        if value is None:
            continue
        if not isinstance(value, datetime):
            issues.append(
                ValidationIssue(field_name, f"{field_name} must be a datetime.")
            )
            continue

        date_value = value
        if date_value.tzinfo is None:
            date_value = date_value.replace(tzinfo=timezone.utc)

        if date_value.astimezone(timezone.utc) > now:
            issues.append(
                ValidationIssue(field_name, f"{field_name} cannot be in future.")
            )

    created_at = record.get("created_at")
    updated_at = record.get("updated_at")
    if isinstance(created_at, datetime) and isinstance(updated_at, datetime):
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        if updated_at.tzinfo is None:
            updated_at = updated_at.replace(tzinfo=timezone.utc)
        if updated_at < created_at:
            issues.append(
                ValidationIssue(
                    "updated_at",
                    "updated_at cannot be earlier than created_at.",
                )
            )

    return issues


def validate_repository_record(record: dict[str, Any]) -> list[ValidationIssue]:
    """
    Validate a cleaned repository record.

    Args:
        record: Repository data prepared for persistence.

    Returns:
        list[ValidationIssue]: Validation issues found in the record.
    """
    issues = _validate_required_fields(record)

    if _is_missing_string(record.get("repo_name")):
        issues.append(
            ValidationIssue("repo_name", "Repository name cannot be empty.")
        )
    if _is_missing_string(record.get("owner")):
        issues.append(ValidationIssue("owner", "Repository owner cannot be empty."))
    if _is_missing_string(record.get("default_branch")):
        issues.append(
            ValidationIssue("default_branch", "Default branch cannot be empty.")
        )

    if not is_valid_url(record.get("html_url")):
        issues.append(ValidationIssue("html_url", "Invalid repository URL."))

    issues.extend(_validate_non_negative_fields(record))
    issues.extend(_validate_date_fields(record))
    return issues
