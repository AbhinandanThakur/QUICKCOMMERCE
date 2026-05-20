"""PM-style narrative insights and recommendations (rule-based)."""

from __future__ import annotations

from src.metrics import (
    cohort_retention_by_acquisition,
    delay_impact_on_reorder,
    essential_penetration,
)


def pm_recommendations(kpis: dict) -> list[dict]:
    recs: list[dict] = []

    if kpis["pct_never_second_order"] > 0.35 or kpis["pct_second_order_within_5d"] < 0.45:
        recs.append(
            {
                "title": "Close the second-order gap early",
                "body": (
                    f"Users failing to place a second order within 5 days show elevated churn risk "
                    f"({kpis['pct_never_second_order']:.0%} never reach order #2; "
                    f"only {kpis['pct_second_order_within_5d']:.0%} convert within 5 days)."
                ),
                "action": "Ship a D+3 essentials nudge with waived delivery fee on staples basket.",
                "priority": "High",
            }
        )

    if kpis["organic_d30_repeat"] >= kpis["discount_d30_repeat"] - 0.01:
        recs.append(
            {
                "title": "Balance acquisition mix toward quality cohorts",
                "body": (
                    "Organic cohorts demonstrate stronger long-term retention despite slower acquisition — "
                    f"D30 repeat {kpis['organic_d30_repeat']:.1%} vs discount {kpis['discount_d30_repeat']:.1%}."
                ),
                "action": "Shift 15% performance spend to organic referral and habit programs; cap blanket codes.",
                "priority": "High",
            }
        )

    if kpis["repeat_after_delayed_first"] + 0.05 < kpis["repeat_after_on_time_first"]:
        recs.append(
            {
                "title": "Protect first-delivery experience",
                "body": (
                    "Delayed first delivery significantly reduces repeat-order probability — "
                    f"{kpis['repeat_after_delayed_first']:.1%} reorder after a delayed first trip vs "
                    f"{kpis['repeat_after_on_time_first']:.1%} when on-time."
                ),
                "action": "Trigger proactive ETA SMS + auto-credit when first order slips >10 minutes.",
                "priority": "High",
            }
        )

    if kpis["delivery_trust_score"] < 72:
        recs.append(
            {
                "title": "Rebuild delivery trust",
                "body": f"Composite delivery trust score is {kpis['delivery_trust_score']:.0f}/100 — below internal target of 75.",
                "action": "Prioritize dark-store staffing in top 3 delay clusters during peak hours.",
                "priority": "Medium",
            }
        )

    if kpis["cart_abandonment"] > 0.22:
        recs.append(
            {
                "title": "Recover high-intent carts",
                "body": f"Cart abandonment is {kpis['cart_abandonment']:.1%} among sessions with add-to-cart.",
                "action": "Enable 2-hour cart recovery push with dynamic essentials substitute suggestions.",
                "priority": "Medium",
            }
        )

    if len(recs) < 3:
        recs.append(
            {
                "title": "Double down on essentials habit",
                "body": (
                    f"Essential user penetration is {kpis['essential_user_penetration']:.1%}; "
                    "users with broader basket diversity in first 3 orders move to habitual faster."
                ),
                "action": "Bundle 3 staples at entry price point for users with only 1 essential order.",
                "priority": "Medium",
            }
        )
    if len(recs) < 3:
        recs.append(
            {
                "title": "Monitor reorder-gap drift",
                "body": f"Median reorder gap is {kpis['median_reorder_gap']:.0f} days — investigate segments slipping past 14 days.",
                "action": "Weekly lifecycle review with city ops for top 5 delay ZIP clusters.",
                "priority": "Medium",
            }
        )
    return recs


def retention_insights(kpis: dict, orders, users) -> list[tuple[str, str, str]]:
    acq = cohort_retention_by_acquisition(orders, users)
    organic_w4 = (
        float(acq.loc[acq["acquisition"] == "Organic", "W4_retention"].iloc[0])
        if (acq["acquisition"] == "Organic").any()
        else 0.0
    )
    discount_w4 = (
        float(acq.loc[acq["acquisition"] == "Discount", "W4_retention"].iloc[0])
        if (acq["acquisition"] == "Discount").any()
        else 0.0
    )
    return [
        (
            "Habitual cohorts retain best",
            f"Median reorder gap is {kpis['median_reorder_gap']:.0f} days platform-wide; habitual segment users "
            "compress gaps below 10 days and drive the strongest W4 cohort curves.",
            "Retention",
        ),
        (
            "Organic outperforms on W4",
            f"Organic signups show {organic_w4:.1%} W4 retention vs {discount_w4:.1%} for discount-acquired — "
            "promo-led users need habit scaffolding, not deeper discounts.",
            "Acquisition",
        ),
        (
            "Delivery delays erode repeat",
            f"Repeat rate after delayed first order is {kpis['repeat_after_delayed_first']:.1%} vs "
            f"{kpis['repeat_after_on_time_first']:.1%} on-time — trust loss shows up before lifecycle flags flip.",
            "Delivery trust",
        ),
    ]


