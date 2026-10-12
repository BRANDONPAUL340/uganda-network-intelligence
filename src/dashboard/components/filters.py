"""
Uganda Network Intelligence Platform — Shared Dashboard Filters Component
Enforces consistent drop-down widget styles and simplifies selection routing [INDEX].
"""
import streamlit as st
import pandas as pd

def render_dropdown_filter(label: str, options: list, key: str) -> str:
    """
    7 & 8. Shared Widget: Standardises the creation of selectbox selectors 
    by automatically appending the 'All' fallback wild-card choice [INDEX].
    """
    full_options = ["All"] + [str(opt) for opt in options if pd.notna(opt)]
    return st.selectbox(
        label=label,
        options=full_options,
        index=0,
        key=key
    )
