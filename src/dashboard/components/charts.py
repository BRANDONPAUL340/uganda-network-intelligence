
"""Shared chart styling for the Uganda Network Intelligence Platform."""

import streamlit as st

CHART_COLORS = {
    "primary": "#5DE0CE",    # Teal
    "secondary": "#55B8FF",  # Cyan-blue
    "success": "#5DE0CE",    # Healthy / successful
    "failure": "#FF6B7A",    # Failed / critical
    "warning": "#FFC766",    # Warnings
    "neutral": "#B6C8D9",    # Supporting information
}

CHART_PANEL_CSS = """
<style>
div[data-testid="stVegaLiteChart"],
div[data-testid="stArrowVegaLiteChart"],
div[data-testid="stLineChart"],
div[data-testid="stBarChart"] {
    background: rgba(16, 35, 54, 0.72);
    border: 1px solid rgba(93, 224, 206, 0.18);
    border-radius: 14px;
    padding: 10px;
    margin-top: 8px;
    margin-bottom: 16px;
}
</style>
"""


def apply_chart_theme():
    """Apply the shared dark chart-panel styling."""
    st.markdown(CHART_PANEL_CSS, unsafe_allow_html=True)


def render_line_chart(data, *, color=None, height=320):
    """Render a consistently styled native Streamlit line chart."""
    if data is None or data.empty:
        st.info("No chart data is available for this period.")
        return

    if color is None:
        color = CHART_COLORS["primary"]

    st.line_chart(
        data,
        color=color,
        height=height,
        use_container_width=True,
    )


def render_bar_chart(data, *, color=None, height=320):
    """Render a consistently styled native Streamlit bar chart."""
    if data is None or data.empty:
        st.info("No chart data is available for this period.")
        return

    if color is None:
        color = CHART_COLORS["secondary"]

    st.bar_chart(
        data,
        color=color,
        height=height,
        use_container_width=True,
    )