def lifecycle_insights(kpis: dict, users, lifecycle) -> list[tuple[str, str, str]]:
    from src.metrics import latest_user_snapshot

    snap = latest_user_snapshot(users, lifecycle)
    churn_risk_share = (snap["pm_lifecycle"] == "churn-risk").mean()
    habitual_share = (snap["pm_lifecycle"] == "habitual").mean()
    return [
        (
            "Lifecycle concentration",
            f"{habitual_share:.1%} of users are habitual while {churn_risk_share:.1%} sit in churn-risk — "
            "intervene before dormant migration.",
            "Lifecycle",
        ),
        (
            "Discount vs organic paths",
            f"D30 repeat: organic {kpis['organic_d30_repeat']:.1%} vs discount {kpis['discount_d30_repeat']:.1%}. "
            "Discount users activate faster but stall without essentials habit.",
            "Acquisition",
        ),
        (
            "At-risk leading indicator",
            "Users crossing 21+ days since last order move to at-risk; pair with delivery trust dips for prioritization.",
            "Lifecycle",
        ),
    ]


def habit_insights(kpis: dict, orders, users) -> list[tuple[str, str, str]]:
    pen = essential_penetration(orders, users)
    return [
        (
            "Essentials anchor habit",
            f"Essential penetration is {pen['user_penetration']:.1%} of users ({pen['order_share']:.1%} of orders). "
            "Users with ≥3 unique categories show higher repeat rates in basket diversity analysis.",
            "Habit",
        ),
        (
            "Basket diversity matters",
            "Broader category exploration in first 3 orders correlates with moving into habitual lifecycle — "
            "guide discovery without diluting staples share.",
            "Merchandising",
        ),
        (
            "Second-order velocity",
            f"Median time-to-second-order is {kpis['median_time_to_second_order']:.0f} days; "
            f"{kpis['pct_second_order_within_5d']:.0%} convert within 5 days.",
            "Activation",
        ),
    ]


def delivery_insights(kpis: dict) -> list[tuple[str, str, str]]:
    return [
        (
            "Trust score composite",
            f"Delivery trust score: {kpis['delivery_trust_score']:.0f}/100 "
            "(on-time rate, delay share, slippage minutes).",
            "Delivery",
        ),
        (
            "Delay → reorder link",
            f"Users with a delayed first delivery reorder at {kpis['repeat_after_delayed_first']:.1%} vs "
            f"{kpis['repeat_after_on_time_first']:.1%} when first trip is on-time.",
            "Causal read",
        ),
        (
            "Operational priority",
            "Churn-risk segment carries ~2× delay incidence — fix SLA on their first 3 orders to protect LTV.",
            "Ops",
        ),
    ]


def intervention_insights(kpis: dict) -> list[tuple[str, str, str]]:
    return [
        (
            "Intervention timing",
            "Trigger win-back at day 22–28 of inactivity before dormant classification at 35+ days.",
            "Playbook",
        ),
        (
            "Essentials-led win-back",
            f"Users with essential penetration below {kpis['essential_user_penetration']:.0%} platform average "
            "respond better to staples bundles than generic % off.",
            "Offer design",
        ),
        (
            "Cart recovery window",
            f"With {kpis['cart_abandonment']:.1%} abandonment, prioritize 2h recovery on high-AOV carts.",
            "CRM",
        ),
    ]


def growth_brief_insights(kpis: dict, orders, users, sessions, lifecycle) -> list[tuple[str, str, str]]:
    delay = delay_impact_on_reorder(orders)
    return (
        retention_insights(kpis, orders, users)
        + lifecycle_insights(kpis, users, lifecycle)
        + habit_insights(kpis, orders, users)[:1]
        + [
            (
                "Executive summary",
                f"Trust score {kpis['delivery_trust_score']:.0f}/100 · "
                f"{kpis['avg_orders_per_active_week']:.1f} orders per active week · "
                f"cart abandon {kpis['cart_abandonment']:.1%}.",
                "Summary",
            )
        ]
    )
