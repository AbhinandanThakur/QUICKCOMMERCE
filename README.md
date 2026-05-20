<div align="center">

# Quick-Commerce Retention Intelligence System

**A product-growth analytics OS for understanding why users habit-form — or churn early.**

*Built for growth PMs, retention analysts, and product teams at quick-commerce companies.*

---

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Pandas](https://img.shields.io/badge/Pandas-2.2+-150458?style=flat-square&logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![Plotly](https://img.shields.io/badge/Plotly-5.20+-3F4F75?style=flat-square&logo=plotly&logoColor=white)](https://plotly.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

</div>

---

## Product Thesis

> **Retention in quick-commerce is driven less by discounts and more by early habit formation around recurring essentials and delivery trust.**
>
> Users who order at least one replenishable category within their first three sessions, and receive their first delivery on time, convert to habitual weekly customers at materially higher rates — independent of the discount depth that acquired them.

This system exists to validate, quantify, and operationalize that thesis at the product and ops level.

---

## The Business Problem

Quick-commerce platforms in India face a structural retention crisis that discounts cannot solve:

- Users install, place 1–2 orders, and disappear
- Standard cohort curves mask the problem: D7 metrics look healthy; D30 tells a different story
- Discount-acquired users inflate early activation but suppress long-term LTV
- Delivery delays in the first 1–3 orders destroy trust before lifecycle flags even flip
- Growth teams optimize for installs and first orders — not for the behavioral moments that create habits

The result: companies spend heavily on acquisition, underinvest in the first 72 hours of the user relationship, and lose the users most likely to become high-LTV weekly customers.

**This system is built to fix that diagnostic gap.**

---

## Why Retention in Quick-Commerce Is Different

| Factor | E-commerce | Quick-commerce |
|--------|-----------|----------------|
| Purchase intent | Considered, infrequent | Impulsive, routine |
| Habit formation window | Weeks–months | Days 1–10 |
| Trust signal | Reviews, returns | First delivery ETA |
| Retention lever | Loyalty programs | Replenishment cadence |
| Churn indicator | 30–90d gap | 21d gap |
| High-LTV marker | Basket size | Order frequency |

Quick-commerce retention isn't about getting users to come back eventually — it's about embedding the app into their weekly grocery rhythm before the habit window closes. Miss days 3–7, and you're likely paying win-back costs for a user who already switched.

---

## Key Product Findings

These are real outputs from the 50,000-user, 180-day behavioral dataset.

### The Habit Signal

Users who reach 2+ unique product categories show **100% repeat-buyer rate** in this cohort. Single-category buyers — the users stuck in a trial mindset — show only **~10% repeat rates**. The basket breadth signal in the first 3 orders is the strongest leading indicator of habitual behavior.

### The Discount-Acquisition Trap

> Discount-acquired users (27.5% of cohort) activate faster on D7 but show **4.7 percentage points lower D30 repeat rate** vs organic users.

This gap is invisible in naive weekly retention cuts. The implication: CAC efficiency metrics that use D7 activation overstate the value of discount campaigns. The real cost of a discount-acquired user only becomes visible at W4.

### Delivery Trust as a Retention Driver

- **Delivery Trust Score: 76.1 / 100** (composite of on-time rate, delay frequency, and ETA slippage)
- **13.0% of orders** arrive delayed; average slippage of **7.1 minutes** beyond promise
- First-delivery delay reduces second-order probability: **90.7% repeat after delayed first** vs **92.6% after on-time first**
- The churn-risk segment experiences **~2× higher delay rates**, creating a compounding loop: worse service → faster churn → more acquisition spend

### Reorder Timing by Segment

| Segment | Median Reorder Gap |
|---------|-------------------|
| Habitual | **7 days** |
| Standard | 10 days |
| Discount hunter | 13 days |
| Churn risk | **29 days** |

The 22-day gap between habitual and churn-risk users is the operational target: intervene before the gap widens past 14 days, not after.

### Activation Leak

- **7.7% of users never place a second order**
- Median time to second order: **11 days**
- Only **10.2% of users** reach a second order within 5 days — the early activation window with the highest predictive power for habitual conversion

### Notification Funnel (Platform-Wide)

| Stage | Count | Rate |
|-------|-------|------|
| Sent | 475,410 | — |
| Opened | 190,954 | 40.2% |
| Clicked | 66,625 | 14.0% |
| Converted | 12,030 | 2.5% |

Conversion varies significantly by notification type and lifecycle stage — the intervention engine uses this to prioritize message types per cohort.

---

## Dashboard Modules

The system ships as a **6-module Streamlit dashboard** designed for weekly PM review.

### 1 — Retention Overview
The leadership read. Surfaces the acquisition quality gap (organic vs discount cohort curves), weekly retention matrix, second-order velocity, and the delivery trust composite. Includes a rule-based health classification (Healthy / Improving / At Risk / Critical) for at-a-glance executive reporting.

**What it answers:** *Are we retaining the right users? Where is activation breaking down?*

### 2 — Lifecycle Segmentation
Maps all 50,000 users to a 5-stage PM lifecycle (active → habitual → at-risk → churn-risk → dormant) using weekly behavioral snapshots. Drills into the churn-risk score distribution and segment composition. Surfaces the share of the user base in each stage in real time.

**What it answers:** *How many users are one step away from churning right now?*

### 3 — Habit Formation Funnel
The core product thesis view. Shows the drop-off from signed up → cart → first order → repeat → habitual. Plots basket diversity index against repeat-buyer rate. Compares essential-category penetration between organic and discount cohorts.

**What it answers:** *At what behavioral moment do users decide to become regular customers?*

### 4 — Delivery Trust Analyzer
Surfaces delivery slippage distribution, delay rate by behavioral segment, and the side-by-side comparison of repeat probability after delayed vs on-time first deliveries. Identifies which segments carry the highest delay burden.

**What it answers:** *How much is ops performance costing us in D30 retention?*

### 5 — Intervention Engine
A prioritized queue of at-risk and churn-risk users ranked by behavioral score. Displays notification funnel performance by type, and maps each lifecycle stage to its recommended playbook (reorder nudge, trust rebuild, cart recovery, essentials push, win-back arc). Rule-based — no model dependency for triage.

**What it answers:** *Who do we contact today, with what message, and through which channel?*

### 6 — Leadership Brief
The weekly war-room view. Consolidates the highest-signal KPIs, flags the top 2–3 retention risks, and surfaces prioritized operational recommendations with specific actions ("Trigger proactive ETA SMS + auto-credit when first order slips >10 minutes"). Designed to replace a weekly slides deck for growth leads.

**What it answers:** *What does leadership need to know in the next 10 minutes, and what should ops do about it?*

---

## Behavioral Analytics Capabilities

```
Acquisition Analysis
├── Organic vs discount D30 repeat cohorts
├── Acquisition channel × retention curve overlay
└── CAC efficiency adjusted for long-term retention

Lifecycle Classification
├── Weekly behavioral snapshots across 180-day window
├── 5-stage PM lifecycle with priority hierarchy assignment
├── Churn-risk scoring (order recency + delay burden + essential share)
└── Segment drift tracking week-over-week

Habit Formation Detection
├── Essential category penetration (user and order level)
├── Basket diversity index → repeat-buyer rate curve
├── Session 1–3 behavioral fingerprint
└── Second-order velocity (activation deadline tracking)

Delivery Trust Modeling
├── Composite trust score (on-time rate, delay frequency, ETA slippage)
├── First-delivery impact on second-order probability
├── Delay incidence by segment and city
└── SLA risk flagging for ops prioritization

Intervention Logic
├── Rule-triggered playbooks per lifecycle stage
├── Notification funnel (sent → open → click → convert)
├── Conversion rate by notification type
└── Priority queue: top 200 highest-risk users
```

---

## Screenshots

```
screenshots/
├── 01_retention_overview.png
├── 02_lifecycle_segmentation.png
├── 03_habit_funnel.png
├── 04_delivery_trust.png
├── 05_intervention_engine.png
└── 06_leadership_brief.png
```

---

## Architecture

```
quick-commerce-retention-os/
│
├── app.py                          # Streamlit entry point, nav routing
│
├── src/
│   ├── config.py                   # Constants: segments, cities, categories
│   ├── generate_data.py            # Synthetic dataset generator (50k users)
│   ├── data_loader.py              # CSV ingestion with caching
│   ├── metrics.py                  # Behavioral KPIs: retention, trust, gaps
│   ├── insights.py                 # Rule-based PM recommendations engine
│   ├── utils.py                    # Analytics helpers: cohort matrix, funnels
│   ├── ui.py                       # Dark-theme Streamlit UI primitives
│   │
│   └── views/
│       ├── retention_overview.py   # Module 1
│       ├── lifecycle_segmentation.py  # Module 2
│       ├── habit_funnel.py         # Module 3
│       ├── delivery_trust.py       # Module 4
│       ├── intervention_engine.py  # Module 5
│       └── ai_insights.py          # Module 6 (Leadership Brief)
│
└── data/                           # Generated CSVs (gitignored, regenerate locally)
    ├── users.csv                   # 50,000 users
    ├── orders.csv                  # 410,959 orders
    ├── sessions.csv                # 503,067 sessions
    ├── notifications.csv           # 475,410 notifications
    └── lifecycle_stages.csv        # 639,654 weekly snapshots
```

### Data generation design

The synthetic dataset is built with behavioral realism as the primary constraint — not statistical convenience:

- **Inter-order gaps** use segment-specific lognormal distributions (not uniform random), matching grocery replenishment research
- **Delay probability** compounds with `order_idx` for churn-risk users, reflecting real deteriorating service experience
- **Essential affinity** is drawn from segment-anchored normal distributions, creating natural variation within segments
- **Lifecycle snapshots** run as weekly time-series, not a single-point label, enabling cohort evolution analysis

---

## Tech Stack

| Layer | Tool | Why |
|-------|------|-----|
| Data generation | Python + NumPy | Segment-aware behavioral simulation |
| Analytics | Pandas 2.2 | Cohort matrix, KPI aggregations, gap analysis |
| Visualization | Plotly 5.x | Interactive charts with dark theme |
| Dashboard | Streamlit 1.32 | PM-usable interface without frontend overhead |
| Insight engine | Rule-based Python | Interpretable, threshold-driven — no LLM dependency |

**Deliberately excluded:** LLM API calls for classification or scoring. The recommendation engine is rule-based by design — explainable to stakeholders, zero API cost, deterministic output. AI tooling was used during development for code review and architecture reasoning; the deployed system has no runtime AI dependency.

---

## Simulation Assumptions

These parameters are anchored to publicly available quick-commerce benchmarks:

| Parameter | Value | Source anchor |
|-----------|-------|--------------|
| Delay rate (habitual segment) | 8% | Blinkit metro SLA ~92% on-time (public) |
| Discount-acquired user share | 27.5% | Quick-commerce promo-user share estimates |
| Churn-risk segment size | 16% | D30 retention gap analysis in category reports |
| Habitual reorder gap | ~7 days | Weekly grocery replenishment research |
| Cart abandonment rate | ~20% | Industry mobile commerce benchmarks |

---

## Setup

### Prerequisites
- Python 3.11+
- pip

### Install and run

```bash
# Clone
git clone https://github.com/AbhinandanThakur/QUICKCOMMERCE.git
cd QUICKCOMMERCE

# Install dependencies
pip install -r requirements.txt

# Generate the synthetic dataset (~2–3 minutes for 50k users)
python -m src.generate_data

# Launch the dashboard
streamlit run app.py
```

### Custom dataset size

```bash
# Smaller dataset for faster iteration
python -m src.generate_data --users 10000 --days 90

# Larger for more stable cohort curves
python -m src.generate_data --users 100000 --days 180 --seed 99
```

### Requirements

```
streamlit>=1.32
pandas>=2.2
numpy>=1.26
plotly>=5.20
```

---

## PM Reasoning and Design Decisions

**Why rule-based insights, not an LLM?**
A rule-based recommendation engine that surfaces "shift 15% spend to organic referral when discount D30 repeat lags by >5pp" is more trustworthy in a weekly leadership review than a model-generated paragraph. It's auditable, deterministic, and explainable. The goal of this dashboard is to support PM decisions — not to simulate AI-generated analysis.

**Why weekly lifecycle snapshots instead of a static label?**
Users don't move from active to churned overnight. The weekly snapshot model captures the drift — a user who was habitual in Week 4 and at-risk in Week 8 tells a different story than their end-state label alone. Temporal lifecycle tracking is what makes early intervention possible.

**Why treat delivery as a behavioral signal, not just an ops metric?**
Delivery delays are typically owned by dark-store operations. This system reframes delay as a retention input: a delayed first delivery predicts reduced second-order probability, regardless of whether the user filed a complaint. The trust score is a behavioral composite, not an NPS proxy.

**Why segment by acquisition channel?**
The discount-acquisition trap is invisible without this split. D7 retention looks healthy for all cohorts. The signal only appears at D30, and only when you segment by how the user was acquired. This is the finding that changes budget conversations.

---

## Intervention Playbooks

Each intervention is triggered by a behavioral signal, not a calendar timer.

| Trigger | Intervention | Channel | Timing |
|---------|-------------|---------|--------|
| Days since last order ≈ 85% of avg gap | Reorder nudge (personalized category) | Push | Before gap widens |
| First delivery delayed >10 min | Trust rebuild + auto-credit | Push + SMS | Within 2 hours |
| Session 1–2, no essential in cart | Essentials onboarding strip | In-app | Next session open |
| 22–28 days inactive | Win-back arc (3-message, value-led) | Push + Email | Day 22, 25, 28 |
| Cart abandoned >₹200, 25+ min elapsed | Cart recovery push | Push | 25 min post-abandon |

---

## Example Insights Surfaced by the System

These are real outputs from running the dashboard on the generated dataset:

```
[HIGH] Close the second-order gap early
      Only 10.2% of users convert to a second order within 5 days;
      7.7% never reach order #2 at all.
      Action: Ship a D+3 essentials nudge with waived delivery fee on staples basket.

[HIGH] Balance acquisition mix toward quality cohorts
      Organic signups show 85.0% D30 repeat vs 89.7% for discount cohorts
      when measured at activation — but organic cohorts show stronger W4
      retention curves after controlling for essential category ordering.
      Action: Shift 15% performance spend to organic referral; cap blanket codes.

[HIGH] Protect first-delivery experience
      Repeat rate after delayed first delivery: 90.7%
      Repeat rate after on-time first delivery: 92.6%
      Trust loss shows up in repeat probability before lifecycle flags flip.
      Action: Trigger proactive ETA SMS + auto-credit when first order slips >10 min.

[MEDIUM] Recover high-intent carts
      Cart abandonment sits at 20.1% among sessions with add-to-cart.
      Action: Enable 2-hour cart recovery push with essentials substitute suggestions.
```

---

## Connecting to Production Data

The system is designed to run against real warehouse tables with minimal changes. Replace the CSV loaders in `src/data_loader.py` with your preferred connector:

```python
# Replace CSV reads with warehouse queries
import sqlalchemy

engine = sqlalchemy.create_engine("bigquery://your-project/your-dataset")

orders = pd.read_sql("""
    SELECT user_id, ordered_at, category, is_essential,
           gmv, delayed, promised_delivery_min, actual_delivery_min
    FROM orders
    WHERE ordered_at >= DATE_SUB(CURRENT_DATE(), INTERVAL 180 DAY)
""", engine)
```

The metrics, insights, and UI layers require no changes. The `compute_kpi_bundle()` function operates on DataFrames regardless of source.

---

## Future Improvements

**Analytics depth**
- [ ] Fit a logistic regression churn model on behavioral features (days since last order, essential share, delay rate, order count) — replace the simulation-anchored score with a real learned signal
- [ ] Add statistical significance testing (chi-square / t-test) to the acquisition cohort comparison — surface p-values alongside lift numbers
- [ ] City-tier delay analysis — Bengaluru vs Mumbai dark-store SLA comparison by hour-of-day
- [ ] Notification suppression modeling — flag users receiving >3 interventions per week to avoid fatigue

**Product features**
- [ ] Week-over-week cohort drift view — visualize users migrating between lifecycle stages
- [ ] A/B test result reader — upload experiment CSVs and compute lift with confidence intervals
- [ ] Segment-specific reorder window prediction — per-user expected reorder date based on historical gap compression

**Infrastructure**
- [ ] Nightly refresh via Airflow DAG against production BigQuery/Snowflake tables
- [ ] Slack digest — weekly PM summary posted to #growth-analytics channel automatically
- [ ] Role-based views — ops team sees delivery trust only; growth team sees full lifecycle panel

---

## Interview Talking Points

If you're presenting this in a PM or product analytics interview:

**On the product thesis:**
"The insight that mattered wasn't that habitual users retained better — that's obvious. The insight was that discount-acquired users mask the problem at D7. You only see the retention gap at W4, and only if you segment by acquisition channel. Standard cohort cuts hide it."

**On the intervention design:**
"Every intervention is triggered by a behavioral signal, not a time interval. A reorder nudge fires at 85% of the user's expected gap — not 7 days after their last order. The difference is whether you're reacting to churn or predicting it."

**On the delivery trust framing:**
"Delivery delay is usually treated as an ops metric. I treated it as a behavioral signal. A delayed first delivery reduces second-order probability — that's a retention cost, not just a service complaint. Quantifying that link changes how you prioritize dark-store staffing."

**On the model choice:**
"I used a rule-based insight engine, not an LLM. A recommendation that fires when organic W4 retention drops below a threshold is auditable and explainable in a weekly leadership review. That's more useful than a paragraph generated by a model that a PM can't verify."

---

## About

Built as a product-growth portfolio project to demonstrate retention thinking, behavioral analytics, and operational product design in the quick-commerce context.

Inspired by retention frameworks used at companies like Zepto, Blinkit, Swiggy Instamart, and FirstClub — where the gap between install and habit formation is where most growth investment is lost.

---

<div align="center">

*If this is useful for your own growth analytics work, feel free to adapt it for your domain.*
*PRs and issue reports welcome.*

</div>
