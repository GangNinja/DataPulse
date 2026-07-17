"""Streamlit dashboard for DataPulse analytics."""

from collections.abc import Callable
from pathlib import Path
import sys
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import get_settings
from dashboard.dashboard_utils import (
    build_kpi_cards,
    build_quality_summary_cards,
    parse_quality_report,
    sort_health_distribution,
)
from dashboard.data_access import (
    create_dashboard_engine,
    fetch_dashboard_kpis,
    fetch_health_distribution,
    fetch_healthiest_repositories,
    fetch_language_distribution,
    fetch_repositories_needing_attention,
    fetch_size_distribution,
    fetch_top_repositories,
    read_latest_quality_report,
)
from utils.logger import get_logger


logger = get_logger(__name__)


st.set_page_config(
    page_title="DataPulse Dashboard",
    page_icon="DP",
    layout="wide",
)


@st.cache_resource
def _get_engine() -> Any:
    """Create and cache the dashboard database engine."""
    settings = get_settings()
    return create_dashboard_engine(settings.database_url)


@st.cache_data(ttl=300)
def _load_dashboard_data() -> dict[str, Any]:
    """Load dashboard datasets from PostgreSQL and report files."""
    engine = _get_engine()
    return {
        "kpis": fetch_dashboard_kpis(engine),
        "language_distribution": fetch_language_distribution(engine),
        "health_distribution": sort_health_distribution(
            fetch_health_distribution(engine)
        ),
        "size_distribution": fetch_size_distribution(engine),
        "top_repositories": fetch_top_repositories(engine),
        "healthiest_repositories": fetch_healthiest_repositories(engine),
        "needs_attention": fetch_repositories_needing_attention(engine),
        "quality_report": read_latest_quality_report(),
    }


def _dataframe(rows: list[dict[str, Any]]) -> pd.DataFrame:
    """Convert dashboard rows to a DataFrame."""
    return pd.DataFrame(rows)


def _render_kpi_cards(cards: list[dict[str, str]]) -> None:
    """Render KPI cards using Streamlit metric components."""
    columns = st.columns(len(cards))
    for column, card in zip(columns, cards, strict=True):
        with column:
            st.metric(card["label"], card["value"])


def _render_home(data: dict[str, Any]) -> None:
    """Render dashboard homepage."""
    st.subheader("Overview")
    _render_kpi_cards(build_kpi_cards(data["kpis"]))

    left_column, right_column = st.columns(2)

    with left_column:
        health_df = _dataframe(data["health_distribution"])
        if not health_df.empty:
            fig = px.bar(
                health_df,
                x="health_category",
                y="repository_count",
                color="health_category",
                title="Repository Health Distribution",
                labels={
                    "health_category": "Health Category",
                    "repository_count": "Repositories",
                },
            )
            st.plotly_chart(fig, use_container_width=True)

    with right_column:
        language_df = _dataframe(data["language_distribution"])
        if not language_df.empty:
            fig = px.bar(
                language_df,
                x="repository_count",
                y="language",
                orientation="h",
                title="Language Distribution",
                labels={
                    "repository_count": "Repositories",
                    "language": "Language",
                },
            )
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top Repositories")
    st.dataframe(
        _dataframe(data["top_repositories"]),
        use_container_width=True,
        hide_index=True,
    )


def _render_repository_analytics(data: dict[str, Any]) -> None:
    """Render repository analytics page."""
    st.subheader("Repository Analytics")

    left_column, right_column = st.columns(2)

    with left_column:
        language_df = _dataframe(data["language_distribution"])
        if not language_df.empty:
            fig = px.pie(
                language_df,
                names="language",
                values="repository_count",
                title="Repositories by Language",
            )
            st.plotly_chart(fig, use_container_width=True)

    with right_column:
        size_df = _dataframe(data["size_distribution"])
        if not size_df.empty:
            fig = px.bar(
                size_df,
                x="size_category",
                y="repository_count",
                title="Repository Size Categories",
                labels={
                    "size_category": "Size Category",
                    "repository_count": "Repositories",
                },
            )
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top 10 Repositories")
    st.dataframe(
        _dataframe(data["top_repositories"]),
        use_container_width=True,
        hide_index=True,
    )


def _render_repository_health(data: dict[str, Any]) -> None:
    """Render repository health page."""
    st.subheader("Repository Health Score")
    st.caption(
        "Health score is relative to repositories in the current warehouse. "
        "Very large repositories can make smaller repositories score lower."
    )

    health_df = _dataframe(data["health_distribution"])
    if not health_df.empty:
        fig = px.bar(
            health_df,
            x="health_category",
            y="repository_count",
            color="health_category",
            title="Health Score Distribution",
            labels={
                "health_category": "Health Category",
                "repository_count": "Repositories",
            },
        )
        st.plotly_chart(fig, use_container_width=True)

    left_column, right_column = st.columns(2)
    with left_column:
        st.subheader("Healthiest Repositories")
        st.dataframe(
            _dataframe(data["healthiest_repositories"]),
            use_container_width=True,
            hide_index=True,
        )

    with right_column:
        st.subheader("Needs Attention")
        st.dataframe(
            _dataframe(data["needs_attention"]),
            use_container_width=True,
            hide_index=True,
        )


def _render_data_quality(data: dict[str, Any]) -> None:
    """Render data quality report page."""
    st.subheader("Data Quality Report")
    report_text = data["quality_report"]
    parsed_report = parse_quality_report(report_text)

    if parsed_report:
        _render_kpi_cards(build_quality_summary_cards(parsed_report))

    if report_text:
        st.text(report_text)
    else:
        st.info("No data quality report found. Run `python main.py` first.")


def _render_navigation() -> str:
    """Render dashboard navigation."""
    return st.sidebar.radio(
        "Dashboard",
        (
            "Home",
            "Repository Analytics",
            "Repository Health",
            "Data Quality Report",
        ),
    )


def _page_map() -> dict[str, Callable[[dict[str, Any]], None]]:
    """Return page render functions by page name."""
    return {
        "Home": _render_home,
        "Repository Analytics": _render_repository_analytics,
        "Repository Health": _render_repository_health,
        "Data Quality Report": _render_data_quality,
    }


def main() -> None:
    """Run the Streamlit dashboard."""
    logger.info("Dashboard started")
    st.title("DataPulse")
    st.caption("GitHub Repository Intelligence Platform")

    try:
        data = _load_dashboard_data()
    except Exception as exc:  # pragma: no cover - Streamlit runtime guard
        logger.error("Dashboard data load failed: %s", exc)
        st.error("Unable to load dashboard data. Check database configuration.")
        return

    selected_page = _render_navigation()
    _page_map()[selected_page](data)


if __name__ == "__main__":
    main()
