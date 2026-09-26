"""Verify that the GitHub checkout works without an exported SQLite file."""
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import pandas as pd
from streamlit.testing.v1 import AppTest

from src.dashboard_data import load_games
from src.prepare_data import RAW, clean_games


ROOT = Path(__file__).resolve().parents[1]


class DashboardDataTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory(prefix="hockey-checkout-tests-")
        self.addCleanup(temporary.cleanup)
        self.output = Path(temporary.name) / "processed"
        self.database = self.output / "hockey.db"

    def test_fresh_checkout_preserves_all_games_counts_and_missing_values(self):
        games = load_games(self.database)
        expected = clean_games(pd.read_csv(RAW))
        expected["date"] = pd.to_datetime(expected["date"])
        pd.testing.assert_frame_equal(games, expected, check_dtype=False)
        self.assertEqual(len(games), 138)
        self.assertEqual(games.goals_for.sum(), 135)
        self.assertEqual(games.shots_for.sum(), 2453)
        self.assertEqual(games.pp_opportunities.isna().sum(), 22)
        self.assertEqual(games.opponent_pp_opportunities.isna().sum(), 22)
        self.assertFalse(self.output.exists())

    def test_existing_database_stays_the_selected_source(self):
        expected = clean_games(pd.read_csv(RAW)).tail(2)
        self.output.mkdir()
        with sqlite3.connect(self.database) as connection:
            expected.to_sql("games", connection, index=False)
        games = load_games(self.database, raw_path=self.output / "missing.csv")
        self.assertEqual(games.source_url.tolist(), expected.source_url.tolist())

    def test_fresh_checkout_dashboard_renders_archive_totals(self):
        with patch("src.prepare_data.OUTPUT", self.output):
            app = AppTest.from_file(ROOT / "app.py", default_timeout=15).run()
            season = next(item for item in app.selectbox if item.label == "Season")
            season.select("All seasons").run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.error), 0)
        totals = next(item.value for item in app.dataframe
                      if "Team" in item.value.columns).set_index("Team")
        self.assertEqual(totals.loc["Lawrence", "Goals"], 135)
        self.assertEqual(totals.loc["Lawrence", "Shots on goal"], 2453)
        self.assertEqual(totals["Power-play chances"].tolist(), ["N/A", "N/A"])
        self.assertFalse(self.output.exists())

    def test_invalid_raw_data_shows_error_instead_of_dashboard(self):
        invalid = pd.read_csv(RAW)
        invalid.loc[0, "shots_for"] = -1
        raw_path = self.output.parent / "invalid.csv"
        invalid.to_csv(raw_path, index=False)
        with patch("src.prepare_data.OUTPUT", self.output), patch("src.prepare_data.RAW", raw_path):
            app = AppTest.from_file(ROOT / "app.py", default_timeout=15).run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.error), 1)
        self.assertIn("Game data could not be loaded", app.error[0].value)
        self.assertIn("shots_for must contain nonnegative whole numbers", app.error[0].value)
        self.assertEqual(len(app.selectbox), 0)
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
