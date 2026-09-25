# Your first session in VS Code

**Data is now included:** 138 games across 2020–21 through 2025–26 are in `data/raw/games.csv`. After installing dependencies, run `python -m src.prepare_data` before starting Streamlit. The collection steps below explain how to review or extend the dataset. See `sources.md` for missing values and unresolved power-play discrepancies.

## 1. Open the project

Unzip the download if needed. In VS Code choose File → Open Folder and select `lawrence-hockey-dashboard`. Open Terminal → New Terminal. The terminal should be inside the folder containing `app.py`.

## 2. Create your Python environment

Use Python 3.11 or newer. On macOS:

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

The `.venv` folder keeps this project's packages separate. When opening a new terminal later, run `source .venv/bin/activate` again. If using the VS Code Python extension, select `.venv` as the interpreter.

## 3. Open your dashboard

```bash
python -m streamlit run app.py
```

Open the local URL printed in the terminal. An empty-data message means you need to run the preparation command first. Control-C stops the server; it does not delete your work.

## 4. Collect five real games

Open the official statistics page linked in `sources.md`; select 2025–26 if the default season changed. Open each game's box score. Edit `data/raw/games.csv` directly in VS Code: one line per game, with values in the header's exact order. Read `data-dictionary.md` first. CSV is a text format; no Excel is required. Put text containing a comma in double quotes.

Record counts from Lawrence's perspective, even for away games. Keep one opponent spelling throughout. Use YYYY-MM-DD dates and lowercase home/away/neutral. Record each game's source URL. Do not use zero for unavailable data. Only the two opportunity columns may be blank when the source omits them. Such blanks become NULL and the affected rates show N/A; other fields must be verified before import.

## 5. Prepare the data

```bash
python -m src.prepare_data
```

If a validation error appears, inspect the raw row and its source. Successful preparation creates `data/processed/games_clean.csv` and `data/processed/hockey.db`. Rerun after changing the raw data; refreshing the dashboard alone will not import changes.

## 6. Analyze and document

With the SQLite command-line tool installed, run:

```bash
sqlite3 -header -column data/processed/hockey.db < sql/analysis.sql
```

Alternatively open `hockey.db` with a SQLite viewer and paste queries from `sql/analysis.sql`. Explain one query in your own words, then write one supported finding in `docs/findings.md`. Collect the rest of the season after validating these first five games.

## 7. Commit meaningful progress

Use VS Code's Source Control view to review changed files, stage the relevant ones, and commit. Suggested milestones: initial scaffold; first five verified games; season validation; findings and screenshot. Never commit `.venv`, credentials, or secrets.
