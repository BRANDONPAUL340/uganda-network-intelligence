
import streamlit as st

from src.dashboard.monitoring import get_pipeline_summary_metrics


# ---------------------------------------------------------------------------
# PAGE CONTENT
# ---------------------------------------------------------------------------

st.html(
    """
    <style>
    .home-hero {
        position: relative;
        overflow: hidden;
        padding: 42px 40px;
        border: 1px solid rgba(93, 224, 206, 0.25);
        border-radius: 20px;
        background:
            radial-gradient(
                circle at 90% 15%,
                rgba(85, 184, 255, 0.15),
                transparent 32%
            ),
            linear-gradient(
                120deg,
                rgba(16, 42, 62, 0.98),
                rgba(8, 26, 43, 0.94)
            );
        margin-bottom: 26px;
    }

    .home-eyebrow {
        color: #5de0ce;
        font-size: 11px;
        font-weight: 750;
        letter-spacing: 2.5px;
        text-transform: uppercase;
        margin-bottom: 18px;
    }

    .home-hero h1 {
        color: #f1f7ff;
        font-size: clamp(34px, 4.5vw, 54px);
        line-height: 1.12;
        font-weight: 800;
        letter-spacing: -1.8px;
        margin: 0 0 18px 0;
    }

    .home-hero h1 span {
        color: #5de0ce;
    }

    .home-hero p {
        color: #b6c8d9;
        max-width: 760px;
        font-size: 15px;
        line-height: 1.8;
        margin-bottom: 0;
    }

    .home-section-label {
        color: #f1f7ff;
        font-size: 21px;
        font-weight: 750;
        letter-spacing: -0.4px;
        margin-top: 25px;
        margin-bottom: 5px;
    }

    .home-section-description {
        color: #9fb2c5;
        font-size: 13px;
        margin-bottom: 18px;
    }

    .home-feature {
        min-height: 165px;
        padding: 21px;
        margin-bottom: 14px;
        border: 1px solid rgba(120, 163, 190, 0.18);
        border-radius: 14px;
        background: rgba(16, 35, 54, 0.82);
        transition:
            border-color 160ms ease,
            transform 160ms ease;
    }

    .home-feature:hover {
        border-color: rgba(93, 224, 206, 0.42);
        transform: translateY(-2px);
    }

    .home-feature .feature-index {
        color: #5de0ce;
        font-size: 11px;
        font-weight: 750;
        letter-spacing: 1.5px;
        margin-bottom: 12px;
    }

    .home-feature h3 {
        color: #f1f7ff;
        font-size: 16px;
        font-weight: 700;
        margin: 0 0 9px 0;
    }

    .home-feature p {
        color: #a9bdcf;
        font-size: 13px;
        line-height: 1.65;
        margin: 0;
    }

    .home-mission {
        padding: 23px 25px;
        margin-top: 18px;
        border: 1px solid rgba(93, 224, 206, 0.2);
        border-left: 4px solid #5de0ce;
        border-radius: 12px;
        background: rgba(13, 40, 55, 0.68);
    }

    .home-mission strong {
        color: #5de0ce;
        font-size: 14px;
    }

    .home-mission p {
        color: #d1dfeb;
        font-size: 14px;
        line-height: 1.75;
        margin: 8px 0 0 0;
    }

    .home-footer {
        color: #8196aa;
        font-size: 11px;
        text-align: center;
        line-height: 1.8;
        padding: 28px 0 8px 0;
        letter-spacing: 1px;
    }

    @media (max-width: 768px) {
        .home-hero {
            padding: 28px 22px;
        }

        .home-feature {
            min-height: auto;
        }
    }
    </style>
    """,
)


# ---------------------------------------------------------------------------
# EXECUTIVE HERO
# ---------------------------------------------------------------------------

st.html(
    """
    <section class="home-hero">
        <div class="home-eyebrow">
            UGANDA / NETWORK INTELLIGENCE / DATA ENGINEERING
        </div>

        <h1>
            Understand your network.<br>
            <span>Act with intelligence.</span>
        </h1>

        <p>
            A centralized network and service intelligence platform
            bringing together pipeline monitoring, network performance,
            data quality, incident investigation and data operations.
            Turn operational data into clearer visibility and better
            decisions.
        </p>
    </section>
    """,
)


