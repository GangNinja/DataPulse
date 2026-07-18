"""Streamlit dashboard for DataPulse analytics."""

from collections.abc import Callable
from html import escape
import os
from pathlib import Path
import sys
from typing import Any

from dotenv import load_dotenv
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
load_dotenv()

PAGE_OPTIONS = (
    "Home",
    "Repository Analytics",
    "Repository Health",
    "Data Quality Report",
)

HEALTH_COLORS = {
    "Excellent": "#16a34a",
    "Very Good": "#0d9488",
    "Good": "#2563eb",
    "Average": "#f59e0b",
    "Needs Attention": "#dc2626",
}

ACCENT_COLORS = [
    "#2563eb",
    "#16a34a",
    "#f59e0b",
    "#dc2626",
    "#7c3aed",
    "#0891b2",
    "#be123c",
    "#4d7c0f",
]

REPOSITORY_COLUMNS = {
    "owner": "Owner",
    "repo_name": "Repository",
    "html_url": "GitHub",
    "stars": "Stars",
    "forks": "Forks",
    "watchers": "Watchers",
    "open_issues": "Open Issues",
    "language": "Language",
    "updated_at": "Updated At",
    "health_score": "Health Score",
    "health_category": "Category",
}


st.set_page_config(
    page_title="DataPulse Dashboard",
    page_icon="DP",
    layout="wide",
)


