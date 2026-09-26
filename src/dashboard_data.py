"""Load the dashboard from a local database or the validated CSV in GitHub."""
from contextlib import closing
from pathlib import Path
import sqlite3

import pandas as pd

from src import prepare_data


def load_games(database, raw_path=None):
    """Use an existing import, or build an in-memory database on a fresh checkout."""
    database = Path(database)
    if database.exists():
        with closing(sqlite3.connect(database)) as connection:
            games = pd.read_sql_query("SELECT * FROM games ORDER BY date, opponent", connection)
    else:
        raw_path = prepare_data.RAW if raw_path is None else raw_path
        validated = prepare_data.clean_games(pd.read_csv(raw_path))
        with closing(sqlite3.connect(":memory:")) as connection:
            validated.to_sql("games", connection, index=False)
            games = pd.read_sql_query("SELECT * FROM games ORDER BY date, opponent", connection)
    games["date"] = pd.to_datetime(games["date"])
    return games
