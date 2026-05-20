"""Analytics helpers for the retention dashboard."""

import pandas as pd


def cohort_retention(orders: pd.DataFrame, horizon_weeks: int = 8) -> pd.DataFrame:
    orders = orders.copy()
    orders["order_week"] = orders["ordered_at"].dt.to_period("W").dt.start_time
    first = orders.groupby("user_id")["order_week"].min().rename("cohort_week")
    orders = orders.merge(first, on="user_id")
    orders["period"] = ((orders["order_week"] - orders["cohort_week"]).dt.days // 7).astype(int)
    active = orders.groupby(["cohort_week", "period"])["user_id"].nunique()
    cohort_size = orders.groupby("cohort_week")["user_id"].nunique()
    matrix = (
        active.unstack(fill_value=0)
        .reindex(columns=range(horizon_weeks + 1), fill_value=0)
        .div(cohort_size, axis=0)
    )
    matrix.columns = [f"W{w}" for w in matrix.columns]
    return matrix


def reorder_interval_summary(orders: pd.DataFrame) -> pd.DataFrame:
    gaps = orders.dropna(subset=["days_since_prior_order"])
    if gaps.empty or "segment" not in gaps.columns:
        return pd.DataFrame(columns=["segment", "median_days", "p75_days", "users"])
    per_user = (
        gaps.groupby(["user_id", "segment"], observed=True)["days_since_prior_order"]
        .median()
        .reset_index(name="median_days")
    )
    return (
        per_user.groupby("segment", observed=True)
        .agg(
            median_days=("median_days", "median"),
            p75_days=("median_days", lambda s: s.quantile(0.75)),
            users=("user_id", "nunique"),
        )
        .reset_index()
    )


def lifecycle_distribution(lifecycle: pd.DataFrame, as_of: pd.Timestamp | None = None) -> pd.Series:
    df = lifecycle.copy()
    if as_of is not None:
        df = df[df["observed_at"] <= as_of]
    latest = df.sort_values("observed_at").groupby("user_id").tail(1)
    return latest["lifecycle_stage"].value_counts(normalize=True).sort_index()


def cart_abandonment_rate(sessions: pd.DataFrame) -> float:
    carts = sessions[sessions["cart_added"]]
    if carts.empty:
        return 0.0
    return float(carts["abandoned"].mean())


def delivery_trust_metrics(orders: pd.DataFrame) -> dict[str, float]:
    if orders.empty:
        return {"delay_rate": 0.0, "avg_slippage_min": 0.0, "on_time_rate": 0.0}
    slippage = orders["actual_delivery_min"] - orders["promised_delivery_min"]
    return {
        "delay_rate": float(orders["delayed"].mean()),
        "avg_slippage_min": float(slippage.mean()),
        "on_time_rate": float((slippage <= 5).mean()),
    }


def essential_mix(orders: pd.DataFrame) -> pd.DataFrame:
    return (
        orders.groupby("is_essential", as_index=False)
        .agg(orders=("order_id", "count"), gmv=("gmv", "sum"))
        .assign(share=lambda d: d["orders"] / d["orders"].sum())
    )


def notification_funnel(notifications: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "stage": ["sent", "opened", "clicked", "converted"],
            "count": [
                len(notifications),
                notifications["opened"].sum(),
                notifications["clicked"].sum(),
                notifications["converted"].sum(),
            ],
        }
    )


def rule_based_insights(
    users: pd.DataFrame,
    orders: pd.DataFrame,
    sessions: pd.DataFrame,
    lifecycle: pd.DataFrame,
) -> list[str]:
    insights: list[str] = []
    delay_rate = orders["delayed"].mean()
    if delay_rate > 0.15:
        insights.append(
            f"Delivery delays affect {delay_rate:.1%} of orders — prioritize SLA recovery for at-risk cohorts."
        )
    abandon = cart_abandonment_rate(sessions)
    if abandon > 0.2:
        insights.append(
            f"Cart abandonment sits at {abandon:.1%}; cart-recovery notifications show room to improve conversion."
        )
    disc = users["discount_acquired"].mean()
    insights.append(
        f"{disc:.1%} of users were discount-acquired; compare repeat curves vs organic signups in Lifecycle."
    )
    latest = lifecycle.sort_values("observed_at").groupby("user_id").tail(1)
    at_risk = (latest["lifecycle_stage"] == "at_risk").mean()
    insights.append(f"{at_risk:.1%} of users are currently at-risk based on weekly lifecycle snapshots.")
    essential_share = orders["is_essential"].mean()
    insights.append(
        f"Essential-category orders are {essential_share:.1%} of volume — anchor habit programs on staples replenishment."
    )
    return insights
