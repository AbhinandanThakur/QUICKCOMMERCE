import plotly.express as px
import streamlit as st

from src.insights import intervention_insights, pm_recommendations
from src.metrics import compute_kpi_bundle, latest_user_snapshot
from src.ui import apply_chart_style, insight_row, metric_row, page_header, recommendation_card
from src.utils import notification_funnel


def render(data: dict) -> None:
    users = data["users"]
    notifications = data["notifications"]
    lifecycle = data["lifecycle_stages"]
    kpis = compute_kpi_bundle(data)

    snap = latest_user_snapshot(users, lifecycle)
    targets = snap[snap["pm_lifecycle"].isin(["at-risk", "churn-risk", "dormant"])]

    page_header(
        "Intervention Engine",
        "Rule-based plays for at-risk, churn-risk, and dormant users — no ML scoring layer.",
    )

    metric_row(
        [
            ("Intervention pool", f"{len(targets):,}", "At-risk + churn-risk + dormant users."),
            ("Avg churn-risk score", f"{targets['churn_risk_score'].mean():.2f}", "Within intervention pool."),
            ("Discount-acquired", f"{targets['discount_acquired'].mean():.1%}", "Share eligible for habit-led offers."),
            ("Cart abandonment", f"{kpis['cart_abandonment']:.1%}", "Platform-wide abandon rate for context."),
        ]
    )

    st.markdown("##### Product insights")
    insight_row(intervention_insights(kpis))

    st.markdown("##### PM recommendations")
    for rec in pm_recommendations(kpis):
        recommendation_card(rec["title"], rec["body"], rec["action"], rec["priority"])

    col1, col2 = st.columns(2)
    with col1:
        funnel = notification_funnel(notifications)
        fig = px.funnel(funnel, x="count", y="stage", labels={"count": "Messages", "stage": "Funnel stage"})
        apply_chart_style(fig, "Notification funnel", x_title="Count")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        by_type = (
            notifications.groupby("notification_type", observed=True)
            .agg(sent=("notification_id", "count"), converted=("converted", "sum"))
            .assign(conversion_rate=lambda d: d["converted"] / d["sent"])
            .reset_index()
            .sort_values("conversion_rate", ascending=False)
        )
        fig2 = px.bar(by_type, x="notification_type", y="conversion_rate", labels={"conversion_rate": "Conversion rate"})
        apply_chart_style(fig2, "Conversion by notification type", y_title="Converted / sent")
        fig2.update_yaxes(tickformat=".1%")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("##### Priority intervention queue (top 200)")
    if not targets.empty:
        priority = targets.sort_values("churn_risk_score", ascending=False).head(200)
        st.dataframe(
            priority[
                ["user_id", "pm_lifecycle", "segment", "city", "churn_risk_score", "days_since_last_order"]
            ],
            use_container_width=True,
            height=360,
            hide_index=True,
        )
