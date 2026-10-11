"""
Uganda Network Intelligence Platform — Shared Metric Component
Standardises horizontal summary metrics and alert delta status displays [INDEX].
"""
import streamlit as st

def render_metric_card_grid(cards_data: list):
    """
    10. Shared Metric Component: Accepts a list of profile dictionaries 
    and maps them cleanly into a multi-column horizontal layout grid [INDEX].
    Allows changing styling tokens globally in a single place.
    """
    if not cards_data:
        return
        
    # Dynamically generate equal-width presentation columns
    cols = st.columns(len(cards_data))
    
    for i, card in enumerate(cards_data):
        with cols[i]:
            st.metric(
                label=card.get("label", ""),
                value=card.get("value", "0"),
                delta=card.get("delta", None),
                delta_color=card.get("delta_color", "normal")
            )
