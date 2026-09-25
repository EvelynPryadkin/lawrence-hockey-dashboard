# Data plan for a coaches and players dashboard

## What is ready now

The current dataset contains 25 completed 2025–26 games: 13 home and 12 away. Each game has a date, opponent, location, goals, shots on goal, both teams' power-play goals and opportunities, and a source box-score URL.

This supports a useful team review dashboard now: recent results, goals and shot trends, goal and shot differential, shooting percentage, power-play and penalty-kill rates, rolling team performance, and home/away or opponent comparisons. Show the number of games and opportunities behind each comparison, and make each game's source accessible.

Scores and shots describe team outcomes. Individual contributions, ice time, line combinations, shot quality, and expected goals are not in this dataset. Team shots on goal should not be labeled possession or shot attempts.

## Priority 1: official results and individual contributions

- **Game identity and outcomes:** add a stable `game_id`, `opponent_id`, `competition_type` (conference, nonconference, exhibition, or postseason), `official_result` (W, L, or T as published), `finish_type` (regulation, overtime, or shootout), `overtime_periods`, and `shootout_winner` (team ID, blank when not applicable). If standings points are needed, also collect the official `standings_points` and the relevant season's scoring rules. Keep statistical goals separate from shootout results; do not infer every official result or standings point from score alone.
- **Roster:** collect stable player IDs, names, jersey numbers, positions, and season. This makes names consistent across games and enables clear player cards.
- **Player game statistics:** collect appearances, goals, assists, shots on goal, penalty minutes, and power-play goals from public box scores or team-authorized exports. These unlock scoring leaders, individual game logs, and recent performance views. An appearance row is distinct from an omitted player or missing box score.
- **Goalie game statistics:** separately collect goalie ID, game ID, seconds played, shots faced, saves, goals allowed, and source URL. Goalie save percentage and goals-against average require goalie statistics; team goals against may include empty-net goals.

Minimal skater game CSV, with one row per player appearance:

```csv
game_id,player_id,goals,assists,shots_on_goal,penalty_minutes,power_play_goals,source_url
```

Join dates, opponents, and locations through `game_id`, and names, numbers, and positions through the season roster. Derive points as goals plus assists. Leave unknown statistics blank and display them as unavailable; use zero only when the source confirms zero. Validate uniqueness on `(game_id, player_id)` and retain the source for every row. Penalty minutes may be fractional if the source records seconds.

## Priority 2: context for coaching decisions

- **Previous seasons:** collect the same game fields and inclusion rules for at least one earlier season. Compare rates over equivalent samples and show games played alongside totals.
- **Conference context:** collect comparable team season totals, conference membership, and a source/update date. Identify whether each comparison uses all games or conference games. Calculate rates from summed counts rather than averaging percentages.
- **Upcoming schedule:** add scheduled date/time, time zone, opponent, venue, home/away, and schedule status. Keep upcoming games separate from completed games with statistics so they do not become zero-score results.
- **Period and game-state breakdowns:** period scoring and shots, and even-strength/power-play/short-handed splits, would show when performance changes. Individual ice time or shift data would be needed before showing per-60 player rates or line analysis; neither is currently available.

## Priority 3: optional detailed analysis

Shot maps need event-level records: `game_id`, `event_id`, `period`, `elapsed_seconds_in_period`, `team_id`, optional `player_id`, `event_type`, `x`, `y`, `strength_state`, and `source_url`. Define whether the feed includes goals, saves, misses, and blocks so shots on goal and all attempts remain distinct.

For coordinates, record rink dimensions, units, origin, axis directions, and the attacking direction for each team and period. Preserve raw coordinates and normalize attacking direction only for display or analysis. This prevents maps from silently mixing opposite rink ends.

Expected goals would require a documented model and suitable event inputs, potentially including shot type and preceding events. Coordinates alone do not supply an xG value, and current game totals cannot support an xG chart. Add these features only when a suitable public or team-authorized feed is available.

## Visual assets

An approved Lawrence logo, official color values, and a high-resolution team or hockey action photo can strengthen the dashboard immediately. Roster headshots and opponent logos are optional additions for player and matchup views. New statistics are not required for a cleaner layout, typography, charts, or navigation.

## Reconcile before extending

The collection log in [sources.md](sources.md) records an unresolved opponent power-play denominator: individual box scores total 92 opportunities while the team summary reports 91. The dashboard uses 92, yielding 76.1% PK, and should retain its source note until this is resolved.

The source player table also includes a duplicate player row and shot totals that differ from the team tables. Reconcile player records before publishing leaderboards. Check goalie totals separately for empty-net goals, preserve source links, and continue showing missing values explicitly. A CSV export or links to the relevant official tables are sufficient to begin the next data collection step.
