"""
Synthetic quick-commerce datasets: users, sessions, orders, notifications, lifecycle stages.
Run: python -m src.generate_data
"""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from src.config import (
    CITIES,
    DATA_DIR,
    DATA_FILES,
    DAYS_DEFAULT,
    ESSENTIAL_CATEGORIES,
    NON_ESSENTIAL_CATEGORIES,
    N_USERS_DEFAULT,
    RNG_SEED_DEFAULT,
)

SEGMENTS = ("standard", "habitual", "discount_hunter", "churn_risk")


def _end_ts(start: pd.Timestamp, days: int) -> pd.Timestamp:
    return start + pd.Timedelta(days=days)


def generate_users(
    rng: np.random.Generator,
    n_users: int,
    start: pd.Timestamp,
    days: int,
) -> pd.DataFrame:
    signup_offsets = rng.integers(0, days, size=n_users)
    signup_at = start + pd.to_timedelta(signup_offsets, unit="D")

    segment_probs = np.array([0.42, 0.22, 0.20, 0.16])
    segment = rng.choice(list(SEGMENTS), size=n_users, p=segment_probs)

    discount_acquired = (segment == "discount_hunter") | (
        (segment == "standard") & (rng.random(n_users) < 0.18)
    )
    essential_affinity = np.clip(
        rng.normal(
            loc=np.select(
                [segment == "habitual", segment == "churn_risk", segment == "discount_hunter"],
                [0.72, 0.38, 0.48],
                default=0.55,
            ),
            scale=0.08,
            size=n_users,
        ),
        0.15,
        0.95,
    )
    churn_risk_score = np.clip(
        rng.normal(
            loc=np.select(
                [segment == "churn_risk", segment == "habitual"],
                [0.78, 0.22],
                default=0.45,
            ),
            scale=0.12,
            size=n_users,
        ),
        0.05,
        0.99,
    )

    return pd.DataFrame(
        {
            "user_id": np.arange(1, n_users + 1, dtype=np.int32),
            "signup_at": signup_at,
            "city": rng.choice(CITIES, size=n_users),
            "segment": segment,
            "discount_acquired": discount_acquired,
            "essential_affinity": essential_affinity.round(3),
            "churn_risk_score": churn_risk_score.round(3),
        }
    )


def _inter_order_days(rng: np.random.Generator, segment: str, order_idx: int) -> int:
    if segment == "habitual":
        base = rng.lognormal(mean=2.0, sigma=0.35)
    elif segment == "discount_hunter":
        base = rng.lognormal(mean=2.6, sigma=0.45)
    elif segment == "churn_risk":
        base = rng.lognormal(mean=3.1 + min(order_idx, 6) * 0.15, sigma=0.5)
    else:
        base = rng.lognormal(mean=2.4, sigma=0.4)
    return int(np.clip(base, 1, 45))


def generate_orders(users: pd.DataFrame, rng: np.random.Generator, start: pd.Timestamp, days: int) -> pd.DataFrame:
    end = _end_ts(start, days)
    rows: list[dict] = []
    order_id = 1

    for row in users.itertuples(index=False):
        t = row.signup_at + pd.Timedelta(hours=int(rng.integers(6, 72)))
        order_idx = 0
        prev_t = None
        while t < end:
            is_essential = rng.random() < row.essential_affinity
            category = rng.choice(
                ESSENTIAL_CATEGORIES if is_essential else NON_ESSENTIAL_CATEGORIES
            )
            promised = int(rng.integers(12, 32))
            delay_prob = 0.08 if row.segment == "habitual" else 0.14
            if row.segment == "churn_risk":
                delay_prob = 0.28 + min(order_idx, 5) * 0.02
            delayed = rng.random() < delay_prob
            delay_min = int(rng.integers(8, 55)) if delayed else int(rng.exponential(4))
            actual = promised + delay_min
            discount_pct = 0.0
            if row.discount_acquired or row.segment == "discount_hunter":
                discount_pct = float(rng.choice([0, 5, 10, 15, 20], p=[0.35, 0.25, 0.2, 0.12, 0.08]))
            gmv = float(
                np.clip(rng.lognormal(mean=5.6 if is_essential else 5.9, sigma=0.35) * (1 - discount_pct / 100), 80, 2500)
            )
            rows.append(
                {
                    "order_id": order_id,
                    "user_id": row.user_id,
                    "ordered_at": t,
                    "category": category,
                    "is_essential": bool(is_essential),
                    "gmv": round(gmv, 2),
                    "discount_pct": discount_pct,
                    "promised_delivery_min": promised,
                    "actual_delivery_min": actual,
                    "delayed": bool(delayed),
                    "days_since_prior_order": (t - prev_t).days if prev_t is not None else np.nan,
                }
            )
            order_id += 1
            order_idx += 1
            prev_t = t
            gap = _inter_order_days(rng, row.segment, order_idx)
            t += pd.Timedelta(days=gap)

    return pd.DataFrame(rows)


