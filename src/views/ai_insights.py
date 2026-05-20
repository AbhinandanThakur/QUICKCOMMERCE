import streamlit as st

from src.insights import growth_brief_insights, pm_recommendations
from src.metrics import compute_kpi_bundle
from src.ui import (
    Trend,
    critical_insights,
    insight_card,
    kpi_row,
    leadership_brief,
    page_header,
    recommendation_card,
    section_title,
)


def render(data: dict) -> None:
    kpis = compute_kpi_bundle(data)

    page_header(
        "Leadership Brief",
        "High-signal summary for weekly growth review: what’s working, what’s risky, and what to do next.",
    )

    kpi_row(
        [
            dict(
                label="Delivery Trust",
                value=f"{kpis['delivery_trust_score']:.0f}/100",
                subtext="Composite: on-time, delay rate, slippage minutes.",
                badge_text="Ops",
            ),
            dict(
                label="Organic D30 Repeat",
                value=f"{kpis['organic_d30_repeat']:.1%}",
                subtext="Cohort quality (2+ orders in first 30 days).",
                trend=Trend(delta=(kpis["organic_d30_repeat"] - kpis["discount_d30_repeat"]) * 100, suffix="pp", label="vs discount"),
                badge_text="Quality",
            ),
            dict(
                label="Essentials Penetration",
                value=f"{kpis['essential_user_penetration']:.1%}",
                subtext="Users with ≥1 essentials order (habit foundation).",
                badge_text="Habit",
            ),
            dict(
                label="Activation Leak",
                value=f"{kpis['pct_never_second_order']:.1%}",
                subtext="Users who never reach order #2.",
                badge_text="Risk",
            ),
        ]
    )

    section_title("Critical Insights")
    critical_insights(
        [
            (
                "Churn warning",
                "Users failing to place second order within 5 days show materially elevated churn risk — treat D+5 as the activation deadline.",
            ),
            (
                "Retention driver",
                "Delivery delays impact retention more than discount depth: trust loss shows up before lifecycle flags flip.",
            ),
            (
                "Habit signal",
                "Essential-category buyers form habits faster; staples-led early baskets are the most reliable path to repeat.",
            ),
        ]
    )

    section_title("What changed the outcome (story)")
    for title, body, tag in growth_brief_insights(kpis, data["orders"], data["users"], data["sessions"], data["lifecycle_stages"]):
        insight_card(title, body, tag)

    section_title("Operational recommendations (next 7 days)")
    for rec in pm_recommendations(kpis):
        recommendation_card(rec["title"], rec["body"], rec["action"], rec["priority"])

    section_title("Leadership Brief")
    leadership_brief(
        "War-room summary",
        [
            "Biggest retention driver: delivery trust on the first 1–3 orders (protect the first impression).",
            "Biggest churn risk: users missing the second order within 5 days (activation deadline).",
            "Highest-leverage move: essentials-led nudges + fee waivers tied to D+3 to D+5 windows.",
        ],
    )

    st.caption(
        "Insights are generated from rule-based thresholds on synthetic data. "
        "Connect production warehouse tables to refresh nightly for live PM reviews."
    )
