"""Coach-focused team dashboard. Run: python -m streamlit run app.py"""
from html import escape
from pathlib import Path
import sqlite3

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.prepare_data import OUTPUT
from src.metrics import special_teams_rate
from src.dashboard_data import load_games

BLUE, SLATE, TEAL = "#2563EB", "#7C8DA8", "#087F8C"
LOCATION_ORDER = ["home", "away", "neutral"]
SOURCE_NOTES = {
    "2021-22": "January 28 vs Finlandia: the season game table lists zero Lawrence power-play goals; "
               "the box score lists one. The dataset retains the season game-table value. This conflict is unresolved.",
    "2024-25": "Known Lawrence power-play opportunities total 74, with one game missing, versus 72 in the season summary. "
               "Opponent opportunities total 92 versus 91. Box-score counts are retained; full-season power play is N/A "
               "and penalty kill is 82.6% (versus 82.4% using the summary).",
    "2025-26": "Opponent power-play opportunities total 92 across individual box scores, versus 91 in the season summary. "
               "Box-score counts are retained; full-season penalty kill is 76.1% (versus 75.8% using the summary).",
}
st.set_page_config(page_title="Lawrence | Hockey Analytics", page_icon="🏒", layout="wide")
st.markdown(f"<style>{(Path(__file__).parent / 'assets/dashboard.css').read_text()}</style>", unsafe_allow_html=True)


def percentage(numerator, denominator, complement=False):
    if pd.isna(numerator) or pd.isna(denominator) or denominator == 0:
        return "N/A"
    value = numerator / denominator
    return f"{100 * (1 - value if complement else value):.1f}%"


def count(value):
    return "N/A" if pd.isna(value) else str(int(value))


def opportunity_detail(frame, goals, opportunities, complement=False):
    missing = int(frame[opportunities].isna().sum())
    if missing:
        return f"Chance counts missing in {missing} of {len(frame)} games"
    suffix = "goals allowed" if complement else "goals"
    return f"{count(frame[goals].sum())} {suffix} / {count(frame[opportunities].sum())} chances"


def metric(label, value, detail):
    st.markdown(
        f'<div class="stat-card"><div class="stat-label">{escape(label)}</div>'
        f'<div class="stat-value">{escape(str(value))}</div>'
        f'<div class="stat-detail">{escape(detail)}</div></div>', unsafe_allow_html=True)