def _apply_dashboard_theme() -> None:
    """Apply lightweight dashboard styling."""
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1440px;
        }
        section[data-testid="stSidebar"] {
            border-right: 1px solid rgba(148, 163, 184, 0.22);
        }
        div[data-testid="stMetric"] {
            background: linear-gradient(
                135deg,
                rgba(37, 99, 235, 0.12),
                rgba(22, 163, 74, 0.08)
            );
            border: 1px solid rgba(148, 163, 184, 0.24);
            border-radius: 8px;
            padding: 1rem 1.05rem;
            min-height: 104px;
        }
        div[data-testid="stMetric"] label {
            color: rgba(148, 163, 184, 0.95);
            font-size: 0.82rem;
        }
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            font-weight: 750;
            letter-spacing: 0;
        }
        .dp-header {
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            align-items: flex-end;
            border-bottom: 1px solid rgba(148, 163, 184, 0.24);
            padding-bottom: 1.15rem;
            margin-bottom: 1.2rem;
        }
        .dp-eyebrow {
            color: #0d9488;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0;
            margin-bottom: 0.2rem;
            text-transform: uppercase;
        }
        .dp-title {
            font-size: 2.35rem;
            line-height: 1.1;
            font-weight: 800;
            margin: 0;
        }
        .dp-subtitle {
            color: rgba(148, 163, 184, 0.95);
            margin: 0.55rem 0 0 0;
            font-size: 1rem;
        }
        .dp-status {
            border: 1px solid rgba(22, 163, 74, 0.28);
            border-radius: 999px;
            color: #16a34a;
            font-size: 0.78rem;
            font-weight: 700;
            padding: 0.35rem 0.75rem;
            white-space: nowrap;
        }
        .dp-section {
            margin-top: 1.25rem;
            margin-bottom: 0.6rem;
        }
        .dp-section h2 {
            font-size: 1.15rem;
            font-weight: 750;
            margin: 0;
            letter-spacing: 0;
        }
        .dp-section p {
            color: rgba(148, 163, 184, 0.95);
            margin: 0.25rem 0 0 0;
            font-size: 0.9rem;
        }
        .dp-callout {
            border-left: 4px solid #f59e0b;
            background: rgba(245, 158, 11, 0.10);
            border-radius: 8px;
            padding: 0.75rem 0.9rem;
            margin: 0.3rem 0 1rem 0;
            color: inherit;
        }
        .dp-report {
            border: 1px solid rgba(148, 163, 184, 0.24);
            border-radius: 8px;
            padding: 1rem;
            background: rgba(15, 23, 42, 0.05);
            white-space: pre-wrap;
            font-family: Consolas, monospace;
            font-size: 0.9rem;
            line-height: 1.55;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource
def _get_engine() -> Any:
    """Create and cache the dashboard database engine."""
    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url:
        database_url = get_settings().database_url

    return create_dashboard_engine(database_url)


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


def _render_header() -> None:
    """Render dashboard header."""
    st.markdown(
        """
        <div class="dp-header">
            <div>
                <div class="dp-eyebrow">GitHub Repository Intelligence</div>
                <h1 class="dp-title">DataPulse Dashboard</h1>
                <p class="dp-subtitle">
                    Repository analytics, health scoring, and data quality.
                </p>
            </div>
            <div class="dp-status">Warehouse Connected</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_section(title: str, subtitle: str | None = None) -> None:
    """Render a dashboard section heading."""
    subtitle_markup = ""
    if subtitle:
        subtitle_markup = f"<p>{escape(subtitle)}</p>"

    st.markdown(
        f"""
        <div class="dp-section">
            <h2>{escape(title)}</h2>
            {subtitle_markup}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_kpi_cards(cards: list[dict[str, str]]) -> None:
    """Render KPI cards using Streamlit metric components."""
    columns = st.columns(len(cards))
    for column, card in zip(columns, cards, strict=True):
        with column:
            st.metric(card["label"], card["value"])


def _style_figure(fig: Any, height: int = 360) -> Any:
    """Apply consistent chart styling."""
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin={"l": 12, "r": 12, "t": 58, "b": 24},
        font={"family": "Arial", "size": 12},
        title={"font": {"size": 17}, "x": 0.02, "xanchor": "left"},
        legend={"orientation": "h", "y": -0.18},
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0)",
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(148, 163, 184, 0.18)")
    fig.update_yaxes(showgrid=False)
    return fig


def _render_empty_state(message: str) -> None:
    """Render a small empty state."""
    st.info(message)


def _repository_dataframe(rows: list[dict[str, Any]]) -> pd.DataFrame:
    """Prepare repository rows for dashboard tables."""
    dataframe = _dataframe(rows)
    if dataframe.empty:
        return dataframe

    ordered_columns = [
        column for column in REPOSITORY_COLUMNS if column in dataframe.columns
    ]
    dataframe = dataframe[ordered_columns].rename(columns=REPOSITORY_COLUMNS)

    if "Updated At" in dataframe.columns:
        dataframe["Updated At"] = pd.to_datetime(
            dataframe["Updated At"],
            errors="coerce",
        ).dt.strftime("%Y-%m-%d")

    if "Health Score" in dataframe.columns:
        dataframe["Health Score"] = pd.to_numeric(
            dataframe["Health Score"],
            errors="coerce",
        ).fillna(0)

    return dataframe


def _render_repository_table(
    rows: list[dict[str, Any]],
    empty_message: str,
) -> None:
    """Render a formatted repository table."""
    dataframe = _repository_dataframe(rows)
    if dataframe.empty:
        _render_empty_state(empty_message)
        return

    column_config: dict[str, Any] = {}
    if "GitHub" in dataframe.columns:
        column_config["GitHub"] = st.column_config.LinkColumn(
            "GitHub",
            display_text="Open",
        )
    if "Health Score" in dataframe.columns:
        column_config["Health Score"] = st.column_config.ProgressColumn(
            "Health Score",
            min_value=0,
            max_value=100,
            format="%.2f",
        )

    st.dataframe(
        dataframe,
        use_container_width=True,
        hide_index=True,
        column_config=column_config,
    )


def _quality_score_as_float(value: str | None) -> float:
    """Parse quality score text into a float."""
    if not value:
        return 0.0

    return float(value.replace("%", "").strip())


def _render_home(data: dict[str, Any]) -> None:
    """Render dashboard homepage."""
    _render_section(
        "Overview",
        "A quick read on repository volume, engagement, and health.",
    )
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
                color_discrete_map=HEALTH_COLORS,
                title="Repository Health Distribution",
                labels={
                    "health_category": "Health Category",
                    "repository_count": "Repositories",
                },
            )
            st.plotly_chart(_style_figure(fig), use_container_width=True)
        else:
            _render_empty_state("No health score data is available yet.")

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
                color="language",
                color_discrete_sequence=ACCENT_COLORS,
            )
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(_style_figure(fig), use_container_width=True)
        else:
            _render_empty_state("No language distribution data is available yet.")

    _render_section(
        "Top Repositories",
        "Ranked by stars, with health score and repository activity context.",
    )
    _render_repository_table(
        data["top_repositories"],
        "No repository records are available yet.",
    )


