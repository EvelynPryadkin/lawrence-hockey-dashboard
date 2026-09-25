# Data dictionary

One row = one completed game, from Lawrence's perspective. Seasons 2020–21 through 2025–26 are included.

| Column | Format / meaning |
| --- | --- |
| date | YYYY-MM-DD |
| season | Text, e.g. 2025-26 |
| opponent | Consistent official opponent name |
| location | home, away, or neutral |
| goals_for | Lawrence official statistical goals |
| goals_against | Opponent official statistical goals |
| shots_for | Lawrence shots on goal, not all shot attempts |
| shots_against | Opponent shots on goal |
| pp_goals | Lawrence power-play goals |
| pp_opportunities | Lawrence power-play opportunities |
| opponent_pp_goals | Opponent power-play goals |
| opponent_pp_opportunities | Opponent power-play opportunities |
| source_url | HTTPS link to the public box score |

Count fields must be nonnegative integers when present. Only `pp_opportunities` and `opponent_pp_opportunities` may be blank; these become SQL NULL. All other fields are required. Exclude exhibitions or document an explicit inclusion policy before collecting. Verify shootout conventions separately: shootout attempts are not regular goals or shots in this dataset.

## Calculations

- Goals per game = summed goals / game count.
- Shooting percentage = 100 × summed goals / summed shots on goal.
- Power-play percentage = 100 × summed power-play goals / summed opportunities.
- Penalty-kill percentage = 100 × (1 − summed opponent power-play goals / summed opponent opportunities).
- Goal difference = goals for − goals against.

Never average game-level percentages to calculate a season rate. Zero opportunities/shots produce N/A, not 0%. A missing opportunity count in any selected game makes the corresponding aggregate rate N/A (SQL NULL). Check game counts and totals against the official cumulative report before publishing a completed-season analysis.
