# SQL behind the analysis

The database has one table, `games`, with one row per game. These questions can be answered directly from that table, so the queries do not need joins. [The data dictionary](data-dictionary.md) defines each field.

From the project root, with the project environment activated, run:

```bash
python -m src.run_analysis
```

This validates `data/raw/games.csv`, loads it into a temporary SQLite database, runs every named query in [analysis.sql](../sql/analysis.sql), and saves the results in [docs/analysis](analysis). It also writes a manifest with the input and SQL hashes. The result files are part of the portfolio so someone can inspect the numbers without running the app. Empty result cells mean SQL NULL, not zero.

To run the same SQL against the dashboard database instead:

```bash
python -m src.prepare_data
sqlite3 -header -column data/processed/hockey.db < sql/analysis.sql
```

## Season and venue: `season_venue_comparison`

Groups by season and location, keeping neutral-site games separate. Counts, goals, and shots sit next to the averages so the sample behind each comparison is visible. Shooting percentage divides summed goals by summed shots; it does not average game percentages.

Check the 2025–26 rows: home has 13 games, 10 goals, and 195 shots; away has 12 games, 11 goals, and 183 shots. The home and away goals-per-game values are 0.77 and 0.92. Across all seasons there are 13 result rows, including the single 2024–25 neutral-site group.

## Special teams: `special_teams_coverage`

Counts how many games have each opportunity field and shows the underlying goals and known opportunities. `CASE` only calculates a rate when every game in that season has its denominator. `NULLIF` returns NULL for a zero total denominator. These checks are independent for Lawrence and its opponents.

Check 2025–26: 5/78 produces 6.41% on the power play, and `1 − 22/92` produces 76.09% penalty kill. The 2024–25 power-play percentage is NULL because only 26 of 27 games have Lawrence's opportunities. Its penalty kill is 82.61% because the opponent counts are complete. Known opportunity sums in incomplete seasons are partial totals, not estimates of the season totals. Read [the source conflicts](sources.md#reconciliation-and-unresolved-conflicts) before interpreting the results.

## Opponents: `opponent_comparison`

Groups by season and opponent and includes home, away, and neutral game counts. It calculates shots per game and average goal difference from Lawrence's perspective. Negative goal difference means Lawrence was outscored on average in that group.

The 2025–26 Adrian row has two home games and no away games; Trine has two away games and no home games. This is why a venue split alone does not isolate a home effect. Small opponent groups should be read as descriptions of those games, not a ranking of future matchups.

## Season changes: `season_over_season`

The first common table expression (CTE) builds season totals and unrounded rates. The second uses `LAG` to bring the previous available season's values onto each row. The final SELECT calculates changes and rounds the result for display.

The 2025–26 row should show 0.84 goals per game, a change of −0.53 and −38.70%, alongside 15.12 shots per game, a change of −3.10 and −17.02%. Shooting percentage changes by −1.96 percentage points. Comparing per-game rates accounts for 25 games versus 27; it does not adjust for schedule strength. A percentage change is `(current / previous − 1) × 100`; a percentage-point change subtracts two percentages.

The first season has NULL changes because there is no earlier season. A prior rate of zero also produces NULL for relative percentage change. `LAG` refers to the previous season present in the data, which matters if a future dataset skips a season.

## Five-game trends: `rolling_five_games`

The window partitions by season and orders games by date, then opponent. `ROWS BETWEEN 4 PRECEDING AND CURRENT ROW` uses the current game and four earlier games. It never includes a later game or carries results from one season into the next. `games_in_window` shows the available count; the first four games in each season have NULL five-game rates because there is not yet a full window.

For 2025–26, the first full window ends on November 8, 2025. Those five games total two goals and 68 shots: 0.40 goals per game, 13.60 shots per game, and 2.94% shooting. At the sixth game, the first game drops out of the calculation. The final window, ending February 14, 2026, contains three goals and 88 shots: 0.60 goals per game and 17.60 shots per game.

The shooting percentage again uses summed goals and shots in the window. Overlapping windows share four games, so adjacent points are not independent observations. This is a way to choose stretches for closer review, not a forecast or a test of whether performance has changed.
