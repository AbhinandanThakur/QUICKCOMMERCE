"""Quick Commerce Retention OS — internal growth analytics dashboard."""

import streamlit as st

from src.config import NAV_PAGES
from src.data_loader import datasets_available, load_datasets
from src.ui import inject_styles
from src.views import (
    ai_insights,
    delivery_trust,
    habit_funnel,
    intervention_engine,
    lifecycle_segmentation,
    retention_overview,
)

PAGE_RENDERERS = {
    "Retention Overview": retention_overview.render,
    "Lifecycle Segmentation": lifecycle_segmentation.render,
    "Habit Formation Funnel": habit_funnel.render,
    "Delivery Trust Analyzer": delivery_trust.render,
    "Intervention Engine": intervention_engine.render,
    "Growth Insight Brief": ai_insights.render,
}

st.set_page_config(
    page_title="Retention OS · Growth Analytics",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_styles()

st.sidebar.markdown("### Growth Analytics")
st.sidebar.caption("Quick Commerce · Retention OS · Internal")
page = st.sidebar.radio("Navigation", NAV_PAGES, label_visibility="collapsed")
st.sidebar.divider()
st.sidebar.markdown("**Data window**")
st.sidebar.caption("180-day synthetic cohort · 50k users")
st.sidebar.caption("Refresh: `python -m src.generate_data`")

if not datasets_available():
    st.markdown("## Quick Commerce Retention OS")
    st.warning("Datasets not found in `/data`. Generate them first:")
    st.code("python -m src.generate_data", language="bash")
    st.stop()

data = load_datasets()
PAGE_RENDERERS[page](data)
