# Lawrence Women's Ice Hockey Performance Dashboard

**Status: In development — 25 games from 2025–26 collected. One source discrepancy remains documented below.**

An independent student portfolio project analyzing public Lawrence University women's ice hockey game statistics. Not an official Lawrence Athletics product.

## Project question

How do scoring, shooting efficiency, and special-teams performance vary across games and between home and away locations?

## Stack

Python, pandas, SQLite, SQL, Streamlit, and Plotly. Work in VS Code; Excel is not required.

## Start on macOS

Open this folder in VS Code, then choose **Terminal → New Terminal**.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m src.prepare_data
python -m streamlit run app.py
```

Streamlit prints a local browser URL. The dashboard displays the included 2025–26 data after preparation. Stop it with Control-C.

To regenerate the database from the included records, run:

```bash
python -m src.prepare_data
python -m streamlit run app.py
```

See [the first-session guide](docs/getting-started.md) and [data dictionary](docs/data-dictionary.md).

## Files and their responsibilities

| Path | Purpose |
| --- | --- |
| `app.py` | Interactive dashboard; reads the SQLite database |
| `src/prepare_data.py` | Validate CSV records, sort games, write clean CSV and SQLite |
| `data/raw/games.csv` | 25 game records with individual box-score source links |
| `data/processed/` | Generated outputs; ignored by Git |
| `sql/analysis.sql` | Queries for location, special teams, and opponents |
| `docs/getting-started.md` | Beginner-friendly setup and collection workflow |
| `docs/data-dictionary.md` | Column definitions and calculation rules |
| `docs/findings.md` | Template for evidence-based findings |
| `docs/sources.md` | Source and collection log |
| `requirements.txt` | Python dependencies |
| `.streamlit/config.toml` | Dashboard colors |
| `.gitignore` | Excludes local environment, secrets, and generated outputs |

## Data flow

Verified box scores → raw CSV → Python validation → clean CSV + SQLite → SQL analysis and dashboard.

## Milestones

- [x] Create initial project scaffold.
- [ ] Set up Python and open the dashboard locally.
- [x] Collect 25 games from the 2025–26 season.
- [x] Reconcile goals, shots, and Lawrence power-play totals.
- [ ] Resolve opponent power-play opportunity discrepancy (92 across box scores; 91 in season summary).
- [ ] Run and explain each SQL query.
- [ ] Write three findings with sample sizes and limitations.
- [ ] Add a dashboard screenshot and demonstration link.

## Method and limitations

Use only public game statistics. Preserve box-score URLs and log corrections. Rates use summed numerators and denominators, not average per-game percentages. A zero denominator yields N/A (SQL NULL). Missing required statistics block import until verified; never replace unknown values with zero. For shootout games, record official team statistical goals, excluding shootout attempts; verify against cumulative totals. Do not infer causes or coaching effectiveness from simple comparisons. Different opponents and small samples can affect home/away results.

No analysis findings or deployment are included yet. See `docs/sources.md` for collection details and source discrepancies. Dependency ranges are specified but are not a lockfile.
