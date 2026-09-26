# Run the project

The data is already included: 138 games across six seasons. You can start by exploring the dashboard, then follow a result back to its calculation and original box score.

## Set up Python

Open the project folder in VS Code and choose **Terminal → New Terminal**. Python 3.12 is a good choice for a new environment.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Activate `.venv` again when you open a new terminal. If you use the VS Code Python extension, select `.venv` as the interpreter.

## Open the dashboard

```bash
python -m src.prepare_data
python -m streamlit run app.py
```

Open the local URL printed in the terminal. Try **All seasons** with all venues, all opponents, and all games selected. The totals should show 138 games, 135 Lawrence goals, and 2,453 Lawrence shots. Power play and penalty kill show N/A for this selection because historical opportunity counts are incomplete.

Choose a single season or opponent to narrow the view. In **Game review**, open an original box score and compare it with the displayed statistics. Control-C stops the server.

## Check a finding

```bash
python -m src.run_analysis
```

This regenerates the saved CSV results in `docs/analysis/` from the validated raw records. Read [findings.md](findings.md) alongside [sql-guide.md](sql-guide.md). Pick a result and explain the numerator, denominator, sample size, and limitation in your own words.

You can also run the SQL directly against the generated database:

```bash
sqlite3 -header -column data/processed/hockey.db < sql/analysis.sql
```

## Update the data

Read [data-dictionary.md](data-dictionary.md) before editing `data/raw/games.csv`. Each row is one game. Keep opponent names consistent and preserve the source URL. Only the two opportunity fields may be blank; zero is a known count, not a substitute for missing data.

After making a verified correction:

```bash
python -m src.prepare_data
python -m src.run_analysis
python -m unittest discover -s tests -v
```

Update the source log and any findings affected by the correction. Refresh the running dashboard. Generated databases are ignored by Git; the saved analysis evidence is tracked so a reader can inspect it without running Python.

## Share the project

The [walkthrough video](media/dashboard-walkthrough.mp4) can be sent as a file. Open `docs/walkthrough.html` in a browser for the video and step-by-step screenshots. See [deployment.md](deployment.md) for live hosting and [portfolio-notes.md](portfolio-notes.md) for résumé wording and interview practice.
