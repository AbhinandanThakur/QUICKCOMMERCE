import plotly.express as px
import streamlit as st

from src.insights import habit_insights, pm_recommendations
from src.metrics import basket_diversity_habit, compute_kpi_bundle, essential_penetration, orders_per_active_week
from src.ui import apply_chart_style, insight_row, metric_row, page_header, recommendation_card
from src.utils import cart_abandonment_rate, essential_mix


def render(data: dict) -> None:
    users, sessions, orders = data["users"], data["sessions"], data["orders"]
    kpis = compute_kpi_bundle(data)
    pen = essential_penetration(orders, users)

    page_header(
        "Habit Formation Funnel",
        "Activation path from browse → cart → repeat, with essentials and basket breadth signals.",
    )

    metric_row(
        [
            ("Orders / active week", f"{kpis['avg_orders_per_active_week']:.2f}", "Median user-level orders in weeks with activity."),
            ("Essential penetration", f"{pen['user_penetration']:.1%}", "Users with ≥1 essential-category order."),
            ("Time to 2nd order", f"{kpis['median_time_to_second_order']:.0f}d", "Median days between first and second order."),
            ("Cart abandonment", f"{kpis['cart_abandonment']:.1%}", "Sessions with cart but no same-day conversion."),
        ]
    )

    st.markdown("##### Product insights")
    insight_row(habit_insights(kpis, orders, users))

    signed_up = len(users)
    with_cart = sessions[sessions["cart_added"]]["user_id"].nunique()
    ordered = orders["user_id"].nunique()
    repeat = orders.groupby("user_id").size().gt(1).sum()
    habitual = users[users["segment"] == "habitual"]["user_id"].nunique()

    col1, col2 = st.columns([1, 1.2])
    with col1:
        funnel_df = {
            "Stage": ["Signed up", "Added to cart", "Placed 1st order", "Repeat order", "Habitual segment"],
            "Users": [signed_up, with_cart, ordered, repeat, habitual],
        }
        fig = px.funnel(funnel_df, x="Users", y="Stage")
        apply_chart_style(fig, "Habit formation funnel", x_title="Unique users")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        diversity = basket_diversity_habit(orders)
        fig_div = px.line(
            diversity,
            x="unique_categories",
            y="repeat_rate",
            markers=True,
            labels={"unique_categories": "Unique categories ordered", "repeat_rate": "Repeat-buyer rate"},
        )
        apply_chart_style(fig_div, "Basket diversity vs repeat purchase", y_title="Repeat buyer rate")
        fig_div.update_yaxes(tickformat=".0%")
        st.plotly_chart(fig_div, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        mix = essential_mix(orders)
        mix["label"] = mix["is_essential"].map({True: "Essential", False: "Non-essential"})
        fig2 = px.pie(mix, names="label", values="orders", hole=0.45)
        apply_chart_style(fig2, "Order mix: essential vs non-essential")
        st.plotly_chart(fig2, use_container_width=True)

    with col4:
        acq_pen = {
            "cohort": ["Organic", "Discount"],
            "penetration": [pen["organic_user_pen"], pen["discount_user_pen"]],
        }
        fig3 = px.bar(acq_pen, x="cohort", y="penetration", text=[f"{v:.1%}" for v in acq_pen["penetration"]])
        apply_chart_style(fig3, "Essential penetration by acquisition", y_title="User penetration")
        fig3.update_yaxes(tickformat=".0%")
        fig3.update_traces(textposition="outside")
        st.plotly_chart(fig3, use_container_width=True)

    opw = orders_per_active_week(orders)
    fig_hist = px.histogram(opw, x="avg_orders_per_active_week", nbins=30, labels={"avg_orders_per_active_week": "Avg orders per active week"})
    apply_chart_style(fig_hist, "Distribution: orders per active week", x_title="Avg orders in active weeks", y_title="Users")
    st.plotly_chart(fig_hist, use_container_width=True)

    for rec in pm_recommendations(kpis):
        if "second order" in rec["body"].lower() or "cart" in rec["body"].lower():
            recommendation_card(rec["title"], rec["body"], rec["action"], rec["priority"])
            break
