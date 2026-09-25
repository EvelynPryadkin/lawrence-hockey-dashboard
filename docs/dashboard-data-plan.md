# Data plan for a coaches and players dashboard

## What is ready now

The current dataset contains 138 completed games across six seasons, 2020–21 through 2025–26. Each game has a date, opponent, location, goals, shots on goal, both teams' power-play goals, and a source box-score URL. Opportunity counts are partly missing: 23 games have at least one missing count. These remain unavailable rather than being replaced with zero.

This supports a useful team review dashboard now: recent scores, goals and shot trends, shooting percentage, special-teams rates when counts are complete, recent-game windows, venue/opponent filters, and full-season comparisons. The dashboard shows sample sizes and opportunity-data coverage and makes each game's source accessible. Goal and shot differentials can also be derived from the existing data.

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

- **Season history:** all six archived seasons are now included and available in the season-comparison view. Continue the same fields and inclusion rules as later seasons become available; filling historical opportunity gaps would improve special-teams comparisons.
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

The collection log in [sources.md](sources.md) records historical missing counts and unresolved conflicts in 2021–22, 2024–25, and 2025–26. For example, 2025–26 opponent power-play opportunities total 92 in box scores versus 91 in the summary. The dashboard uses 92, yielding 76.1% PK. Retain the notes and N/A safeguards until the gaps and conflicts are resolved.

The source player table also includes a duplicate player row and shot totals that differ from the team tables. Reconcile player records before publishing leaderboards. Check goalie totals separately for empty-net goals, preserve source links, and continue showing missing values explicitly. A CSV export or links to the relevant official tables are sufficient to begin the next data collection step.
