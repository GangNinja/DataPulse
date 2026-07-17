"""Data quality orchestration for repository records."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from quality.cleaning import clean_repository_record
from quality.report import DataQualityReport, calculate_quality_score
from quality.validation import validate_repository_record
from utils.logger import get_logger


logger = get_logger(__name__)


@dataclass(frozen=True)
class DataQualityResult:
    """Clean repository records and their quality report."""

    valid_records: list[dict[str, Any]]
    report: DataQualityReport


def _repository_key(record: dict[str, Any]) -> tuple[str, str] | None:
    """Return a case-insensitive repository identity key."""
    owner = record.get("owner")
    repo_name = record.get("repo_name")

    if not isinstance(owner, str) or not owner.strip():
        return None
    if not isinstance(repo_name, str) or not repo_name.strip():
        return None

    return owner.strip().lower(), repo_name.strip().lower()


def _repository_id(record: dict[str, Any]) -> Any:
    """Return a source repository identifier when present."""
    if "repository_id" in record:
        return record["repository_id"]

    return record.get("id")


def run_repository_quality_checks(
    records: list[dict[str, Any]],
) -> DataQualityResult:
    """
    Clean, de-duplicate, validate, and report on repository records.

    Args:
        records: Repository records prepared by ingestion.

    Returns:
        DataQualityResult: Valid cleaned records and report values.
    """
    logger.info("Running Data Quality Checks")

    valid_records: list[dict[str, Any]] = []
    issue_messages: list[str] = []
    seen_repositories: set[tuple[str, str]] = set()
    seen_repository_ids: set[Any] = set()
    duplicate_records = 0
    invalid_urls = 0
    rejected_records = 0
    missing_values_fixed = 0

    for record in records:
        cleaning_result = clean_repository_record(record)
        cleaned_record = cleaning_result.record
        missing_values_fixed += cleaning_result.missing_values_fixed

        repository_key = _repository_key(cleaned_record)
        repository_id = _repository_id(cleaned_record)

        if repository_key is not None and repository_key in seen_repositories:
            duplicate_records += 1
            continue

        if repository_id is not None and repository_id in seen_repository_ids:
            duplicate_records += 1
            continue

        if repository_key is not None:
            seen_repositories.add(repository_key)
        if repository_id is not None:
            seen_repository_ids.add(repository_id)

        issues = validate_repository_record(cleaned_record)
        if issues:
            rejected_records += 1
            issue_summary = "; ".join(issue.message for issue in issues)
            repo_name = cleaned_record.get("repo_name") or "<unknown>"
            issue_messages.append(f"{repo_name}: {issue_summary}")

            if any(issue.field == "html_url" for issue in issues):
                invalid_urls += 1
                logger.warning("Invalid URL detected")

            logger.error("Repository validation failed")
            continue

        valid_records.append(cleaned_record)

    if missing_values_fixed > 0:
        logger.info("Missing values cleaned")
    if duplicate_records > 0:
        logger.info("Duplicate repositories removed")

    report = DataQualityReport(
        records_processed=len(records),
        valid_records=len(valid_records),
        duplicate_records=duplicate_records,
        missing_values_fixed=missing_values_fixed,
        invalid_urls=invalid_urls,
        rejected_records=rejected_records,
        quality_score=calculate_quality_score(len(valid_records), len(records)),
        generated_at=datetime.now(timezone.utc),
        issue_messages=issue_messages,
    )

    return DataQualityResult(valid_records=valid_records, report=report)
