"""Behavioral and retention metrics for PM analytics."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.utils import cohort_retention, delivery_trust_metrics

PM_LIFECYCLE_ORDER = ["active", "habitual", "at-risk", "churn-risk", "dormant"]


def assign_pm_lifecycle(latest: pd.DataFrame) -> pd.Series:
    """Map raw lifecycle + behavior flags to PM-facing stages."""
    stage = latest["lifecycle_stage"].astype(str)
    pm = pd.Series("active", index=latest.index)

    pm = pm.mask(stage.eq("habitual"), "habitual")
    pm = pm.mask(stage.eq("churned"), "dormant")
    pm = pm.mask(stage.eq("at_risk"), "at-risk")

    churn_flag = latest["churn_risk_score"].ge(0.55) | latest["segment"].eq("churn_risk")
    pm = pm.mask(churn_flag & pm.isin(["active", "at-risk"]), "churn-risk")
    return pm


def latest_user_snapshot(users: pd.DataFrame, lifecycle: pd.DataFrame) -> pd.DataFrame:
    latest = lifecycle.sort_values("observed_at").groupby("user_id").tail(1)
    merged = latest.merge(
        users[["user_id", "segment", "discount_acquired", "churn_risk_score", "signup_at"]],
        on="user_id",
    )
    merged["pm_lifecycle"] = assign_pm_lifecycle(merged)
    return merged


def pm_lifecycle_distribution(users: pd.DataFrame, lifecycle: pd.DataFrame) -> pd.DataFrame:
    snap = latest_user_snapshot(users, lifecycle)
    return (
        snap["pm_lifecycle"]
        .value_counts(normalize=True)
        .reindex(PM_LIFECYCLE_ORDER, fill_value=0)
        .rename("share")
        .reset_index()
        .rename(columns={"index": "pm_lifecycle"})
    )


def delivery_trust_score(orders: pd.DataFrame) -> float:
    m = delivery_trust_metrics(orders)
    slippage_penalty = min(1.0, m["avg_slippage_min"] / 30)
    score = 100 * (
        0.45 * m["on_time_rate"] + 0.35 * (1 - m["delay_rate"]) + 0.20 * (1 - slippage_penalty)
    )
    return round(float(score), 1)


def reorder_gap_distribution(orders: pd.DataFrame) -> pd.DataFrame:
    gaps = orders.dropna(subset=["days_since_prior_order"]).copy()
    gaps["gap_bucket"] = pd.cut(
        gaps["days_since_prior_order"],
        bins=[0, 3, 7, 14, 21, 35, 999],
        labels=["1-3d", "4-7d", "8-14d", "15-21d", "22-35d", "35d+"],
    )
    return gaps.groupby("gap_bucket", observed=True).size().reset_index(name="orders")


def orders_per_active_week(orders: pd.DataFrame) -> pd.DataFrame:
    o = orders.copy()
    o["week"] = o["ordered_at"].dt.to_period("W")
    weekly = o.groupby(["user_id", "week"]).size().reset_index(name="orders_in_week")
    summary = weekly.groupby("user_id")["orders_in_week"].mean().reset_index(name="avg_orders_per_active_week")
    return summary


def essential_penetration(orders: pd.DataFrame, users: pd.DataFrame) -> dict[str, float]:
    flags = (
        users[["user_id", "discount_acquired"]]
        .merge(orders.groupby("user_id")["is_essential"].any().rename("has_essential"), on="user_id", how="left")
        .fillna({"has_essential": False})
    )
    organic = flags.loc[~flags["discount_acquired"], "has_essential"]
    discount = flags.loc[flags["discount_acquired"], "has_essential"]
    return {
        "order_share": float(orders["is_essential"].mean()),
        "user_penetration": float(flags["has_essential"].mean()),
        "discount_user_pen": float(discount.mean()) if len(discount) else 0.0,
        "organic_user_pen": float(organic.mean()) if len(organic) else 0.0,
    }


def time_to_second_order(orders: pd.DataFrame) -> dict[str, float]:
    ranked = (
        orders.sort_values("ordered_at")
        .groupby("user_id")["ordered_at"]
        .agg(first="first", second=lambda s: s.iloc[1] if len(s) > 1 else pd.NaT)
        .reset_index()
    )
    gaps = ranked.dropna(subset=["second"])
    if gaps.empty:
        return {"median_days": 0.0, "pct_within_5d": 0.0, "pct_never_second": 1.0}
    gap_days = (gaps["second"] - gaps["first"]).dt.days
    n_users = orders["user_id"].nunique()
    return {
        "median_days": float(gap_days.median()),
        "pct_within_5d": float((gap_days <= 5).mean()),
        "pct_never_second": float(1 - len(gaps) / n_users),
    }


def delay_impact_on_reorder(orders: pd.DataFrame) -> dict[str, float]:
    """Compare 2nd-order rate after delayed vs on-time first delivery."""
    first = orders.sort_values("ordered_at").groupby("user_id").first().reset_index()
    order_counts = orders.groupby("user_id").size()
    first["repeat"] = first["user_id"].map(order_counts).ge(2)
    delayed = first[first["delayed"]]["repeat"].mean() if first["delayed"].any() else 0.0
    on_time = first[~first["delayed"]]["repeat"].mean() if (~first["delayed"]).any() else 0.0
    return {"repeat_after_delayed_first": float(delayed), "repeat_after_on_time_first": float(on_time)}


def basket_diversity_habit(orders: pd.DataFrame) -> pd.DataFrame:
    diversity = orders.groupby("user_id")["category"].nunique().reset_index(name="unique_categories")
    diversity["order_count"] = diversity["user_id"].map(orders.groupby("user_id").size())
    diversity["repeat_buyer"] = diversity["order_count"].ge(2)
    return (
        diversity.groupby("unique_categories", observed=True)
        .agg(repeat_rate=("repeat_buyer", "mean"), users=("user_id", "count"))
        .reset_index()
    )


def acquisition_retention_d30(orders: pd.DataFrame, users: pd.DataFrame) -> pd.DataFrame:
    u = users[["user_id", "discount_acquired", "signup_at"]].copy()
    u["acquisition"] = np.where(u["discount_acquired"], "Discount", "Organic")
    joined = orders.merge(u[["user_id", "signup_at"]], on="user_id")
    joined["days_since_signup"] = (joined["ordered_at"] - joined["signup_at"]).dt.days
    within_30 = joined[joined["days_since_signup"].between(0, 30, inclusive="both")]
    activated_ids = within_30.groupby("user_id").size().ge(1)
    repeat_ids = within_30.groupby("user_id").size().ge(2)
    u["d30_activation"] = u["user_id"].isin(activated_ids.index[activated_ids])
    u["d30_repeat"] = u["user_id"].isin(repeat_ids.index[repeat_ids])
    return (
        u.groupby("acquisition")
        .agg(users=("user_id", "count"), d30_activation=("d30_activation", "mean"), d30_repeat=("d30_repeat", "mean"))
        .reset_index()
    )


def cohort_retention_by_acquisition(orders: pd.DataFrame, users: pd.DataFrame, horizon: int = 8) -> pd.DataFrame:
    o = orders.merge(users[["user_id", "discount_acquired"]], on="user_id")
    rows = []
    for label, mask in [("Organic", ~o["discount_acquired"]), ("Discount", o["discount_acquired"])]:
        sub = o.loc[mask]
        if sub.empty:
            continue
        mat = cohort_retention(sub, horizon)
        w4 = mat["W4"].mean() if "W4" in mat.columns else np.nan
        rows.append({"acquisition": label, "W4_retention": w4, "W8_retention": mat.iloc[:, -1].mean()})
    return pd.DataFrame(rows)


def compute_kpi_bundle(data: dict) -> dict:
    users, orders, sessions, _lifecycle = (
        data["users"],
        data["orders"],
        data["sessions"],
        data["lifecycle_stages"],
    )
    t2s = time_to_second_order(orders)
    pen = essential_penetration(orders, users)
    delay_impact = delay_impact_on_reorder(orders)
    opw = orders_per_active_week(orders)["avg_orders_per_active_week"]
    acq = acquisition_retention_d30(orders, users)
    organic_rep = float(acq.loc[acq["acquisition"] == "Organic", "d30_repeat"].iloc[0]) if (acq["acquisition"] == "Organic").any() else 0.0
    discount_rep = float(acq.loc[acq["acquisition"] == "Discount", "d30_repeat"].iloc[0]) if (acq["acquisition"] == "Discount").any() else 0.0
    return {
        "delivery_trust_score": delivery_trust_score(orders),
        "median_reorder_gap": float(
            orders.dropna(subset=["days_since_prior_order"])["days_since_prior_order"].median()
        ),
        "avg_orders_per_active_week": float(opw.median()),
        "essential_order_share": pen["order_share"],
        "essential_user_penetration": pen["user_penetration"],
        "median_time_to_second_order": t2s["median_days"],
        "pct_second_order_within_5d": t2s["pct_within_5d"],
        "pct_never_second_order": t2s["pct_never_second"],
        "repeat_after_delayed_first": delay_impact["repeat_after_delayed_first"],
        "repeat_after_on_time_first": delay_impact["repeat_after_on_time_first"],
        "cart_abandonment": float(sessions[sessions["cart_added"]]["abandoned"].mean()),
        "organic_d30_repeat": organic_rep,
        "discount_d30_repeat": discount_rep,
    }