def generate_sessions(
    users: pd.DataFrame,
    orders: pd.DataFrame,
    rng: np.random.Generator,
    start: pd.Timestamp,
    days: int,
) -> pd.DataFrame:
    end = _end_ts(start, days)
    order_days = (
        orders.groupby("user_id")["ordered_at"].apply(lambda s: set(s.dt.floor("D")))
        if not orders.empty
        else pd.Series(dtype=object)
    )

    rows: list[dict] = []
    session_id = 1

    for row in users.itertuples(index=False):
        lam = {"habitual": 14, "standard": 9, "discount_hunter": 11, "churn_risk": 6}[row.segment]
        n_sessions = int(rng.poisson(lam))
        abandon_base = {"habitual": 0.12, "standard": 0.22, "discount_hunter": 0.26, "churn_risk": 0.38}[
            row.segment
        ]

        for _ in range(n_sessions):
            offset_days = int(rng.integers(0, max(1, (end - row.signup_at).days)))
            session_start = row.signup_at + pd.Timedelta(days=offset_days, hours=int(rng.integers(7, 23)))
            if session_start >= end:
                continue
            cart_added = rng.random() < 0.72
            session_day = session_start.floor("D")
            user_order_days = order_days.get(row.user_id, set())
            order_placed = session_day in user_order_days and rng.random() < 0.65
            abandoned = cart_added and not order_placed and rng.random() < abandon_base
            rows.append(
                {
                    "session_id": session_id,
                    "user_id": row.user_id,
                    "session_start": session_start,
                    "device": rng.choice(["android", "ios", "web"], p=[0.55, 0.38, 0.07]),
                    "cart_added": bool(cart_added),
                    "order_placed": bool(order_placed),
                    "abandoned": bool(abandoned),
                    "items_in_cart": int(rng.integers(1, 12)) if cart_added else 0,
                }
            )
            session_id += 1

    return pd.DataFrame(rows)


def generate_notifications(
    users: pd.DataFrame,
    orders: pd.DataFrame,
    rng: np.random.Generator,
    start: pd.Timestamp,
    days: int,
) -> pd.DataFrame:
    end = _end_ts(start, days)
    last_order = orders.groupby("user_id")["ordered_at"].max() if not orders.empty else pd.Series(dtype="datetime64[ns]")
    rows: list[dict] = []
    notif_id = 1
    channels = ["push", "sms", "email", "in_app"]
    types = ["reorder_nudge", "cart_recovery", "delivery_update", "winback_offer", "habit_reminder"]

    for row in users.itertuples(index=False):
        n = int(rng.integers(4, 16))
        for _ in range(n):
            sent_at = row.signup_at + pd.Timedelta(
                days=int(rng.integers(0, max(1, (end - row.signup_at).days))),
                hours=int(rng.integers(8, 22)),
            )
            if sent_at >= end:
                continue
            ntype = rng.choice(types)
            opened = rng.random() < (0.42 - 0.12 * (row.segment == "churn_risk"))
            clicked = opened and rng.random() < 0.35
            converted = clicked and rng.random() < 0.18
            if row.segment == "churn_risk" and (sent_at > last_order.get(row.user_id, row.signup_at) + pd.Timedelta(days=21)):
                ntype = "winback_offer"
            rows.append(
                {
                    "notification_id": notif_id,
                    "user_id": row.user_id,
                    "sent_at": sent_at,
                    "channel": rng.choice(channels, p=[0.5, 0.2, 0.1, 0.2]),
                    "notification_type": ntype,
                    "opened": bool(opened),
                    "clicked": bool(clicked),
                    "converted": bool(converted),
                }
            )
            notif_id += 1

    return pd.DataFrame(rows)


