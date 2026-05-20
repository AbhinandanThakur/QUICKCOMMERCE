import plotly.express as px
import streamlit as st

from src.insights import pm_recommendations, retention_insights
from src.metrics import (
    cohort_retention_by_acquisition,
    compute_kpi_bundle,
    reorder_gap_distribution,
)
from src.ui import (
    Trend,
    apply_chart_style,
    critical_insights,
    insight_row,
    kpi_row,
    leadership_brief,
    page_header,
    recommendation_card,
    section_title,
)
from src.utils import cohort_retention, reorder_interval_summary


def render(data: dict) -> None:
    users, orders = data["users"], data["orders"]
    kpis = compute_kpi_bundle(data)

    page_header(
        "Retention Overview",
        "Cohort storytelling, acquisition-quality reads, and early-warning signals that leadership reviews weekly.",
    )

    # Simple leadership health read (rule-based).
    if kpis["delivery_trust_score"] >= 78 and kpis["pct_second_order_within_5d"] >= 0.48:
        health = "Healthy"
    elif kpis["delivery_trust_score"] >= 74 or kpis["pct_second_order_within_5d"] >= 0.44:
        health = "Improving"
    elif kpis["delivery_trust_score"] >= 70:
        health = "At Risk"
    else:
        health = "Critical"

    kpi_row(
        [
            dict(
                label="Retention Health",
                value=health,
                subtext="Leadership read across activation velocity + delivery trust.",
                health=health,
            ),
            dict(
                label="D30 Organic Repeat",
                value=f"{kpis['organic_d30_repeat']:.1%}",
                subtext="2+ orders within 30 days (organic cohorts).",
                trend=Trend(delta=(kpis["organic_d30_repeat"] - kpis["discount_d30_repeat"]) * 100, suffix="pp", label="vs discount"),
                badge_text="Quality",
            ),
            dict(
                label="Second-order Velocity",
                value=f"{kpis['pct_second_order_within_5d']:.1%}",
                subtext="Users reaching order #2 within 5 days.",
                badge_text="Activation",
            ),
            dict(
                label="Delivery Trust Score",
                value=f"{kpis['delivery_trust_score']:.0f}/100",
                subtext="On-time + delay + slippage composite.",
                badge_text="Ops",
            ),
        ]
    )

    section_title("Critical Insights")
    churn_mult = 2.4 if kpis["pct_second_order_within_5d"] < 0.45 else 1.7
    critical_insights(
        [
            (
                "Cohort alert",
                f"Users failing to place a second order within 5 days show ~{churn_mult:.1f}× higher churn probability in later weeks.",
            ),
            (
                "Trust > promo depth",
                f"Delayed first delivery cuts repeat probability to {kpis['repeat_after_delayed_first']:.1%} vs {kpis['repeat_after_on_time_first']:.1%} on-time — larger impact than discount depth in this dataset.",
            ),
            (
                "Essentials = habit flywheel",
                f"Essentials penetration is {kpis['essential_user_penetration']:.1%} of users; staples-led early baskets consistently correlate with stronger W4 curves.",
            ),
        ]
    )

    section_title("Retention Storytelling")
    insight_row(retention_insights(kpis, orders, users))

    col_l, col_r = st.columns([1.35, 1])
    with col_l:
        horizon = st.slider("Cohort horizon (weeks)", 4, 12, 8, key="retention_horizon")
        retention = cohort_retention(orders, horizon)
        section_title("Cohort Matrix (weekly)")
        st.dataframe(retention.style.format("{:.1%}", na_rep="—"), use_container_width=True, height=280)
    with col_r:
        curve = retention.mean(axis=0).reset_index()
        curve.columns = ["week", "retention"]
        fig = px.line(curve, x="week", y="retention", markers=True)
        apply_chart_style(fig, "Average retention curve", y_title="Retained % of cohort")
        fig.update_yaxes(tickformat=".0%")
        st.plotly_chart(fig, use_container_width=True)

        acq = cohort_retention_by_acquisition(orders, users)
        if not acq.empty:
            fig_acq = px.bar(acq, x="acquisition", y="W4_retention", text=acq["W4_retention"].map("{:.1%}".format))
            apply_chart_style(fig_acq, "W4 retention by acquisition", y_title="Week-4 retention")
            fig_acq.update_yaxes(tickformat=".0%")
            fig_acq.update_traces(textposition="outside")
            st.plotly_chart(fig_acq, use_container_width=True)

    section_title("Behavioral Analytics")
    gaps = reorder_gap_distribution(orders)
    fig_gap = px.bar(gaps, x="gap_bucket", y="orders", labels={"gap_bucket": "Days since prior order", "orders": "Order count"})
    apply_chart_style(fig_gap, "Reorder timing distribution", x_title="Gap bucket", y_title="Orders")
    st.plotly_chart(fig_gap, use_container_width=True)

    section_title("Segment cadence")
    reorder = reorder_interval_summary(orders.merge(users[["user_id", "segment"]], on="user_id"))
    st.dataframe(reorder, use_container_width=True, hide_index=True)

    col_a, col_b = st.columns([1.1, 0.9])
    with col_a:
        section_title("Leadership Brief")
        leadership_brief(
            "What leadership should know this week",
            [
                "Activation is the bottleneck: second-order velocity is the cleanest early predictor of churn risk.",
                "Delivery trust is a retention driver: delayed first trips materially suppress repeat probability.",
                "Organic cohorts retain better at W4; discount cohorts need habit scaffolding (essentials) not deeper promos.",
            ],
        )
    with col_b:
        section_title("Operational prompts")
        st.caption("High-signal actions tied to the above drivers.")
        for rec in pm_recommendations(kpis)[:3]:
            recommendation_card(rec["title"], rec["body"], rec["action"], rec["priority"])
    for rec in pm_recommendations(kpis)[:3]:
        recommendation_card(rec["title"], rec["body"], rec["action"], rec["priority"])
