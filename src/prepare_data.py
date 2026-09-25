"""Validate the raw CSV, then export clean data and a SQLite database.

Run from the project root: python -m src.prepare_data
"""
from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/games.csv"
OUTPUT = ROOT / "data/processed"
COUNTS = ["goals_for", "goals_against", "shots_for", "shots_against",
          "pp_goals", "pp_opportunities", "opponent_pp_goals",
          "opponent_pp_opportunities"]
COLUMNS = ["date", "season", "opponent", "location", *COUNTS, "source_url"]
OPTIONAL_COUNTS = {"pp_opportunities", "opponent_pp_opportunities"}


def clean_games(frame):
    """Reject questionable records rather than quietly changing statistics."""
    missing = set(COLUMNS) - set(frame.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    df = frame[COLUMNS].copy()
    if df.empty:
        raise ValueError("No games yet. Add verified game rows to data/raw/games.csv first.")
    for col in ["date", "season", "opponent", "location", "source_url"]:
        df[col] = df[col].astype("string").str.strip()
        if (df[col].isna() | df[col].eq("")).any():
            raise ValueError(f"Missing {col}; check the source box score.")
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="raise").dt.strftime("%Y-%m-%d")
    df["location"] = df["location"].str.lower()
    if not df["location"].isin(["home", "away", "neutral"]).all():
        raise ValueError("Location must be home, away, or neutral.")
    if not df["source_url"].str.startswith("https://").all():
        raise ValueError("Each game needs an https:// source URL.")
    if df.duplicated(["season", "date", "opponent"]).any():
        raise ValueError("Duplicate season/date/opponent found; resolve before importing.")
    for col in COUNTS:
        values = pd.to_numeric(df[col], errors="raise")
        present = values.dropna()
        if (col not in OPTIONAL_COUNTS and values.isna().any()) or (present < 0).any() or (present % 1 != 0).any():
            raise ValueError(f"{col} must contain nonnegative whole numbers; only opportunity counts may be blank.")
        df[col] = values.astype("Int64")
    for smaller, larger in [("goals_for", "shots_for"), ("goals_against", "shots_against"),
                            ("pp_goals", "pp_opportunities"), ("pp_goals", "goals_for"),
                            ("opponent_pp_goals", "opponent_pp_opportunities"),
                            ("opponent_pp_goals", "goals_against")]:
        if (df[smaller] > df[larger]).any():
            raise ValueError(f"{smaller} cannot exceed {larger}.")
    return df.sort_values(["date", "opponent"]).reset_index(drop=True)


def main():
    try:
        games = clean_games(pd.read_csv(RAW))
    except (ValueError, TypeError) as error:
        raise SystemExit(f"Data check failed: {error}") from error
    OUTPUT.mkdir(parents=True, exist_ok=True)
    games.to_csv(OUTPUT / "games_clean.csv", index=False)
    with sqlite3.connect(OUTPUT / "hockey.db") as connection:
        games.to_sql("games", connection, if_exists="replace", index=False)
    print(f"Saved {len(games)} validated games to CSV and SQLite.")


if __name__ == "__main__":
    main()
