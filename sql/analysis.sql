-- Run after python -m src.prepare_data.
-- sqlite3 -header -column data/processed/hockey.db < sql/analysis.sql

-- Home/away/neutral comparison, separated by season.
SELECT season, location, COUNT(*) AS games,
       ROUND(AVG(goals_for), 2) AS goals_per_game,
       ROUND(AVG(goals_against), 2) AS goals_allowed_per_game,
       ROUND(AVG(shots_for), 2) AS shots_per_game,
       ROUND(100.0 * SUM(goals_for) / NULLIF(SUM(shots_for), 0), 2) AS shooting_pct
FROM games GROUP BY season, location ORDER BY season, location;

-- Special teams. A zero denominator returns NULL, not a misleading zero.
SELECT season,
       ROUND(100.0 * SUM(pp_goals) / NULLIF(SUM(pp_opportunities), 0), 2) AS power_play_pct,
       ROUND(100.0 * (1.0 - 1.0 * SUM(opponent_pp_goals) /
             NULLIF(SUM(opponent_pp_opportunities), 0)), 2) AS penalty_kill_pct
FROM games GROUP BY season;

-- Opponent comparison: report game counts alongside averages.
SELECT season, opponent, COUNT(*) AS games,
       ROUND(AVG(shots_for), 2) AS shots_per_game,
       ROUND(AVG(goals_for - goals_against), 2) AS average_goal_difference
FROM games GROUP BY season, opponent ORDER BY season, average_goal_difference DESC;
