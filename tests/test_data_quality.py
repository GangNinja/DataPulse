"""Tests for Week 4 Session 1 data quality improvements."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

from quality.cleaning import (
    DEFAULT_DESCRIPTION,
    DEFAULT_LANGUAGE,
    clean_repository_record,
    coerce_datetime,
)
from quality.quality_checker import run_repository_quality_checks
from quality.report import save_quality_report
from quality.validation import is_valid_url, validate_repository_record


def _repository_record(repo_name: str = "DataPulse") -> dict[str, object]:
    """Create a valid transformed repository record."""
    timestamp = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return {
        "id": 1,
        "repo_name": repo_name,
        "owner": "OpenAI",
        "description": "Repository intelligence platform.",
        "stars": 100,
        "forks": 20,
        "watchers": 10,
        "open_issues": 2,
        "size_kb": 4096,
        "language": "Python",
        "default_branch": "main",
        "created_at": timestamp,
        "updated_at": timestamp,
        "html_url": "https://github.com/openai/datapulse",
        "last_synced": timestamp,
    }


def test_clean_repository_record_fixes_missing_values_and_whitespace() -> None:
    """Cleaning should trim strings and fill safe defaults."""
    record = _repository_record(repo_name=" Data Pulse ")
    record["description"] = " "
    record["language"] = None
    record["owner"] = " OpenAI "

    result = clean_repository_record(record)

    assert result.record["repo_name"] == "Data-Pulse"
    assert result.record["owner"] == "OpenAI"
    assert result.record["description"] == DEFAULT_DESCRIPTION
    assert result.record["language"] == DEFAULT_LANGUAGE
    assert result.missing_values_fixed == 2


def test_coerce_datetime_converts_valid_timestamp_strings() -> None:
    """Timestamp strings should be converted when possible."""
    parsed_value = coerce_datetime("2024-01-01T00:00:00Z")

    assert parsed_value == datetime(2024, 1, 1, tzinfo=timezone.utc)


def test_validate_repository_record_detects_invalid_values() -> None:
    """Validation should catch empty names, bad URLs, negatives, and dates."""
    record = _repository_record(repo_name="")
    record["html_url"] = "not-a-url"
    record["stars"] = -1
    record["forks"] = -2
    record["watchers"] = -3
    record["created_at"] = datetime.now(timezone.utc) + timedelta(days=10)

    issues = validate_repository_record(record)
    issue_fields = {issue.field for issue in issues}

    assert "repo_name" in issue_fields
    assert "html_url" in issue_fields
    assert "stars" in issue_fields
    assert "forks" in issue_fields
    assert "watchers" in issue_fields
    assert "created_at" in issue_fields


def test_url_validation_accepts_only_http_and_https_urls() -> None:
    """URL validation should reject empty, malformed, and non-web URLs."""
    assert is_valid_url("https://github.com/openai/datapulse")
    assert is_valid_url("http://github.com/openai/datapulse")
    assert not is_valid_url("github.com/openai/datapulse")
    assert not is_valid_url("ftp://github.com/openai/datapulse")
    assert not is_valid_url("")


def test_quality_checker_removes_duplicate_repositories_and_ids() -> None:
    """Quality checks should remove duplicate repo keys and source IDs."""
    repo_one = _repository_record(repo_name="DataPulse")
    duplicate_name = _repository_record(repo_name="datapulse")
    duplicate_name["id"] = 2
    duplicate_id = _repository_record(repo_name="OtherRepo")

    result = run_repository_quality_checks(
        [repo_one, duplicate_name, duplicate_id]
    )

    assert len(result.valid_records) == 1
    assert result.report.records_processed == 3
    assert result.report.duplicate_records == 2
    assert result.report.valid_records == 1


def test_quality_checker_rejects_invalid_records() -> None:
    """Invalid records should be rejected and counted in the report."""
    valid_record = _repository_record()
    invalid_record = _repository_record(repo_name="Broken")
    invalid_record["id"] = 2
    invalid_record["html_url"] = "bad-url"

    result = run_repository_quality_checks([valid_record, invalid_record])

    assert len(result.valid_records) == 1
    assert result.report.invalid_urls == 1
    assert result.report.rejected_records == 1
    assert result.report.quality_score == 50.0


def test_quality_report_generation_writes_timestamped_and_latest_files() -> None:
    """Quality report generation should write files for dashboard reuse."""
    result = run_repository_quality_checks([_repository_record()])
    reports_directory = Path("reports") / "test_quality_reports"

    report_path = save_quality_report(
        result.report,
        reports_directory=reports_directory,
    )
    latest_report_path = reports_directory / "data_quality_report_latest.txt"

    assert report_path.exists()
    assert latest_report_path.exists()
    assert "DATA QUALITY REPORT" in report_path.read_text(encoding="utf-8")
    assert "Records Processed   : 1" in latest_report_path.read_text(
        encoding="utf-8"
    )
