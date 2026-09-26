# Portfolio notes

## Résumé entry

**Lawrence Women's Ice Hockey Analytics Dashboard — Independent Project**

Python · pandas · SQL / SQLite · Streamlit · Plotly

- Developed an interactive dashboard for 138 games across six seasons, with filters for season, opponent, venue, and recent games to explore scoring, shooting, and special teams.
- Built a CSV-to-SQLite data pipeline with duplicate checks, statistical validation, and automated tests; reconciled goals and shots against published season totals and documented missing values and source conflicts.

Add an accessible GitHub or demo link beside the title once it is ready. For now, you can share the [walkthrough video](media/dashboard-walkthrough.mp4) as a file. Adjust the wording to match the work you can explain in an interview.

## One-minute walkthrough

Use this as a starting point for a recording or an interview. Open the dashboard before you begin.

> This project looks at Lawrence women's hockey across 138 games and six seasons. I wanted someone to be able to move from a season overview to a specific game without digging through separate box scores.
>
> Here I can select a season, compare home and away games, or choose All seasons for the full archive. The scoring and shooting charts show how performance changes, and Game review links back to the original box score.
>
> The data work is a big part of the project. Python checks the CSV before loading it into SQLite. Some historical power-play counts are missing, so those rates show N/A. I also calculate percentages from total goals and opportunities, which keeps games with different opportunity counts weighted correctly.
>
> The analysis describes patterns, but it doesn't explain their causes. My next step is getting feedback from a coach or player about which comparisons would help them review games.

## Interview practice

**How does the data get into the dashboard?**

Each CSV row represents one game and includes its source URL. `src/prepare_data.py` checks required fields, dates, duplicate season/date/opponent records, and nonnegative whole-number counts. It also catches impossible combinations, such as more goals than shots. pandas writes the validated rows to a clean CSV and a SQLite `games` table. The Streamlit app reads SQLite, applies filters, and builds the charts with Plotly. Rebuilding replaces the table, so an updated CSV becomes the next complete snapshot.

**Why keep missing values instead of replacing them with zero?**

Zero opportunities means the team had no power plays. A blank means the count is unknown. Treating an unknown count as zero would understate the denominator and could inflate the rate. Only the two opportunity columns may be blank; those values stay NULL in SQLite. If any selected game is missing a required opportunity count, its aggregate special-teams rate is unavailable. A known zero total denominator also gives N/A.

**Why not average the percentages from each game?**

That would give every game equal weight even when the opportunities differ. For example, scoring once in two opportunities is 50%, and once in eight is 12.5%. Averaging those percentages gives 31.25%, but the combined result is two goals in ten opportunities: 20%. The dashboard divides summed goals by summed opportunities.

**Where does SQL add value here?**

`GROUP BY` summarizes records by season, venue, or opponent. `LAG` compares a season's metric with the previous available season. A window ordered by game date calculates a moving five-game average while keeping each game as a row. It resets at each season. The first four games show their window counts but have no full five-game average yet. These queries let me reproduce a result independently of the dashboard.

**What do you do when two sources disagree?**

I keep the discrepancy visible and document which value the project uses. For 2025–26, individual box scores total 92 opponent power-play opportunities, while the season summary lists 91. Using 92 gives a 76.1% penalty-kill rate; using 91 gives 75.8%. The dashboard uses the box-score counts and shows a source note. Agreement with a season total is a useful check, but it doesn't settle every conflicting record.

**What is a finding you would discuss?**

Choose one result from [the findings](findings.md). State the comparison, game counts, and actual numbers before interpreting it. Be ready to reproduce it with `sql/analysis.sql`. Explain what the result suggests reviewing next and what the available data cannot establish. Avoid memorizing a claim without understanding the calculation.

**What can't this dataset tell you?**

It has team game totals, so it cannot measure individual player impact, line combinations, shot quality, or time on ice. Opponents and schedules change between seasons, so a trend is not evidence that a coaching decision caused it. Historical special-teams coverage is incomplete. Shootout attempts are excluded from statistical goals, and official overtime/shootout outcomes are not recorded, so I do not reconstruct an official win–loss record from these scores.

**How would you improve it next?**

First I would ask a coach or player which question they need answered and watch them use the dashboard. Then I would choose the next feature around that feedback. Player statistics would support individual game review; shot locations would support rink maps. Those additions need new data rather than a different chart of the existing totals.

## Coach or player feedback

**Status: pending.** This is a draft to send yourself. No feedback has been collected or claimed.

> Hi [name], I've been working on a dashboard using public Lawrence women's hockey stats. It lets you compare seasons, filter games, and review scoring and special teams. Would you have five minutes to try it and tell me what would make it useful for game review? Here's the link: [dashboard or walkthrough link].
>
> 1. What's one question you usually want answered after a game?
> 2. Can you find a game or comparison you care about? What was confusing or missing?
> 3. If I could add one thing, what would be most useful?

When someone responds, record the date, their role, the task they tried, what they said, and the change you made. Ask before naming or quoting them publicly. Keep the résumé focused on completed work until there is actual feedback or use to report.