def assign_lifecycle_stages(snap: pd.DataFrame) -> pd.Series:
    oc = snap["order_count_to_date"].to_numpy()
    dsl = snap["days_since_last_order"].fillna(-1).to_numpy(dtype=float)
    es = snap["essential_share"].to_numpy()
    dr = snap["delay_rate"].to_numpy()
    seg = snap["segment"].to_numpy()

    has_orders = oc > 0
    churned = has_orders & (dsl > 35)
    at_risk = has_orders & ~churned & ((seg == "churn_risk") | (dsl > 21))
    habitual = (
        has_orders
        & ~churned
        & ~at_risk
        & (((oc >= 6) & (es >= 0.45) & (dr < 0.2)) | ((oc >= 3) & (dsl < 14)))
    )
    win_back = has_orders & ~churned & ~at_risk & ~habitual & (dsl > 28) & (dsl <= 35)

    stage = np.where(oc == 0, "new", "activated")
    stage = np.where(oc == 1, "activated", stage)
    stage = np.where(churned, "churned", stage)
    stage = np.where(at_risk, "at_risk", stage)
    stage = np.where(habitual, "habitual", stage)
    stage = np.where(win_back, "win_back", stage)
    return pd.Series(stage, index=snap.index)


def generate_lifecycle_stages(
    users: pd.DataFrame,
    orders: pd.DataFrame,
    start: pd.Timestamp,
    days: int,
) -> pd.DataFrame:
    end = _end_ts(start, days)
    week_ends = pd.date_range(start + pd.Timedelta(days=7), end, freq="7D")
    frames: list[pd.DataFrame] = []

    for observed_at in week_ends:
        window = orders[orders["ordered_at"] <= observed_at]
        agg = window.groupby("user_id", as_index=False).agg(
            order_count_to_date=("order_id", "count"),
            last_order=("ordered_at", "max"),
            essential_share=("is_essential", "mean"),
            delay_rate=("delayed", "mean"),
        )
        snap = users.loc[users["signup_at"] <= observed_at, ["user_id", "segment"]].merge(
            agg, on="user_id", how="left"
        )
        snap["observed_at"] = observed_at
        snap["order_count_to_date"] = snap["order_count_to_date"].fillna(0).astype(int)
        snap["days_since_last_order"] = (observed_at - snap["last_order"]).dt.days
        snap["essential_share"] = snap["essential_share"].fillna(0.0)
        snap["delay_rate"] = snap["delay_rate"].fillna(0.0)

        snap["lifecycle_stage"] = assign_lifecycle_stages(snap)
        frames.append(
            snap[
                [
                    "user_id",
                    "observed_at",
                    "lifecycle_stage",
                    "order_count_to_date",
                    "days_since_last_order",
                ]
            ]
        )

    return pd.concat(frames, ignore_index=True)


def save_datasets(datasets: dict[str, pd.DataFrame], data_dir: Path | None = None) -> dict[str, Path]:
    data_dir = data_dir or DATA_DIR
    data_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    for name, df in datasets.items():
        filename = DATA_FILES[name]
        path = data_dir / filename
        df.to_csv(path, index=False)
        paths[name] = path
    return paths


def generate_all(
    n_users: int = N_USERS_DEFAULT,
    days: int = DAYS_DEFAULT,
    seed: int = RNG_SEED_DEFAULT,
    data_dir: Path | None = None,
) -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    start = pd.Timestamp.today().normalize() - pd.Timedelta(days=days)

    print(f"Generating {n_users:,} users over {days} days (seed={seed})...")
    users = generate_users(rng, n_users, start, days)

    print("Generating orders...")
    orders = generate_orders(users, rng, start, days)

    print("Generating sessions...")
    sessions = generate_sessions(users, orders, rng, start, days)

    print("Generating notifications...")
    notifications = generate_notifications(users, orders, rng, start, days)

    print("Generating lifecycle stages (weekly snapshots)...")
    lifecycle_stages = generate_lifecycle_stages(users, orders, start, days)

    datasets = {
        "users": users,
        "sessions": sessions,
        "orders": orders,
        "notifications": notifications,
        "lifecycle_stages": lifecycle_stages,
    }
    paths = save_datasets(datasets, data_dir)
    for name, path in paths.items():
        print(f"  {name}: {len(datasets[name]):,} rows -> {path}")
    return datasets


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate synthetic quick-commerce CSVs")
    parser.add_argument("--users", type=int, default=N_USERS_DEFAULT)
    parser.add_argument("--days", type=int, default=DAYS_DEFAULT)
    parser.add_argument("--seed", type=int, default=RNG_SEED_DEFAULT)
    args = parser.parse_args()
    generate_all(n_users=args.users, days=args.days, seed=args.seed)
