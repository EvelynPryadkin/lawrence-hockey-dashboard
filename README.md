# Lawrence Women's Ice Hockey Analytics

An independent project using 138 games from six seasons, 2020–21 through 2025–26. It brings scoring, shots, and special teams into one dashboard, with a link back to each game's box score.

**Python · pandas · SQL / SQLite · Streamlit · Plotly**

[Watch the 36-second walkthrough](docs/media/dashboard-walkthrough.mp4) · [Read the findings](docs/findings.md) · [See the SQL](sql/analysis.sql)

![Dashboard preview](docs/dashboard-preview.png)

## What the data shows

- **Scoring fell in 2025–26.** Lawrence went from 37 goals in 27 games to 21 in 25 games. Goals per game fell from 1.37 to 0.84. Shot volume and shooting percentage both declined.
- **Home and away results were close in the latest season.** Lawrence averaged 0.77 goals at home across 13 games and 0.92 away across 12. The opponents differed, so this does not establish an effect of venue.
- **Special-teams comparisons need coverage checks.** Using the collected box scores, penalty kill was 82.6% in 2024–25 and 76.1% in 2025–26. Both seasons have an unresolved opportunity-count discrepancy. The earlier season's power-play rate is unavailable because one game's denominator is missing.

The [full findings](docs/findings.md) include the counts behind each result, SQL evidence, and questions worth reviewing next. These are descriptions of the recorded games, not explanations of what caused the results.

## Use the dashboard

The sidebar filters by season, venue, opponent, and the most recent 5 or 10 matching games. **All seasons** combines the archive: 138 games, 135 Lawrence goals, and 2,453 Lawrence shots when the other filters include every game.

- **Team overview:** scoring and shot trends, recent games, venue comparisons, and selected-game totals.
- **Special teams:** power-play and penalty-kill rates, with the number of games that have usable opportunity counts.
- **Game review:** a team comparison for one game, its original box score, and a CSV download of the current selection.
- **Season comparison:** all six full seasons, independent of the sidebar selection.

The [walkthrough page](docs/walkthrough.html) includes the video and screenshots of each view. The video is a file you can share directly. A live Streamlit deployment has not been created yet; [deployment instructions](docs/deployment.md) are ready.

## Run it locally

Use Python 3.12 for a new environment. From the project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m src.prepare_data
python -m streamlit run app.py
```

Open the local URL printed by Streamlit. A fresh checkout also works without the generated database: the app validates the included CSV and builds a SQLite table in memory. If you already have a local database, run `python -m src.prepare_data` after changing the CSV to refresh it.

## Reproduce the analysis

```bash
python -m src.run_analysis
```

This command validates the raw CSV, runs the five named queries in [analysis.sql](sql/analysis.sql), and saves their results to [docs/analysis](docs/analysis). It also saves hashes of the source CSV and SQL so the evidence can be traced to the exact inputs. It reads the raw data directly, so an older local database cannot change the results.

The queries cover season/venue summaries, special-teams coverage, opponent comparisons, season-over-season changes using `LAG`, and rolling five-game averages. [The SQL guide](docs/sql-guide.md) explains what each query answers and how to check the output. The first four games of each season have no full five-game average; the window resets at the next season.

To run the same SQL against the generated database:

```bash
sqlite3 -header -column data/processed/hockey.db < sql/analysis.sql
```

## Data checks and limits

The preparation step rejects duplicate games, invalid dates, negative or fractional counts, missing required statistics, and impossible combinations such as more goals than shots. Goals, shots, and power-play goal totals have been checked against the archived season summaries.

23 games have at least one missing opportunity count. Those values stay NULL in SQLite. A rate shows N/A if any selected denominator is missing or the total denominator is zero. Percentages use summed goals and opportunities, rather than an average of each game's percentage.

Some published sources disagree. The [source log](docs/sources.md) explains the unresolved 2021–22, 2024–25, and 2025–26 records and the values kept in the dataset. The audit files in [data/reference](data/reference) preserve the counts and source links.

These are team game totals. They cannot measure player impact, ice time, shot quality, or coaching effectiveness. Statistical goals exclude shootout attempts; official overtime and shootout outcomes are not recorded. This is not an official Lawrence Athletics product, and no coach or player adoption is claimed.

## Tests

```bash
python -m unittest discover -s tests -v
```

Tests cover the historical totals, invalid records, missing values, SQL calculations, dashboard filters, and startup from a fresh checkout. Dependency ranges are in `requirements.txt`; they are not a lockfile.

## Project files

| File | What it does |
| --- | --- |
| `data/raw/games.csv` | Source-linked game records |
| `src/prepare_data.py` | Validation and clean CSV/SQLite exports |
| `src/dashboard_data.py` | Load a local database or validate the CSV for a fresh checkout |
| `src/metrics.py` | Special-teams rates with missing-data checks |
| `src/run_analysis.py` | Run the named SQL queries and save evidence |
| `app.py`, `assets/dashboard.css` | Dashboard and styling |
| `docs/findings.md`, `docs/sql-guide.md` | Results and explanations |
| `docs/portfolio-notes.md` | Résumé wording, interview practice, and a feedback-request draft |

The next steps are to collect coach/player feedback, finish the live hosting setup, and resolve the remaining source gaps where better records are available. Feedback and live deployment are still pending.