def style_chart(fig, y_title, height=310):
    fig.update_layout(
        height=height, margin=dict(l=8, r=16, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial, sans-serif", color="#52617A", size=12),
        legend=dict(orientation="h", y=1.16, x=0, title=None),
        hoverlabel=dict(bgcolor="#132842", font_color="white"),
        xaxis=dict(title=None, showgrid=False, zeroline=False, automargin=True),
        yaxis=dict(title=y_title, gridcolor="#E9EEF5", zeroline=False,
                   rangemode="tozero", automargin=True))
    st.plotly_chart(fig, use_container_width=True, theme=None,
                    config={"displayModeBar": False, "responsive": True})


def trend_chart(frame, columns, names, y_title):
    fig = go.Figure()
    for column, name, color, dash in zip(columns, names, [BLUE, SLATE], ["solid", "dash"]):
        for index, (_, season_frame) in enumerate(frame.groupby("season", sort=True)):
            fig.add_trace(go.Scatter(
                x=season_frame["date"], y=season_frame[column], name=name, mode="lines+markers",
                legendgroup=name, showlegend=index == 0,
                line=dict(color=color, width=3, dash=dash), marker=dict(size=7),
                customdata=season_frame[["opponent", "location", "season"]].values,
                hovertemplate=("%{x|%b %d, %Y}<br>%{customdata[0]} · %{customdata[1]}"
                               f"<br>Season %{{customdata[2]}}<br>{name}: %{{y}}<extra></extra>")))
    fig.update_xaxes(type="date", tickformat="%b %Y" if frame.season.nunique() > 1 else "%b %d", nticks=7)
    style_chart(fig, y_title)


database = OUTPUT / "hockey.db"
try:
    all_games = load_games(database)
except (OSError, ValueError, TypeError, sqlite3.Error, pd.errors.DatabaseError) as error:
    st.title("Lawrence Hockey Analytics")
    st.error(f"Game data could not be loaded: {error}")
    st.caption("Check data/raw/games.csv and run python -m src.prepare_data after correcting it.")
    st.stop()
if all_games.empty:
    st.info("No games have been imported yet. Run python -m src.prepare_data to load the data.")
    st.stop()

with st.sidebar:
    st.markdown('<div class="sidebar-brand"><span class="brand-mark">LH</span>'
                '<div>LAWRENCE<span>HOCKEY ANALYTICS</span></div></div>', unsafe_allow_html=True)
    st.caption("Women's ice hockey · Team performance")
    st.caption(f"{len(all_games)} games · {all_games.season.nunique()} seasons in the archive")
    st.divider()
    st.markdown("#### Your game selection")
    seasons = sorted(all_games["season"].unique(), reverse=True)
    season = st.selectbox("Season", ["All seasons", *seasons], index=1)
    season_games = all_games if season == "All seasons" else all_games[all_games["season"] == season]
    location = st.radio("Venue", ["All", "Home", "Away", "Neutral"], horizontal=True)
    opponents = st.multiselect("Opponents", sorted(season_games["opponent"].unique()), placeholder="All opponents")
    window = st.selectbox("Game window", ["All games", "Last 5 games", "Last 10 games"])
    st.caption("The game window uses the most recent games that match your season, venue, and opponents.")
    st.divider()
    st.markdown('<div class="sidebar-note"><strong>Built for game review</strong>'
                '<p>Follow scoring, shot volume, and special teams. Open a game to see the details.</p>'
                '</div>', unsafe_allow_html=True)
    st.caption("Independent student project. Not an official Lawrence Athletics product.")

games = season_games.copy()
if location != "All":
    games = games[games["location"] == location.lower()]
if opponents:
    games = games[games["opponent"].isin(opponents)]
if window != "All games":
    games = games.tail(5 if window == "Last 5 games" else 10)
if games.empty:
    st.title("Team performance")
    st.info("No games match this selection. Try another venue or opponent in the sidebar.")
    st.stop()

totals = games.select_dtypes(include="number").sum()
home_count = int(games["location"].eq("home").sum())
away_count = int(games["location"].eq("away").sum())
neutral_count = int(games["location"].eq("neutral").sum())
venue_summary = f"{home_count} home · {away_count} away"
if neutral_count:
    venue_summary += f" · {neutral_count} neutral"
date_range = f"{games.date.min():%b %d, %Y} – {games.date.max():%b %d, %Y}"
latest = games.iloc[-1]
st.markdown(
    '<div class="hero"><div class="hero-copy">'
    f'<div class="eyebrow">LAWRENCE WOMEN’S ICE HOCKEY <span>{escape(season)}</span></div>'
    '<h1>Every game. A clearer picture.</h1>'
    '<p>Your team’s performance, from the season view to the final shot.</p>'
    f'<div class="hero-meta"><b>{len(games)} games selected</b><span>{venue_summary}</span>'
    f'<span>{date_range}</span></div></div>'
    '<div class="hero-game"><div class="eyebrow">LATEST IN SELECTION</div>'
    f'<div class="hero-game-date">{latest.date:%b %d, %Y} · {escape(latest.location.title())}</div>'
    f'<div class="score-line"><span>Lawrence</span><strong>{latest.goals_for}</strong></div>'
    f'<div class="score-line"><span>{escape(latest.opponent)}</span><strong>{latest.goals_against}</strong></div>'
    '<div class="hero-game-note">Team statistical score · excludes shootout attempts</div>'
    '</div></div>', unsafe_allow_html=True)

st.markdown('<div class="section-kicker">PERFORMANCE SNAPSHOT <span>Current selection</span></div>', unsafe_allow_html=True)
stats = [
    ("Goals / game", f"{games.goals_for.mean():.2f}", f"{count(totals.goals_for)} goals in {len(games)} games"),
    ("Shots / game", f"{games.shots_for.mean():.1f}", f"{count(totals.shots_for)} shots on goal"),
    ("Shooting", percentage(totals.goals_for, totals.shots_for), "Goals ÷ shots on goal"),
    ("Power play", special_teams_rate(games, "pp_goals", "pp_opportunities"),
     opportunity_detail(games, "pp_goals", "pp_opportunities")),
    ("Penalty kill", special_teams_rate(games, "opponent_pp_goals", "opponent_pp_opportunities", True),
     opportunity_detail(games, "opponent_pp_goals", "opponent_pp_opportunities", True))]
with st.container(key="performance_cards"):
    for card, values in zip(st.columns(5), stats):
        with card:
            metric(*values)
missing_pp = int(games.pp_opportunities.isna().sum())
missing_pk = int(games.opponent_pp_opportunities.isna().sum())
if missing_pp or missing_pk:
    st.info(f"Opportunity counts are missing for power play in {missing_pp} of {len(games)} games "
            f"and penalty kill in {missing_pk}. Affected rates show N/A. Goals and shots are complete.")
selected_source_notes = {value: SOURCE_NOTES[value] for value in sorted(games.season.unique())
                         if value in SOURCE_NOTES}
if season in SOURCE_NOTES:
    st.caption(f"ⓘ {season} source note: {SOURCE_NOTES[season]} Details in Data notes below.")
elif selected_source_notes:
    st.caption(f"ⓘ Source conflicts affect {', '.join(selected_source_notes)}. See Data notes below.")

overview, special_teams, game_review, season_comparison = st.tabs(
    ["Team overview", "Special teams", "Game review", "Season comparison"])
with overview:
    left, right = st.columns([1.65, 1], gap="large")
    with left, st.container(border=True, key="panel_scoring"):
        st.subheader("Scoring trend")
        st.caption("Goals scored and allowed, game by game")
        trend_chart(games, ["goals_for", "goals_against"], ["Lawrence", "Opponents"], "Goals")
    with right, st.container(border=True, key="panel_recent"):
        st.subheader("Recent games")
        st.caption("Up to five most recent games in your selection")
        rows = []
        for game in games.tail(5).iloc[::-1].itertuples():
            rows.append(
                f'<div class="game-row"><div class="game-date">{game.date:%b}<b>{game.date:%d}</b></div>'
                f'<div class="game-opponent">{escape(game.opponent)}<span>{escape(game.location.title())}</span></div>'
                f'<div class="game-score">{game.goals_for}<span>–</span>{game.goals_against}</div></div>')
        st.markdown('<div class="game-list">' + ''.join(rows) + '</div>', unsafe_allow_html=True)
        st.caption("Scores shown as Lawrence – opponent. Shootout attempts excluded.")
    left, right = st.columns([1.65, 1], gap="large")
    with left, st.container(border=True, key="panel_shots"):
        st.subheader("Shot volume")
        st.caption("Shots on goal for and against")
        trend_chart(games, ["shots_for", "shots_against"], ["Lawrence", "Opponents"], "Shots on goal")
    with right, st.container(border=True, key="panel_venue"):
        st.subheader("Scoring by venue")
        st.caption("Average goals per game by venue")
        locations = [value for value in LOCATION_ORDER if value in games.location.values]
        comparison = games.groupby("location")[["goals_for", "goals_against"]].mean().reindex(locations)
        counts = games.groupby("location").size()
        fig = go.Figure()
        for column, name, color in [("goals_for", "Lawrence", BLUE), ("goals_against", "Opponents", SLATE)]:
            fig.add_bar(x=[f"{value.title()} · {counts[value]} games" for value in locations],
                        y=comparison[column], name=name, marker_color=color,
                        text=comparison[column].round(2), textposition="outside", cliponaxis=False,
                        hovertemplate="%{x}<br>%{y:.2f} goals / game<extra>%{fullData.name}</extra>")
        fig.update_layout(barmode="group", bargap=0.4)
        style_chart(fig, "Goals / game")
    with st.expander(f"Selected-game totals · {len(games)} games", expanded=season == "All seasons"):
        st.dataframe(pd.DataFrame({
            "Team": ["Lawrence", "Opponents"],
            "Goals": [int(totals.goals_for), int(totals.goals_against)],
            "Shots on goal": [int(totals.shots_for), int(totals.shots_against)],
            "Power-play goals": [int(totals.pp_goals), int(totals.opponent_pp_goals)],
            "Power-play chances": ["N/A" if missing_pp else count(totals.pp_opportunities),
                                   "N/A" if missing_pk else count(totals.opponent_pp_opportunities)],
        }), hide_index=True, use_container_width=True)
        st.caption("Totals cover every game in your selection. Opportunity totals show N/A when any selected count is missing.")

with special_teams:
    st.subheader("Make every opportunity count")
    st.caption("Rates use total goals and opportunities across your selected games.")
    left, right = st.columns(2, gap="large")
    for panel, label, goals_col, chances_col, complement, color in [
        (left, "Power play", "pp_goals", "pp_opportunities", False, BLUE),
        (right, "Penalty kill", "opponent_pp_goals", "opponent_pp_opportunities", True, TEAL)]:
        with panel, st.container(border=True, key=f"panel_{goals_col}"):
            st.subheader(label)
            st.metric("Success rate", special_teams_rate(games, goals_col, chances_col, complement))
            known = games.dropna(subset=[goals_col, chances_col])
            st.caption(opportunity_detail(games, goals_col, chances_col, complement))
            if len(known) == len(games):
                goals, chances = int(totals[goals_col]), int(totals[chances_col])
                successful = chances - goals if complement else goals
                if chances:
                    st.progress(successful / chances)
                else:
                    st.caption("No opportunities in this selection; the rate is unavailable.")
            else:
                st.caption(f"The chart includes {len(known)} of {len(games)} games with recorded counts. "
                           "Games with missing counts are omitted.")
            if known.empty:
                st.info("No recorded opportunity counts to chart in this selection.")
                continue
            fig = go.Figure()
            values = known[chances_col] - known[goals_col] if complement else known[goals_col]
            custom = known[["opponent", chances_col]].values
            fig.add_bar(x=known.date, y=values, name="Kills" if complement else "Goals", marker_color=color,
                        customdata=custom, hovertemplate="%{x|%b %d, %Y}<br>%{customdata[0]}<br>%{y} successful / %{customdata[1]} chances<extra></extra>")
            fig.add_bar(x=known.date, y=known[chances_col] - values,
                        name="Goals allowed" if complement else "No goal", marker_color="#DDE5F0",
                        customdata=custom, hovertemplate="%{x|%b %d, %Y}<br>%{customdata[0]}<br>%{y} unsuccessful / %{customdata[1]} chances<extra></extra>")
            fig.update_layout(barmode="stack")
            fig.update_xaxes(type="date", tickformat="%b %Y" if known.season.nunique() > 1 else "%b %d", nticks=6)
            style_chart(fig, "Opportunities", height=300)

with game_review:
    st.subheader("A closer look at each game")
    st.caption("Choose a game for a side-by-side team comparison and its original box score.")
    selected_index = st.selectbox("Game", games.index[::-1],
        format_func=lambda index: f"{games.loc[index, 'date']:%b %d, %Y} · {games.loc[index, 'opponent']} · {games.loc[index, 'location'].title()}")
    game = games.loc[selected_index]
    left, right = st.columns([1.6, 1], gap="large")
    with left, st.container(border=True, key="panel_game"):
        comparison = pd.DataFrame({
            "Statistic": ["Goals", "Shots on goal", "Shooting", "Power play", "Penalty kill"],
            "Lawrence": [count(game.goals_for), count(game.shots_for), percentage(game.goals_for, game.shots_for),
                         f"{count(game.pp_goals)} / {count(game.pp_opportunities)}", percentage(game.opponent_pp_goals, game.opponent_pp_opportunities, True)],
            "Opponent": [count(game.goals_against), count(game.shots_against), percentage(game.goals_against, game.shots_against),
                         f"{count(game.opponent_pp_goals)} / {count(game.opponent_pp_opportunities)}", percentage(game.pp_goals, game.pp_opportunities, True)]})
        st.dataframe(comparison, hide_index=True, use_container_width=True)
    with right:
        st.markdown(f"**{game.date:%B %d, %Y} · {game.location.title()}**")
        st.write(f"Lawrence vs. {game.opponent}")
        st.link_button("Open original box score ↗", game.source_url, use_container_width=True)
        st.caption("Team statistical scores exclude shootout attempts. Official overtime and shootout results are not yet recorded in this dataset.")
    st.markdown("#### Game log")
    log = games.sort_values("date", ascending=False).copy()
    log["score"] = log.goals_for.astype(str) + " – " + log.goals_against.astype(str)
    log["power_play"] = log.pp_goals.map(count) + " / " + log.pp_opportunities.map(count)
    log["location"] = log.location.str.title()
    st.dataframe(log[["date", "season", "opponent", "location", "score", "shots_for", "shots_against", "power_play", "source_url"]],
        hide_index=True, use_container_width=True, column_config={
            "date": st.column_config.DateColumn("Date", format="MMM D, YYYY"),
            "season": "Season",
            "opponent": "Opponent", "location": "Venue", "score": "Score (LU – Opp)",
            "shots_for": "Shots for", "shots_against": "Shots against", "power_play": "PP goals / chances",
            "source_url": st.column_config.LinkColumn("Box score", display_text="View ↗")})
    export = games.copy()
    export["date"] = export.date.dt.strftime("%Y-%m-%d")
    st.download_button("Download selected games ↓", export.to_csv(index=False), "lawrence_selected_games.csv", "text/csv")

with season_comparison:
    st.subheader("The bigger picture")
    st.caption("Full-season comparison across all venues and opponents, including every archived game. "
               "Use the other tabs to review your sidebar selection.")
    summary_rows = []
    for archived_season, frame in all_games.groupby("season", sort=True):
        summary_rows.append({
            "season": archived_season, "games": len(frame),
            "goals_for": frame.goals_for.mean(), "goals_against": frame.goals_against.mean(),
            "shots_for": frame.shots_for.mean(),
            "shooting": percentage(frame.goals_for.sum(), frame.shots_for.sum()),
            "power_play": special_teams_rate(frame, "pp_goals", "pp_opportunities"),
            "penalty_kill": special_teams_rate(frame, "opponent_pp_goals", "opponent_pp_opportunities", True),
            "pp_coverage": f"{frame.pp_opportunities.notna().sum()} / {len(frame)}",
            "pk_coverage": f"{frame.opponent_pp_opportunities.notna().sum()} / {len(frame)}",
        })
    summary = pd.DataFrame(summary_rows)
    with st.container(border=True, key="panel_seasons"):
        st.subheader("Scoring across seasons")
        st.caption("Goals per game keeps seasons with different game counts comparable.")
        fig = go.Figure()
        for column, name, color in [("goals_for", "Lawrence", BLUE), ("goals_against", "Opponents", SLATE)]:
            fig.add_bar(x=summary.season, y=summary[column], name=name, marker_color=color,
                        customdata=summary[["games"]].values,
                        hovertemplate="%{x} · %{customdata[0]} games<br>%{y:.2f} goals / game<extra>%{fullData.name}</extra>")
        fig.update_layout(barmode="group", bargap=0.35)
        fig.update_xaxes(type="category")
        style_chart(fig, "Goals / game")
    st.dataframe(summary, hide_index=True, use_container_width=True, column_config={
        "season": "Season", "games": "Games",
        "goals_for": st.column_config.NumberColumn("Goals / game", format="%.2f"),
        "goals_against": st.column_config.NumberColumn("Allowed / game", format="%.2f"),
        "shots_for": st.column_config.NumberColumn("Shots / game", format="%.1f"),
        "shooting": "Shooting", "power_play": "Power play", "penalty_kill": "Penalty kill",
        "pp_coverage": "PP counts available", "pk_coverage": "PK counts available",
    })
    st.caption("Coverage is games with recorded opportunity counts / total games. "
               "N/A means a count is missing or the total denominator is zero. Opponents and schedules vary by season.")
    with st.expander("Historical source conflicts"):
        for note_season, note in SOURCE_NOTES.items():
            st.write(f"**{note_season}:** {note}")

with st.expander("Data notes & sources"):
    st.markdown("**Source:** Public Lawrence Athletics game statistics. Each game links to its original box score in Game review.")
    st.write("Percentages are calculated from summed goals and opportunities, not averages of game percentages. "
             "Missing or zero opportunity counts produce N/A. Missing values stay blank in downloaded CSVs. "
             "Shots are shots on goal. Scores exclude shootout attempts.")
    for note_season, note in selected_source_notes.items():
        st.warning(f"{note_season}: {note}")
    st.caption("Small samples, opponent strength, and schedule differences affect comparisons. "
               "These team statistics describe outcomes; they do not establish causes or measure individual player performance.")

st.markdown('<div class="page-footer"><span>LAWRENCE / HOCKEY ANALYTICS</span>'
            '<span>Independent student project · Public game statistics</span></div>', unsafe_allow_html=True)
