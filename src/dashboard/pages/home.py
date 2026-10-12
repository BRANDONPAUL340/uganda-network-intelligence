import streamlit as st
from src.dashboard.monitoring import get_pipeline_summary_metrics


# ---------------------------------------------------------
# PAGE STYLING
# ---------------------------------------------------------

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(
                circle at 85% 5%,
                rgba(0, 210, 190, 0.12),
                transparent 32%
            ),
            linear-gradient(
                145deg,
                #07111f 0%,
                #0b1728 55%,
                #101d30 100%
            );
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }

    .hero {
        padding: 48px 38px;
        border: 1px solid rgba(93, 224, 206, 0.25);
        border-radius: 22px;
        background: linear-gradient(
            120deg,
            rgba(15, 39, 59, 0.97),
            rgba(8, 26, 43, 0.84)
        );
        margin-bottom: 25px;
    }

    .eyebrow {
        color: #5de0ce;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 2.5px;
        text-transform: uppercase;
    }

    .hero h1 {
        color: #f1f7ff;
        font-size: clamp(34px, 5vw, 58px);
        line-height: 1.12;
        margin: 20px 0;
    }

    .hero h1 span {
        color: #5de0ce;
    }

    .hero p {
        color: #b6c8d9;
        font-size: 16px;
        line-height: 1.8;
        max-width: 780px;
    }

    .section-heading {
        color: #f1f7ff;
        font-size: 23px;
        font-weight: 700;
        margin-top: 28px;
        margin-bottom: 5px;
    }

    .section-description {
        color: #9fb2c5;
        font-size: 14px;
        margin-bottom: 20px;
    }

    .feature-card {
        background: rgba(16, 35, 54, 0.86);
        border: 1px solid rgba(135, 172, 198, 0.18);
        border-radius: 15px;
        padding: 22px;
        min-height: 175px;
        margin-bottom: 14px;
    }

    .feature-card h3 {
        color: #5de0ce;
        font-size: 17px;
        margin-bottom: 10px;
    }

    .feature-card p {
        color: #b6c8d9;
        font-size: 14px;
        line-height: 1.7;
    }

    .mission {
        padding: 22px;
        background: rgba(13, 40, 55, 0.7);
        border-left: 4px solid #5de0ce;
        border-radius: 8px;
        color: #d7e5f2;
        line-height: 1.8;
        margin-top: 15px;
    }

    .footer-note {
        color: #8196aa;
        font-size: 12px;
        text-align: center;
        padding: 25px 0 10px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# HERO SECTION
# ---------------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">
            UGANDA | NETWORK INTELLIGENCE | DATA ENGINEERING
        </div>
        <h1>
            See your network.<br>
            <span>Understand what is happening.</span>
        </h1>
        <p>
            A centralized platform for monitoring data pipelines,
            evaluating data quality, investigating operational
            incidents, and understanding how network information
            moves through your data systems.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# PRIMARY ACTION
# ---------------------------------------------------------

st.markdown(
    '<div class="section-heading">Your operations workspace</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="section-description">
        Move from scattered operational records to a clearer,
        evidence-based view of system activity and data reliability.
    </div>
    """,
    unsafe_allow_html=True,
)

if st.button(
    "Open Operations Dashboard",
    type="primary",
    use_container_width=True,
):
    st.switch_page("pages/overview.py")


# ---------------------------------------------------------
# LIVE PLATFORM METRICS
# ---------------------------------------------------------

st.markdown("---")

st.markdown(
    '<div class="section-heading">Platform at a glance</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="section-description">
        Live operational figures from the existing monitoring layer.
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    metrics = get_pipeline_summary_metrics()

    if metrics.get("status") == "HEALTHY":
        metric_columns = st.columns(4)

        metric_items = [
            ("Pipeline Runs", "total_runs"),
            ("Successful Runs", "success_runs"),
            ("Failed Runs", "failed_runs"),
            ("Open Incidents", "open_incidents"),
        ]

        for column, (label, key) in zip(
            metric_columns, metric_items
        ):
            with column:
                value = metrics.get(key)

                if value is not None:
                    st.metric(label, f"{int(value):,}")
                else:
                    st.metric(label, "N/A")

    else:
        st.warning(
            "The monitoring service did not report a healthy status. "
            "Live figures are unavailable."
        )

except Exception as exc:
    st.warning(
        "Live metrics could not be loaded. "
        "Other homepage information remains available."
    )
    st.caption(f"Monitoring detail: {type(exc).__name__}")


# ---------------------------------------------------------
# PLATFORM CAPABILITIES
# ---------------------------------------------------------

st.markdown("---")

st.markdown(
    '<div class="section-heading">One platform. Multiple perspectives.</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="section-description">
        Explore the capabilities already available in the platform.
    </div>
    """,
    unsafe_allow_html=True,
)

features = [
    (
        "Pipeline Intelligence",
        "Track pipeline executions, review processing history, "
        "and investigate failed runs.",
    ),
    (
        "Data Quality",
        "Review validation outcomes, identify problematic records, "
        "and examine data-quality trends.",
    ),
    (
        "Incident Management",
        "Review recorded incidents, understand severity, "
        "and follow issues through resolution.",
    ),
    (
        "Data Lineage",
        "Understand relationships between data sources, "
        "processing steps, and downstream records.",
    ),
    (
        "Event Processing",
        "Explore available event records and investigate "
        "processing activity and outcomes.",
    ),
    (
        "Data Operations",
        "Use the existing input interface to submit information "
        "through the platform's ingestion workflows.",
    ),
]

feature_columns = st.columns(3)

for index, (title, description) in enumerate(features):
    with feature_columns[index % 3]:
        st.markdown(
            f"""
            <div class="feature-card">
                <h3>{title}</h3>
                <p>{description}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------
# PROJECT PURPOSE
# ---------------------------------------------------------

st.markdown(
    """
    <div class="mission">
        <strong>Our mission</strong><br>
        Help network operators identify operational problems,
        monitor data reliability, and make better-informed
        decisions using centralized network data intelligence.
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.markdown(
    """
    <div class="footer-note">
        UGANDA NETWORK INTELLIGENCE PLATFORM<br>
        NETWORK OPERATIONS | DATA QUALITY | PIPELINE MONITORING
    </div>
    """,
    unsafe_allow_html=True,
)