from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"

N_USERS_DEFAULT = 50_000
DAYS_DEFAULT = 180
RNG_SEED_DEFAULT = 42

DATA_FILES = {
    "users": "users.csv",
    "sessions": "sessions.csv",
    "orders": "orders.csv",
    "notifications": "notifications.csv",
    "lifecycle_stages": "lifecycle_stages.csv",
}

NAV_PAGES = [
    "Retention Overview",
    "Lifecycle Segmentation",
    "Habit Formation Funnel",
    "Delivery Trust Analyzer",
    "Intervention Engine",
    "Growth Insight Brief",
]

PM_LIFECYCLE_STAGES = ["active", "habitual", "at-risk", "churn-risk", "dormant"]

LIFECYCLE_STAGES = [
    "new",
    "activated",
    "habitual",
    "at_risk",
    "churned",
    "win_back",
]

CITIES = ["Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Pune", "Chennai", "Kolkata"]
ESSENTIAL_CATEGORIES = ["milk", "bread", "eggs", "vegetables", "fruits", "staples"]
NON_ESSENTIAL_CATEGORIES = ["snacks", "beverages", "personal_care", "household", "impulse"]
