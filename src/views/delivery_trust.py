import pandas as pd
import plotly.express as px
import streamlit as st

from src.insights import delivery_insights, pm_recommendations
from src.metrics import compute_kpi_bundle, delay_impact_on_reorder
from src.ui import apply_chart_style, insight_row, metric_row, page_header, recommendation_card
from src.utils import delivery_trust_metrics


def render(data: dict) -> None:
    users, orders = data["users"], data["orders"]
    kpis = compute_kpi_bundle(data)
    metrics = delivery_trust_metrics(orders)
    delay_impact = delay_impact_on_reorder(orders)

    page_header(
        "Delivery Trust Analyzer",
        "SLA performance, slippage, and the retention cost of delayed deliveries.",
    )

    metric_row(
        [
            ("Delivery trust score", f"{kpis['delivery_trust_score']:.0f}/100", "Weighted on-time, delay rate, and slippage."),
            ("Delayed order rate", f"{metrics['delay_rate']:.1%}", "Share of orders arriving past promise."),
            ("Avg slippage", f"{metrics['avg_slippage_min']:.1f} min", "Mean minutes over promised ETA."),
            ("Repeat after delayed 1st", f"{delay_impact['repeat_after_delayed_first']:.1%}", "Users with 2+ orders when first trip was delayed."),
        ]
    )

    st.markdown("##### Product insights")
    insight_row(delivery_insights(kpis))

    orders = orders.copy()
    orders["slippage_min"] = orders["actual_delivery_min"] - orders["promised_delivery_min"]
    merged = orders.merge(users[["user_id", "segment", "churn_risk_score"]], on="user_id")

    col1, col2 = st.columns(2)
    with col1:
        fig = px.histogram(
            merged,
            x="slippage_min",
            color="delayed",
            nbins=36,
            labels={"slippage_min": "Minutes over promise", "delayed": "Flagged delayed"},
        )
        apply_chart_style(fig, "Delivery slippage distribution", x_title="Minutes over promise", y_title="Orders")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        impact_df = pd.DataFrame(
            {
                "first_delivery": ["Delayed first", "On-time first"],
                "repeat_rate": [
                    delay_impact["repeat_after_delayed_first"],
                    delay_impact["repeat_after_on_time_first"],
                ],
            }
        )
        fig_imp = px.bar(impact_df, x="first_delivery", y="repeat_rate", text=impact_df["repeat_rate"].map("{:.1%}".format))
        apply_chart_style(fig_imp, "Reorder probability after first delivery", y_title="Share reaching 2nd order")
        fig_imp.update_yaxes(tickformat=".0%")
        fig_imp.update_traces(textposition="outside")
        st.plotly_chart(fig_imp, use_container_width=True)

    by_segment = (
        merged.groupby("segment", observed=True)
        .agg(delay_rate=("delayed", "mean"), avg_slippage=("slippage_min", "mean"))
        .reset_index()
    )
    fig2 = px.bar(by_segment, x="segment", y="delay_rate", labels={"delay_rate": "Delay rate"})
    apply_chart_style(fig2, "Delay rate by behavioral segment", y_title="Delayed order share")
    fig2.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig2, use_container_width=True)

    for rec in pm_recommendations(kpis):
        if "deliver" in rec["title"].lower() or "deliver" in rec["body"].lower():
            recommendation_card(rec["title"], rec["body"], rec["action"], rec["priority"])
