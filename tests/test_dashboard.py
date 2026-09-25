"""Exercise the historical dashboard against an isolated, freshly imported database."""
from html import unescape
from pathlib import Path
import re
import sqlite3
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import pandas as pd
from streamlit.testing.v1 import AppTest

from src.prepare_data import RAW, clean_games


ROOT = Path(__file__).resolve().parents[1]


class DashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.games = clean_games(pd.read_csv(RAW))
        temporary = TemporaryDirectory(prefix="hockey-dashboard-tests-")
        cls.addClassCleanup(temporary.cleanup)
        cls.output = Path(temporary.name)
        with sqlite3.connect(cls.output / "hockey.db") as connection:
            cls.games.to_sql("games", connection, index=False)
        output_patch = patch("src.prepare_data.OUTPUT", cls.output)
        output_patch.start()
        cls.addClassCleanup(output_patch.stop)

    def setUp(self):
        self.app = AppTest.from_file(ROOT / "app.py", default_timeout=15).run()
        self.assert_no_errors()

    def widget(self, kind, label):
        return next(item for item in getattr(self.app, kind) if item.label == label)

    def game_log(self):
        return next(item.value for item in self.app.dataframe
                    if "source_url" in item.value.columns)

    def cards(self):
        markup = "\n".join(item.value for item in self.app.markdown)
        values = re.findall(
            r'class="stat-label">([^<]+)</div>\s*<div class="stat-value">([^<]+)</div>',
            markup,
        )
        return {unescape(label): unescape(value) for label, value in values}

    def assert_no_errors(self):
        self.assertEqual(len(self.app.exception), 0,
                         [error.message for error in self.app.exception])
        text = []
        for kind in ("markdown", "caption", "info", "warning", "metric"):
            text.extend(str(item.value) for item in getattr(self.app, kind))
        for item in self.app.dataframe:
            strings = item.value.select_dtypes(include=["object", "string"])
            text.extend(str(value) for value in strings.to_numpy().ravel())
        self.assertNotRegex("\n".join(text), r"(?i)(?<!\w)(?:nan|<NA>)(?!\w)")

    def test_every_season_renders_all_imported_games_and_correct_rates(self):
        expected = {
            "2020-21": (9, "N/A", "N/A"),
            "2021-22": (23, "N/A", "N/A"),
            "2022-23": (27, "N/A", "N/A"),
            "2023-24": (27, "N/A", "N/A"),
            "2024-25": (27, "N/A", "82.6%"),
            "2025-26": (25, "6.4%", "76.1%"),
        }
        self.assertEqual(set(self.widget("selectbox", "Season").options), set(expected))
        for season, (count, power_play, penalty_kill) in expected.items():
            with self.subTest(season=season):
                self.widget("selectbox", "Season").select(season).run()
                self.assert_no_errors()
                log = self.game_log()
                self.assertEqual(len(log), count)
                self.assertEqual(set(log.source_url),
                                 set(self.games.loc[self.games.season.eq(season), "source_url"]))
                self.assertEqual(self.cards()["Power play"], power_play)
                self.assertEqual(self.cards()["Penalty kill"], penalty_kill)
                self.assertEqual([item.value for item in self.app.metric
                                  if item.label == "Success rate"], [power_play, penalty_kill])

    def test_individual_game_with_missing_opportunities_is_readable(self):
        self.widget("selectbox", "Season").select("2020-21").run()
        missing = self.games.loc[
            self.games.season.eq("2020-21") & self.games.pp_opportunities.isna()
        ].iloc[0]
        game_index = missing.name
        self.widget("selectbox", "Game").select(game_index).run()
        self.assert_no_errors()
        comparison = next(item.value for item in self.app.dataframe
                          if "Statistic" in item.value.columns).set_index("Statistic")
        for team in ("Lawrence", "Opponent"):
            self.assertIn("N/A", comparison.loc["Power play", team])
            self.assertEqual(comparison.loc["Penalty kill", team], "N/A")
        log = self.game_log()
        self.assertIn("N/A", log.loc[log.source_url.eq(missing.source_url), "power_play"].iloc[0])

        # Every Marian game that season lacks counts, so neither chart has data.
        self.widget("multiselect", "Opponents").set_value(["Marian (WI)"]).run()
        self.assert_no_errors()
        self.assertEqual(len(self.game_log()), 2)
        self.assertEqual(self.cards()["Power play"], "N/A")
        self.assertEqual(self.cards()["Penalty kill"], "N/A")
        self.assertEqual(sum("No recorded opportunity counts" in item.value
                             for item in self.app.info), 2)

    def test_season_comparison_keeps_full_archive_under_sidebar_filters(self):
        summary = next(item.value for item in self.app.dataframe
                       if "pp_coverage" in item.value.columns)
        self.assertEqual(len(summary), 6)
        self.assertEqual(summary.games.sum(), 138)
        historical = summary.set_index("season").loc["2024-25"]
        self.assertEqual(historical.pp_coverage, "26 / 27")
        self.assertEqual(historical.pk_coverage, "27 / 27")
        self.assertEqual(historical.power_play, "N/A")
        self.assertEqual(historical.penalty_kill, "82.6%")

        self.widget("radio", "Venue").set_value("Away").run()
        self.widget("selectbox", "Game window").select("Last 5 games").run()
        self.assert_no_errors()
        self.assertEqual(len(self.game_log()), 5)
        filtered_summary = next(item.value for item in self.app.dataframe
                                if "pp_coverage" in item.value.columns)
        pd.testing.assert_frame_equal(filtered_summary, summary)

    def test_filters_recover_from_empty_selection_and_keep_latest_matching_games(self):
        self.widget("radio", "Venue").set_value("Neutral").run()
        self.assert_no_errors()
        self.assertTrue(any("No games match" in item.value for item in self.app.info))
        self.widget("radio", "Venue").set_value("All").run()
        self.assert_no_errors()
        self.assertEqual(len(self.game_log()), 25)

        self.widget("radio", "Venue").set_value("Away").run()
        self.widget("selectbox", "Game window").select("Last 5 games").run()
        self.assert_no_errors()
        expected = self.games.loc[
            self.games.season.eq("2025-26") & self.games.location.eq("away")
        ].tail(5)
        self.assertEqual(set(self.game_log().source_url), set(expected.source_url))

        self.widget("multiselect", "Opponents").set_value(["MSOE"]).run()
        self.assert_no_errors()
        expected = self.games.loc[
            self.games.season.eq("2025-26") & self.games.location.eq("away")
            & self.games.opponent.eq("MSOE")
        ].tail(5)
        self.assertEqual(set(self.game_log().source_url), set(expected.source_url))


if __name__ == "__main__":
    unittest.main()
