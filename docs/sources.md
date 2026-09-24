# Sources and collection log

Collected with Python by the project assistant on 2026-09-24, from public Lawrence Athletics HTML tables. This dataset contains all 25 completed games listed for 2025–26, with 13 home and 12 away games. No synthetic records are included.

- Season statistics: https://vikings.lawrence.edu/sports/womens-ice-hockey/stats/?path=whockey
- Season schedule: https://vikings.lawrence.edu/sports/womens-ice-hockey/schedule/2025-26
- Individual box-score URLs: `source_url` in each row of `data/raw/games.csv`.

## Collection method

Dates, opponents, locations, goals, and shots come from the Lawrence and Opponents game-by-game tables. Records were joined by game date. The season schedule provides canonical box-score URLs. Both teams' power-play goals and opportunities come from each box score's Power Plays table totals, identified by team abbreviation rather than table order. Power-play goals were cross-checked against the game-by-game tables for every game.

Dates were converted to ISO format. Opponent names were trimmed, the `at` prefix was converted to `away`, and unprefixed games were marked `home` using the Lawrence-perspective table. The ranking prefix was removed from Augsburg. `Aurora University` and `Aurora` were standardized to `Aurora`. No player-level records were imported.

## Reconciliation

| Statistic | Sum of collected games | Published team summary | Result |
| --- | ---: | ---: | --- |
| Games | 25 | 25 | Matches |
| Lawrence goals | 21 | 21 | Matches |
| Opponent goals | 93 | 93 | Matches |
| Lawrence shots | 378 | 378 | Matches |
| Opponent shots | 949 | 949 | Matches |
| Lawrence power-play goals | 5 | 5 | Matches |
| Lawrence power-play opportunities | 78 | 78 | Matches |
| Opponent power-play goals | 22 | 22 | Matches |
| Opponent power-play opportunities | 92 | 91 | Unresolved source discrepancy |

The dataset retains 92 opponent opportunities from the individual box scores. It does not silently subtract an opportunity to force agreement. Therefore the full-season penalty-kill rate is 76.1% (1 − 22/92), versus 75.8% using the summary denominator. Which source needs correction remains unconfirmed. The dashboard displays this limitation. Resolve against an authoritative corrected report before claiming full special-teams reconciliation.

The individual skater table also repeats Sophia Labrecque's row and reports 396 total shots. The team summary and game-by-game tables report 378. This project uses team game-level statistics, not the duplicated player table. The goalie game-by-game GA column also differs from game scores in some empty-net games; goals against were taken from team scores, not that goalie column.

## Checks performed

- Exactly 25 unique date/opponent records; no missing required fields.
- Nonnegative integer counts and valid date/location/source formats.
- Goals do not exceed shots; power-play goals do not exceed opportunities or total goals.
- All 25 box-score power-play goal counts match the game-level tables.
- CSV successfully passed `src.prepare_data` and generated the SQLite database.

This is a snapshot. The website may revise its historical records or change its default season later.
