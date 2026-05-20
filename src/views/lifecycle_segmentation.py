import plotly.express as px
import streamlit as st

from src.insights import lifecycle_insights, pm_recommendations
from src.metrics import compute_kpi_bundle, latest_user_snapshot, pm_lifecycle_distribution
from src.ui import PM_LIFECYCLE_COLORS, apply_chart_style, insight_row, metric_row, page_header, recommendation_card


def render(data: dict) -> None:
    users, orders, lifecycle = data["users"], data["orders"], data["lifecycle_stages"]
    kpis = compute_kpi_bundle(data)
    snap = latest_user_snapshot(users, lifecycle)
    dist = pm_lifecycle_distribution(users, lifecycle)

    page_header(
        "Lifecycle Segmentation",
        "PM lifecycle view: active, habitual, at-risk, churn-risk, and dormant populations.",
    )

    counts = snap["pm_lifecycle"].value_counts()
    metric_row(
        [
            ("Active", f"{counts.get('active', 0):,}", "New/activated users still in play."),
            ("Habitual", f"{counts.get('habitual', 0):,}", "Staples-led repeat rhythm established."),
            ("At-risk", f"{counts.get('at-risk', 0):,}", "Gap widening; intervention window open."),
            ("Churn-risk", f"{counts.get('churn-risk', 0):,}", "Behavioral score + weak engagement pattern."),
        ],
        columns=4,
    )
    c1, c2 = st.columns(2)
    with c1:
        metric_row([("Dormant", f"{counts.get('dormant', 0):,}", "No meaningful activity 35+ days post last order.")], columns=1)
    with c2:
        metric_row(
            [("D30 organic vs discount", f"{kpis['organic_d30_repeat']:.1%} / {kpis['discount_d30_repeat']:.1%}", "Repeat within 30 days.")],
            columns=1,
        )

    st.markdown("##### Product insights")
    insight_row(lifecycle_insights(kpis, users, lifecycle))

    col_a, col_b = st.columns(2)
    with col_a:
        fig = px.bar(
            dist,
            x="pm_lifecycle",
            y="share",
            color="pm_lifecycle",
            color_discrete_map=PM_LIFECYCLE_COLORS,
        )
        apply_chart_style(fig, "Current lifecycle mix", y_title="Share of users")
        fig.update_yaxes(tickformat=".0%")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        merged = snap.assign(
            acquisition=snap["discount_acquired"].map({True: "Discount", False: "Organic"})
        )
        cross = merged.groupby(["pm_lifecycle", "acquisition"], observed=True).size().reset_index(name="users")
        fig2 = px.bar(cross, x="pm_lifecycle", y="users", color="acquisition", barmode="group")
        apply_chart_style(fig2, "Lifecycle × acquisition type", y_title="Users")
        st.plotly_chart(fig2, use_container_width=True)

    stage_segment = (
        snap.groupby(["pm_lifecycle", "segment"], observed=True)
        .size()
        .reset_index(name="users")
    )
    fig3 = px.sunburst(stage_segment, path=["pm_lifecycle", "segment"], values="users", color="pm_lifecycle", color_discrete_map=PM_LIFECYCLE_COLORS)
    apply_chart_style(fig3, "Lifecycle × behavioral segment")
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("##### PM recommendations")
    for rec in pm_recommendations(kpis):
        if "organic" in rec["body"].lower() or "second order" in rec["body"].lower():
            recommendation_card(rec["title"], rec["body"], rec["action"], rec["priority"])
