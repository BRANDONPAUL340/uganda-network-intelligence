
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

# Initialize and validate environment configuration first.
import src.config

# Import database-dependent modules only after configuration is ready.
from src.dashboard.monitoring import get_pipeline_summary_metrics
# ---------------------------------------------------------------------------
# Global Page Configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Uganda Network Intelligence Platform",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# Global Enterprise Theme — shared across every dashboard page
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    :root {
        --uni-bg: #081321;
        --uni-panel: #102336;
        --uni-panel-soft: rgba(16, 35, 54, 0.86);
        --uni-teal: #5de0ce;
        --uni-text: #f1f7ff;
        --uni-muted: #b6c8d9;
        --uni-border: rgba(93, 224, 206, 0.18);
    }

    /* Application background and typography */
    .stApp {
        background:
            radial-gradient(
                ellipse at 85% 0%,
                rgba(26, 104, 119, 0.16),
                transparent 38%
            ),
            linear-gradient(
                145deg,
                #081321 0%,
                #0a1727 55%,
                #0b1d2b 100%
            );
        color: var(--uni-text);
    }

    [data-testid="stHeader"] {
        background: rgba(8, 19, 33, 0.88);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #0b1b2b 0%,
            #081321 100%
        );
        border-right: 1px solid var(--uni-border);
    }

    [data-testid="stSidebar"] > div:first-child {
        background: transparent;
    }

    /* Consistent page headings */
    h1, h2, h3, h4 {
        color: var(--uni-text) !important;
        letter-spacing: -0.025em;
    }

    h1 {
        font-weight: 750 !important;
    }

    p, label, .stCaption, [data-testid="stMarkdownContainer"] {
        color: var(--uni-muted);
    }

    /* Enterprise panels and metric cards */
    [data-testid="stMetric"] {
        background: var(--uni-panel-soft);
        border: 1px solid var(--uni-border);
        border-radius: 14px;
        padding: 18px 20px;
        min-height: 112px;
    }

    [data-testid="stMetricLabel"] {
        color: var(--uni-muted) !important;
    }

    [data-testid="stMetricValue"] {
        color: var(--uni-teal) !important;
        font-weight: 750;
    }

    [data-testid="stMetricDelta"] {
        font-size: 0.82rem;
    }

    /* Buttons */
    .stButton > button,
    .stDownloadButton > button,
    [data-testid="stFormSubmitButton"] > button {
        border: 1px solid rgba(93, 224, 206, 0.42);
        border-radius: 9px;
        background: linear-gradient(
            135deg,
            rgba(24, 92, 104, 0.95),
            rgba(16, 53, 72, 0.95)
        );
        color: #f1f7ff;
        font-weight: 650;
        transition: border-color 160ms ease, transform 160ms ease;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover,
    [data-testid="stFormSubmitButton"] > button:hover {
        border-color: var(--uni-teal);
        color: #ffffff;
        transform: translateY(-1px);
    }

    /* Inputs and selectors */
    input, textarea,
    [data-baseweb="select"] > div,
    [data-baseweb="input"] > div {
        border-radius: 8px !important;
    }

    /* Data tables */
    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        border: 1px solid var(--uni-border);
        border-radius: 12px;
        overflow: hidden;
    }

    /* Tabs */
    button[data-baseweb="tab"] {
        color: var(--uni-muted);
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: var(--uni-teal);
        border-bottom-color: var(--uni-teal);
    }

    /* Expanders and forms */
    [data-testid="stExpander"],
    [data-testid="stForm"] {
        border: 1px solid var(--uni-border);
        border-radius: 12px;
        background: rgba(16, 35, 54, 0.42);
    }

    /* Alerts */
    [data-testid="stAlert"] {
        border-radius: 10px;
    }

    /* Dividers and links */
    hr {
        border-color: var(--uni-border);
    }

    a {
        color: var(--uni-teal) !important;
    }

    /* Keep the design usable on smaller screens */
    @media (max-width: 768px) {
        [data-testid="stMetric"] {
            padding: 12px;
            min-height: 95px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)



# ---------------------------------------------------------------------------
# Sidebar Branding
# ---------------------------------------------------------------------------

st.sidebar.title("🌍 UGANDA NETWORK")
st.sidebar.subheader("INTELLIGENCE")
st.sidebar.markdown("---")


# ---------------------------------------------------------------------------
# Database Health Check
# ---------------------------------------------------------------------------

try:
    health = get_pipeline_summary_metrics()
    db_connected = health.get("status") == "HEALTHY"

except Exception:
    db_connected = False


# ---------------------------------------------------------------------------
# Multi-Page Navigation
# ---------------------------------------------------------------------------
#
# The Input Data page is the final operational ingestion interface.
#
# Event Store Worker Monitoring remains intentionally excluded because its
# underlying persistence model is not part of the authoritative schema.
#
# Lineage remains active because pipeline_lineage is present and verified.
# ---------------------------------------------------------------------------

pages = {
    "Dashboard & Home": [
    st.Page(
        "pages/home.py",
        title="Home",
        icon=":material/home:",
        default=True,
    ),
    st.Page(
        "pages/overview.py",
        title="Platform Overview",
        icon=":material/dashboard:",
    ),
        st.Page(
            "pages/pipeline_runs.py",
            title="Pipeline Execution Logs",
            icon="🔄",
        ),
    ],

    "📡 Telemetry & Metrics": [
        st.Page(
            "pages/data_quality.py",
            title="Data Quality Engine",
            icon="✅",
        ),
        st.Page(
            "pages/incidents.py",
            title="Incident Management Panel",
            icon="🚨",
        ),

        st.Page(
            "pages/network_health.py",
            title="Network Health Intelligence",
            icon=":material/monitor_heart:",
        ),

        st.Page(
             "pages/degradation_early_warning.py",
              title="Degradation Early Warning",
              icon=":material/trending_up:",
      ),
    ],

    "🧭 Data Lineage": [
        st.Page(
            "pages/lineage.py",
            title="Data Lineage Map",
            icon="🧭",
        ),

        
    ],

    "📝 Data Operations": [
        st.Page(
            "pages/input_data.py",
            title="Input Data",
            icon="📝",
        ),
    ],
}


# ---------------------------------------------------------------------------
# Navigation Router
# ---------------------------------------------------------------------------

navigation_router = st.navigation(pages)


# ---------------------------------------------------------------------------
# Sidebar Infrastructure Status
# ---------------------------------------------------------------------------

st.sidebar.markdown("---")
st.sidebar.markdown("### 🖥️ System Infrastructure")

if db_connected:
    st.sidebar.success("🟢 PostgreSQL 18: Connected")
else:
    st.sidebar.error("🔴 PostgreSQL 18: Disconnected")

st.sidebar.caption("Workstation Node Location: Kampala, Uganda")


# ---------------------------------------------------------------------------
# Execute Selected Page
# ---------------------------------------------------------------------------

navigation_router.run()