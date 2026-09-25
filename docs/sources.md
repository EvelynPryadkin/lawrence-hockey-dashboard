# Sources, coverage, and data quality

Collected with Python by the project assistant on 2026-09-25 from Lawrence Athletics public HTML tables, with PDF checks for missing historical fields. The 2025–26 records were first collected on 2026-09-24 and retained in this expansion.

## Coverage

All six seasons offered by the statistics archive are included: **138 games, 2020–21 through 2025–26**. This means all completed games listed in those season statistics, including listed postseason games. It does not mean every field in every game is complete. Cancelled games and future fixtures are excluded. No player-level or synthetic data is included.

| Season | Games | Home | Away | Neutral | Missing Lawrence PP opportunities | Missing opponent PP opportunities |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2020-21 | 9 | 4 | 5 | 0 | 5 | 5 |
| 2021-22 | 23 | 11 | 12 | 0 | 13 | 13 |
| 2022-23 | 27 | 10 | 17 | 0 | 1 | 1 |
| 2023-24 | 27 | 12 | 15 | 0 | 2 | 3 |
| 2024-25 | 27 | 9 | 17 | 1 | 1 | 0 |
| 2025-26 | 25 | 13 | 12 | 0 | 0 | 0 |

There are 23 games with at least one missing opportunity field. Each opportunity column has 22 missing values; these counts overlap. Goals, shots, and power-play goals are populated for every game. The single neutral-site game is retained as `neutral`, not `home`.

## Source pages

- [2020-21](https://vikings.lawrence.edu/sports/womens-ice-hockey/stats/2020-21)
- [2021-22](https://vikings.lawrence.edu/sports/womens-ice-hockey/stats/2021-22)
- [2022-23](https://vikings.lawrence.edu/sports/womens-ice-hockey/stats/2022-23)
- [2023-24](https://vikings.lawrence.edu/sports/womens-ice-hockey/stats/2023-24)
- [2024-25](https://vikings.lawrence.edu/sports/womens-ice-hockey/stats/2024-25)
- [2025-26](https://vikings.lawrence.edu/sports/womens-ice-hockey/stats/2025-26)

Canonical box-score URLs are in `data/raw/games.csv` (`source_url`). Each season's schedule, at the same season-specific `/schedule/YYYY-YY` route, supplied those links. `data/reference/season_audit.json` contains the published team totals, dataset totals, missing-field counts, source URLs, and access date. `data/reference/data_quality_issues.json` lists each missing opportunity field and the conflicting 2021–22 goal record with its source.

## Collection and cleaning

1. Read each season's Lawrence and Opponents game-by-game tables and join records by game date within the season.
2. Use team game-level goals, shots, and power-play goals. Do not sum the player or goalie tables to reconstruct team totals.
3. Follow schedule box-score links and read each Power Plays table's goals/opportunities total. Identify Lawrence by its abbreviation (LAW, LU, LWR, LWU, LUV, LAWRENCE, or L U), not by table order. Treat each team's availability independently.
4. Check linked PDFs when historical power-play tables are empty. Available older PDFs also omit the needed totals in the unresolved cases; some PDF document links have no downloadable asset. No opportunities were inferred from penalties, leftover season totals, or missing table rows.
5. Convert dates to YYYY-MM-DD. Read `at` as away and `vs` as neutral in the Lawrence game table; unprefixed opponents are home. Strip ranking and location prefixes.
6. Standardize aliases across seasons: Adrian College → Adrian; Aurora University → Aurora; Finlandia University → Finlandia; Lake Forest College → Lake Forest; Marian University/Marian → Marian (WI); St. Norbert College → St. Norbert; Trine University → Trine; UW-Stevens Point → Wis.-Stevens Point; University of Dubuque → Dubuque.

## Reconciliation and unresolved conflicts

For **all six seasons**, sums of game-level goals, shots, and power-play goals match the published team summary totals. See the audit JSON for exact numbers.

- **2021–22, January 28 vs Finlandia:** the season game table lists zero Lawrence power-play goals, while the box score's Power Plays total lists one. The dataset retains the season game-table value. This is unresolved; matching season totals alone does not establish that either source is correct.
- **2024–25:** known Lawrence box-score opportunities sum to **74**, with one game still missing, versus **72** in the season summary. Opponent opportunities are complete and sum to **92**, versus **91** in the summary. Keep the observed box-score counts. Full-season Lawrence PP% is N/A because one denominator is missing; penalty kill is **82.6%** using 16/92, compared with **82.4%** using 16/91.
- **2025–26:** opponent opportunities total **92** across box scores versus **91** in the summary. The dashboard retains 92: penalty kill is **76.1%**, compared with **75.8%** using the summary. All other tracked 2025–26 totals match.
- In other seasons, opportunity sums cover only games where the field is available. Do not compare a partial sum to a full-season denominator as though they had the same coverage.
- The 2025–26 skater table duplicates Sophia Labrecque and reports 396 shots; the team summary and game table report 378. The dataset uses the team game table. Some goalie game-table goals-against entries also conflict with team scores; this project uses team scores.

## Missing-value rules

An empty CSV opportunity field becomes SQL NULL. It is never converted to zero. Only the two opportunity columns allow missing values. All other fields remain required.

If any selected game's opportunity count is missing, the corresponding dashboard rate shows **N/A**, and the SQL query returns **NULL**. This avoids mixing a full set of goals with a partial denominator. Coverage counts are shown. Selecting a subset with complete counts enables its rate; a zero total denominator still yields N/A. Rates always divide summed numerators by summed denominators, rather than averaging per-game rates. Source conflict warnings remain visible for affected seasons.

## Validation

- 138 unique season/date/opponent records and 138 unique source URLs.
- Published goals and shots reconciled for every season.
- Nonnegative integer counts and valid date/location/source fields.
- Known power-play goals do not exceed known opportunities or total goals.
- CSV imports into SQLite with missing values preserved as NULL.
- Regression tests cover season counts, source control totals, missing and zero denominators, invalid records, and SQL/Python rate behavior.

Run `python -m unittest discover -s tests -v`. Records are a historical snapshot; the website may revise them later. No claim of complete special-teams reconciliation is made.
