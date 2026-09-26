"""Rebuild the saved SQL evidence from the included CSV: python -m src.run_analysis."""
import hashlib
import json
from pathlib import Path
import re
import sqlite3

import pandas as pd

from src.prepare_data import RAW, ROOT, clean_games

SQL = ROOT / "sql/analysis.sql"
RESULTS = ROOT / "docs/analysis"


def load_queries(path):
    """Read the named statements from the project's analysis SQL file."""
    sections = re.split(r"^-- name: ([a-z][a-z0-9_]*)\s*$", Path(path).read_text(), flags=re.MULTILINE)
    queries = {}
    for name, statement in zip(sections[1::2], sections[2::2]):
        if name in queries:
            raise ValueError(f"Duplicate query name: {name}")
        queries[name] = statement.strip()
    if not queries:
        raise ValueError("No named SQL queries found.")
    return queries


def run_analysis(raw=RAW, sql_path=SQL, output=RESULTS):
    """Validate raw records, execute SQLite queries, and save their exact results."""
    raw, sql_path, output = Path(raw), Path(sql_path), Path(output)
    games = clean_games(pd.read_csv(raw))
    queries = load_queries(sql_path)
    frames = {}
    with sqlite3.connect(":memory:") as connection:
        games.to_sql("games", connection, index=False)
        for name, statement in queries.items():
            frames[name] = pd.read_sql_query(statement, connection)
    output.mkdir(parents=True, exist_ok=True)
    for name, frame in frames.items():
        frame.to_csv(output / f"{name}.csv", index=False)
    row_counts = {name: len(frame) for name, frame in frames.items()}
    manifest = {
        "raw_csv_sha256": hashlib.sha256(raw.read_bytes()).hexdigest(),
        "sql_sha256": hashlib.sha256(sql_path.read_bytes()).hexdigest(),
        "games": len(games),
        "seasons": sorted(games.season.unique().tolist()),
        "result_rows": row_counts,
        "missing_values": "Empty CSV cells represent SQL NULL, not zero.",
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return row_counts


def main():
    try:
        row_counts = run_analysis()
    except (ValueError, TypeError, sqlite3.Error) as error:
        raise SystemExit(f"Analysis failed: {error}") from error
    for name, rows in row_counts.items():
        print(f"{name}: {rows} rows")
    print(f"Saved SQL results to {RESULTS}")


if __name__ == "__main__":
    main()
