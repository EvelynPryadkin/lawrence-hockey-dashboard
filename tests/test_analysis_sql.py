"""Check that SQL trends use the intended games and rate denominators."""
import sqlite3
import unittest

import pandas as pd

from src.run_analysis import SQL, load_queries


class AnalysisSQLTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.queries = load_queries(SQL)

    def query(self, name, rows):
        with sqlite3.connect(":memory:") as connection:
            pd.DataFrame(rows).to_sql("games", connection, index=False)
            return pd.read_sql_query(self.queries[name], connection)

    def season_rows(self, season, goals, shots):
        return [
            {"season": season, "date": f"{season[:4]}-11-{day:02d}",
             "opponent": "Test opponent", "location": "home",
             "goals_for": goal, "shots_for": shot}
            for day, (goal, shot) in enumerate(zip(goals, shots), start=1)
        ]

    def test_rolling_window_resets_each_season_and_drops_oldest_game(self):
        rows = self.season_rows("2023-24", [1, 2, 3, 4, 5, 6], [10, 20, 30, 40, 50, 60])
        rows += self.season_rows("2024-25", [0, 1, 0, 0, 0, 0], [1, 2, 3, 4, 5, 6])
        # Reverse input order so chronology must come from the SQL window.
        result = self.query("rolling_five_games", rows[::-1])
        for _, season in result.groupby("season"):
            self.assertEqual(season.games_in_window.tolist(), [1, 2, 3, 4, 5, 5])
            self.assertTrue(season.iloc[:4].rolling_goals_per_game.isna().all())
            self.assertTrue(season.iloc[:4].rolling_shots_per_game.isna().all())
        first = result[result.season == "2023-24"].reset_index(drop=True)
        self.assertEqual(first.loc[4, "rolling_goals_per_game"], 3)
        self.assertEqual(first.loc[5, "rolling_goals_per_game"], 4)
        latest = result[result.season == "2024-25"].reset_index(drop=True)
        self.assertEqual(latest.loc[4, "rolling_goals_per_game"], 0.2)
        self.assertEqual(latest.loc[4, "rolling_shots_per_game"], 3)
        # 1 goal / 15 shots, not the average of individual game percentages.
        self.assertEqual(latest.loc[4, "rolling_shooting_pct"], 6.67)
        self.assertEqual(latest.loc[5, "rolling_shots_per_game"], 4)
        self.assertEqual(latest.loc[5, "rolling_shooting_pct"], 5)

    def test_season_changes_compare_unrounded_per_game_rates(self):
        rows = self.season_rows("2023-24", [1, 2, 4], [10, 20, 40])
        rows += self.season_rows("2024-25", [1, 1], [10, 10])
        result = self.query("season_over_season", rows[::-1]).set_index("season")
        self.assertTrue(pd.isna(result.loc["2023-24", "goals_per_game_change_pct"]))
        latest = result.loc["2024-25"]
        self.assertEqual(latest.previous_season, "2023-24")
        self.assertEqual(latest.goals_per_game_change, -1.33)
        # Compare 1 with 7/3, not with rounded 2.33 or total seven goals.
        self.assertEqual(latest.goals_per_game_change_pct, -57.14)
        self.assertEqual(latest.shots_per_game_change_pct, -57.14)
        self.assertEqual(latest.shooting_pct_change_pp, 0)

    def test_zero_prior_rates_leave_relative_changes_null(self):
        rows = self.season_rows("2023-24", [0], [0])
        rows += self.season_rows("2024-25", [1], [2])
        result = self.query("season_over_season", rows).set_index("season")
        latest = result.loc["2024-25"]
        self.assertEqual(latest.goals_per_game_change, 1)
        self.assertEqual(latest.shots_per_game_change, 2)
        self.assertTrue(pd.isna(latest.goals_per_game_change_pct))
        self.assertTrue(pd.isna(latest.shots_per_game_change_pct))
        self.assertTrue(pd.isna(latest.shooting_pct_change_pp))


if __name__ == "__main__":
    unittest.main()