# ---------------------------------------------------------------------------
# PRIMARY WORKSPACE ACTION
# ---------------------------------------------------------------------------

st.markdown(
    '<div class="home-section-label">Operations workspace</div>',
    unsafe_allow_html=True,
)

st.html(
    """
    <div class="home-section-description">
        Start with a consolidated view of network and platform operations.
    </div>
    """,
)

if st.button(
    "Open Platform Overview",
    type="primary",
    icon=":material/arrow_forward:",
    width="stretch",
):
    st.switch_page("pages/overview.py")


# ---------------------------------------------------------------------------
# LIVE OPERATIONAL METRICS
# ---------------------------------------------------------------------------

st.markdown("---")

st.markdown(
    '<div class="home-section-label">Operational snapshot</div>',
    unsafe_allow_html=True,
)

st.html(
    """
    <div class="home-section-description">
        Pipeline and incident figures retrieved from the existing
        platform monitoring service.
    </div>
    """,
)

try:
    metrics = get_pipeline_summary_metrics()

    if metrics.get("status") == "HEALTHY":
        metric_items = [
            ("Pipeline Runs", "total_runs"),
            ("Successful Runs", "success_runs"),
            ("Failed Runs", "failed_runs"),
            ("Open Incidents", "open_incidents"),
        ]

        columns = st.columns(4)

        for column, (label, key) in zip(columns, metric_items):
            value = metrics.get(key)

            with column:
                if value is not None:
                    st.metric(label, f"{int(value):,}")
                else:
                    st.metric(label, "N/A")

    else:
        st.warning(
            "The monitoring service did not report a healthy status. "
            "Live operational figures are currently unavailable."
        )

except Exception as exc:
    st.warning(
        "The monitoring service could not provide live figures. "
        "The remaining homepage information is still available."
    )
    st.caption(f"Technical detail: {type(exc).__name__}")


# ---------------------------------------------------------------------------
# PLATFORM CAPABILITIES
# ---------------------------------------------------------------------------

st.markdown("---")

st.markdown(
    '<div class="home-section-label">Platform capabilities</div>',
    unsafe_allow_html=True,
)

st.html(
    """
    <div class="home-section-description">
        Explore the operational intelligence functions available
        across the platform.
    </div>
    """,
)

features = [
    (
        "01",
        "Pipeline Intelligence",
        "Track execution history, review pipeline outcomes "
        "and investigate failed processing runs.",
    ),
    (
        "02",
        "Network Health",
        "Monitor network availability, latency, packet loss "
        "and daily performance indicators.",
    ),
    (
        "03",
        "Data Quality",
        "Review validation results, identify problematic records "
        "and assess data reliability.",
    ),
    (
        "04",
        "Incident Management",
        "Review recorded incidents, assess severity "
        "and follow issues through resolution.",
    ),
    (
        "05",
        "Data Lineage",
        "Trace relationships between data sources, processing "
        "stages and downstream datasets.",
    ),
    (
        "06",
        "Data Operations",
        "Access the existing input interface and work "
        "with the platform's ingestion workflows.",
    ),
    (
        "07",
        "Degradation Intelligence",
        "Explore early-warning indicators and identify "
        "potential network performance deterioration.",
    ),
]

feature_columns = st.columns(3)

for index, (number, title, description) in enumerate(features):
    with feature_columns[index % 3]:
        st.html(
            f"""
            <div class="home-feature">
                <div class="feature-index">CAPABILITY {number}</div>
                <h3>{title}</h3>
                <p>{description}</p>
            </div>
            """,
        )


# ---------------------------------------------------------------------------
# PLATFORM MISSION
# ---------------------------------------------------------------------------

st.html(
    """
    <div class="home-mission">
        <strong>Platform mission</strong>
        <p>
            Empower network operations through reliable data,
            transparent processing, measurable service performance
            and actionable operational intelligence.
        </p>
    </div>
    """,
)


# ---------------------------------------------------------------------------
# FOOTER
# ---------------------------------------------------------------------------

st.html(
    """
    <div class="home-footer">
        UGANDA NETWORK & SERVICE INTELLIGENCE PLATFORM<br>
        NETWORK OPERATIONS / DATA QUALITY / PIPELINE INTELLIGENCE
    </div>
    """,
)