def _render_repository_analytics(data: dict[str, Any]) -> None:
    """Render repository analytics page."""
    _render_section(
        "Repository Analytics",
        "Compare language mix, repository size, and leading repositories.",
    )

    left_column, right_column = st.columns(2)

    with left_column:
        language_df = _dataframe(data["language_distribution"])
        if not language_df.empty:
            fig = px.pie(
                language_df,
                names="language",
                values="repository_count",
                title="Repositories by Language",
                hole=0.48,
                color_discrete_sequence=ACCENT_COLORS,
            )
            fig.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(_style_figure(fig), use_container_width=True)
        else:
            _render_empty_state("No language data is available yet.")

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
                color="size_category",
                color_discrete_sequence=["#16a34a", "#f59e0b", "#dc2626"],
            )
            st.plotly_chart(_style_figure(fig), use_container_width=True)
        else:
            _render_empty_state("No repository size data is available yet.")

    top_df = _repository_dataframe(data["top_repositories"])
    if not top_df.empty:
        chart_df = top_df.head(10).sort_values("Stars", ascending=True)
        fig = px.bar(
            chart_df,
            x="Stars",
            y="Repository",
            orientation="h",
            color="Language",
            title="Top 10 Repositories by Stars",
            color_discrete_sequence=ACCENT_COLORS,
        )
        st.plotly_chart(_style_figure(fig, height=420), use_container_width=True)

    _render_section("Repository Leaderboard")
    _render_repository_table(
        data["top_repositories"],
        "No top repository records are available yet.",
    )


def _render_repository_health(data: dict[str, Any]) -> None:
    """Render repository health page."""
    _render_section(
        "Repository Health",
        "Weighted score using stars, forks, watchers, and update activity.",
    )
    st.markdown(
        """
        <div class="dp-callout">
            Health score is relative to the current warehouse. Very large
            repositories can make smaller repositories score lower.
        </div>
        """,
        unsafe_allow_html=True,
    )

    health_df = _dataframe(data["health_distribution"])
    if not health_df.empty:
        fig = px.bar(
            health_df,
            x="health_category",
            y="repository_count",
            color="health_category",
            color_discrete_map=HEALTH_COLORS,
            title="Health Score Distribution",
            labels={
                "health_category": "Health Category",
                "repository_count": "Repositories",
            },
        )
        st.plotly_chart(_style_figure(fig), use_container_width=True)
    else:
        _render_empty_state("No repository health data is available yet.")

    left_column, right_column = st.columns(2)
    with left_column:
        _render_section("Healthiest Repositories")
        _render_repository_table(
            data["healthiest_repositories"],
            "No health score records are available yet.",
        )

    with right_column:
        _render_section("Needs Attention")
        _render_repository_table(
            data["needs_attention"],
            "No repositories currently need attention.",
        )


def _render_data_quality(data: dict[str, Any]) -> None:
    """Render data quality report page."""
    _render_section(
        "Data Quality Report",
        "Latest validation, cleaning, duplicate removal, and rejection summary.",
    )
    report_text = data["quality_report"]
    parsed_report = parse_quality_report(report_text)

    if parsed_report:
        _render_kpi_cards(build_quality_summary_cards(parsed_report))
        quality_score = _quality_score_as_float(parsed_report.get("quality_score"))
        st.progress(min(quality_score / 100, 1.0))

    if report_text:
        st.markdown(
            f'<div class="dp-report">{escape(report_text)}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.info("No data quality report found. Run `python main.py` first.")


def _render_navigation() -> str:
    """Render dashboard navigation."""
    st.sidebar.title("DataPulse")
    st.sidebar.caption("Repository Intelligence")
    return st.sidebar.radio(
        "Dashboard",
        PAGE_OPTIONS,
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
    _apply_dashboard_theme()
    _render_header()

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
