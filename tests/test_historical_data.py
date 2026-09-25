"""Run with python -m unittest discover -s tests."""
import sqlite3
import unittest
from pathlib import Path
import pandas as pd
from src.prepare_data import clean_games, RAW
from src.metrics import special_teams_rate


class HistoricalDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.games = clean_games(pd.read_csv(RAW))

    def test_archive_coverage_and_goals_shots(self):
        expected = {
            "2020-21": (9, 9, 70, 164, 568),
            "2021-22": (23, 17, 157, 305, 1251),
            "2022-23": (27, 21, 150, 538, 1299),
            "2023-24": (27, 30, 105, 576, 1087),
            "2024-25": (27, 37, 105, 492, 1079),
            "2025-26": (25, 21, 93, 378, 949),
        }
        self.assertEqual(set(self.games.season), set(expected))
        for season, (count, *totals) in expected.items():
            frame = self.games[self.games.season == season]
            self.assertEqual(len(frame), count)
            self.assertEqual(frame[["goals_for", "goals_against", "shots_for", "shots_against"]].sum().tolist(), totals)

    def test_missing_opportunities_stay_null_in_sqlite(self):
        with sqlite3.connect(":memory:") as connection:
            self.games.to_sql("games", connection, index=False)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM games WHERE pp_opportunities IS NULL").fetchone()[0], 22)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM games WHERE opponent_pp_opportunities IS NULL").fetchone()[0], 22)
            sql = (Path(__file__).resolve().parents[1] / "sql/analysis.sql").read_text()
            for query in sql.split(";"):
                if query.strip():
                    results = connection.execute(query).fetchall()
                    if "AS power_play_pct" in query:
                        seasons = {r[0]: r for r in results}
                        self.assertIsNone(seasons["2020-21"][-2])
                        self.assertIsNone(seasons["2020-21"][-1])
                        self.assertAlmostEqual(seasons["2025-26"][-2], 6.41)

    def test_missing_and_zero_rates(self):
        self.assertEqual(special_teams_rate(self.games, "pp_goals", "pp_opportunities"), "N/A")
        frame = pd.DataFrame({"goals": [1, 1], "opportunities": [2, 8]})
        self.assertEqual(special_teams_rate(frame, "goals", "opportunities"), "20.0%")
        self.assertEqual(special_teams_rate(frame, "goals", "opportunities", True), "80.0%")
        frame.loc[1, "opportunities"] = float("nan")
        self.assertEqual(special_teams_rate(frame, "goals", "opportunities"), "N/A")
        self.assertEqual(special_teams_rate(pd.DataFrame({"goals": [0], "opportunities": [0]}), "goals", "opportunities"), "N/A")

    def test_invalid_and_duplicate_records_rejected(self):
        with self.assertRaises(ValueError):
            clean_games(pd.concat([self.games, self.games.iloc[:1]]))
        invalid = self.games.copy()
        invalid.loc[0, "shots_for"] = -1
        with self.assertRaises(ValueError):
            clean_games(invalid)
        invalid = self.games.copy()
        invalid.loc[0, "goals_for"] = pd.NA
        with self.assertRaises(ValueError):
            clean_games(invalid)


if __name__ == "__main__":
    unittest.main()
