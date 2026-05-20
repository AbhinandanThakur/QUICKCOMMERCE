from pathlib import Path

import pandas as pd
import streamlit as st

from src.config import DATA_DIR, DATA_FILES

DATE_COLUMNS = {
    "users": ["signup_at"],
    "sessions": ["session_start"],
    "orders": ["ordered_at"],
    "notifications": ["sent_at"],
    "lifecycle_stages": ["observed_at"],
}


def data_paths(data_dir: Path | None = None) -> dict[str, Path]:
    base = data_dir or DATA_DIR
    return {name: base / filename for name, filename in DATA_FILES.items()}


def datasets_available(data_dir: Path | None = None) -> bool:
    return all(path.exists() for path in data_paths(data_dir).values())


@st.cache_data(show_spinner="Loading datasets...")
def load_datasets(data_dir: str | None = None) -> dict[str, pd.DataFrame]:
    base = Path(data_dir) if data_dir else DATA_DIR
    loaded: dict[str, pd.DataFrame] = {}
    for name, path in data_paths(base).items():
        if not path.exists():
            raise FileNotFoundError(f"Missing {path}. Run: python -m src.generate_data")
        parse_dates = DATE_COLUMNS.get(name, [])
        loaded[name] = pd.read_csv(path, parse_dates=parse_dates)
    return loaded
