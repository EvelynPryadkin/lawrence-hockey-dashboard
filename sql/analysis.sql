-- Run after python -m src.prepare_data.
-- sqlite3 -header -column data/processed/hockey.db < sql/analysis.sql

-- name: season_venue_comparison
-- Home/away/neutral comparison, separated by season.
SELECT season, location, COUNT(*) AS games,
       SUM(goals_for) AS goals, SUM(shots_for) AS shots,
       ROUND(AVG(goals_for), 2) AS goals_per_game,
       ROUND(AVG(goals_against), 2) AS goals_allowed_per_game,
       ROUND(AVG(shots_for), 2) AS shots_per_game,
       ROUND(100.0 * SUM(goals_for) / NULLIF(SUM(shots_for), 0), 2) AS shooting_pct
FROM games GROUP BY season, location ORDER BY season, location;

-- name: special_teams_coverage
-- Special teams. Missing opportunities or a zero denominator return NULL.
SELECT season,
       COUNT(*) AS games,
       COUNT(pp_opportunities) AS games_with_power_play_opportunities,
       COUNT(opponent_pp_opportunities) AS games_with_opponent_opportunities,
       SUM(pp_goals) AS power_play_goals,
       SUM(pp_opportunities) AS known_power_play_opportunities,
       SUM(opponent_pp_goals) AS opponent_power_play_goals,
       SUM(opponent_pp_opportunities) AS known_opponent_opportunities,
       CASE WHEN COUNT(pp_opportunities) = COUNT(*)
            THEN ROUND(100.0 * SUM(pp_goals) / NULLIF(SUM(pp_opportunities), 0), 2)
       END AS power_play_pct,
       CASE WHEN COUNT(opponent_pp_opportunities) = COUNT(*)
            THEN ROUND(100.0 * (1.0 - 1.0 * SUM(opponent_pp_goals) /
                 NULLIF(SUM(opponent_pp_opportunities), 0)), 2)
       END AS penalty_kill_pct
FROM games GROUP BY season ORDER BY season;

-- name: opponent_comparison
-- Opponent comparison: report game counts alongside averages.
SELECT season, opponent, COUNT(*) AS games,
       SUM(CASE WHEN location = 'home' THEN 1 ELSE 0 END) AS home_games,
       SUM(CASE WHEN location = 'away' THEN 1 ELSE 0 END) AS away_games,
       SUM(CASE WHEN location = 'neutral' THEN 1 ELSE 0 END) AS neutral_games,
       ROUND(AVG(shots_for), 2) AS shots_per_game,
       ROUND(AVG(goals_for - goals_against), 2) AS average_goal_difference
FROM games GROUP BY season, opponent ORDER BY season, average_goal_difference DESC;

-- name: season_over_season
-- Compare rates before rounding so different schedule lengths remain comparable.
-- LAG means the previous available season in this archive.
WITH season_totals AS (
    SELECT season, COUNT(*) AS games,
           SUM(goals_for) AS goals, SUM(shots_for) AS shots,
           AVG(goals_for) AS goals_per_game,
           AVG(shots_for) AS shots_per_game,
           100.0 * SUM(goals_for) / NULLIF(SUM(shots_for), 0) AS shooting_pct
    FROM games
    GROUP BY season
), prior_season AS (
    SELECT *,
           LAG(season) OVER (ORDER BY season) AS previous_season,
           LAG(goals_per_game) OVER (ORDER BY season) AS previous_goals_per_game,
           LAG(shots_per_game) OVER (ORDER BY season) AS previous_shots_per_game,
           LAG(shooting_pct) OVER (ORDER BY season) AS previous_shooting_pct
    FROM season_totals
)
SELECT season, previous_season, games, goals, shots,
       ROUND(goals_per_game, 2) AS goals_per_game,
       ROUND(shots_per_game, 2) AS shots_per_game,
       ROUND(shooting_pct, 2) AS shooting_pct,
       ROUND(goals_per_game - previous_goals_per_game, 2) AS goals_per_game_change,
       ROUND(100.0 * (goals_per_game / NULLIF(previous_goals_per_game, 0) - 1), 2)
           AS goals_per_game_change_pct,
       ROUND(shots_per_game - previous_shots_per_game, 2) AS shots_per_game_change,
       ROUND(100.0 * (shots_per_game / NULLIF(previous_shots_per_game, 0) - 1), 2)
           AS shots_per_game_change_pct,
       ROUND(shooting_pct - previous_shooting_pct, 2) AS shooting_pct_change_pp
FROM prior_season
ORDER BY season;

-- name: rolling_five_games
-- Current game and four previous games, without crossing season boundaries.
-- The first four games keep their window count but have no five-game rate yet.
WITH recent_games AS (
    SELECT season, date, opponent, location, goals_for, shots_for,
           COUNT(*) OVER recent AS games_in_window,
           SUM(goals_for) OVER recent AS window_goals,
           SUM(shots_for) OVER recent AS window_shots
    FROM games
    WINDOW recent AS (
        PARTITION BY season ORDER BY date, opponent
        ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
    )
)
SELECT season, date, opponent, location, goals_for, shots_for, games_in_window,
       CASE WHEN games_in_window = 5
            THEN ROUND(1.0 * window_goals / games_in_window, 2)
       END AS rolling_goals_per_game,
       CASE WHEN games_in_window = 5
            THEN ROUND(1.0 * window_shots / games_in_window, 2)
       END AS rolling_shots_per_game,
       CASE WHEN games_in_window = 5
            THEN ROUND(100.0 * window_goals / NULLIF(window_shots, 0), 2)
       END AS rolling_shooting_pct
FROM recent_games
ORDER BY season, date, opponent;
