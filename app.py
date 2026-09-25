"""Coach-focused team dashboard. Run: python -m streamlit run app.py"""
from html import escape
from pathlib import Path
import sqlite3

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.prepare_data import OUTPUT

BLUE, SLATE, TEAL = "#2563EB", "#7C8DA8", "#087F8C"
LOCATION_ORDER = ["home", "away", "neutral"]
st.set_page_config(page_title="Lawrence | Hockey Analytics", page_icon="🏒", layout="wide")
st.markdown(f"<style>{(Path(__file__).parent / 'assets/dashboard.css').read_text()}</style>", unsafe_allow_html=True)


def percentage(numerator, denominator, complement=False):
    if denominator == 0:
        return "N/A"
    value = numerator / denominator
    return f"{100 * (1 - value if complement else value):.1f}%"


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
        fig.add_trace(go.Scatter(
            x=frame["date"], y=frame[column], name=name, mode="lines+markers",
            line=dict(color=color, width=3, dash=dash), marker=dict(size=7),
            customdata=frame[["opponent", "location"]].values,
            hovertemplate=("%{x|%b %d, %Y}<br>%{customdata[0]} · %{customdata[1]}"
                           f"<br>{name}: %{{y}}<extra></extra>")))
    fig.update_xaxes(type="date", tickformat="%b %d", nticks=7)
    style_chart(fig, y_title)


database = OUTPUT / "hockey.db"
if not database.exists():
    st.title("Lawrence Hockey Analytics")
    st.info("Import the included game statistics to open your dashboard.")
    st.code("python -m src.prepare_data", language="bash")
    st.caption("Run this from the project folder, then refresh the page.")
    st.stop()

with sqlite3.connect(database) as connection:
    all_games = pd.read_sql_query("SELECT * FROM games ORDER BY date, opponent", connection)
all_games["date"] = pd.to_datetime(all_games["date"])
if all_games.empty:
    st.info("No games have been imported yet. Run python -m src.prepare_data to load the data.")
    st.stop()

with st.sidebar:
    st.markdown('<div class="sidebar-brand"><span class="brand-mark">LH</span>'
                '<div>LAWRENCE<span>HOCKEY ANALYTICS</span></div></div>', unsafe_allow_html=True)
    st.caption("Women's ice hockey · Team performance")
    st.divider()
    st.markdown("#### Your game selection")
    season = st.selectbox("Season", sorted(all_games["season"].unique(), reverse=True))
    season_games = all_games[all_games["season"] == season]
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
    ("Goals / game", f"{games.goals_for.mean():.2f}", f"{totals.goals_for} goals in {len(games)} games"),
    ("Shots / game", f"{games.shots_for.mean():.1f}", f"{totals.shots_for} shots on goal"),
    ("Shooting", percentage(totals.goals_for, totals.shots_for), "Goals ÷ shots on goal"),
    ("Power play", percentage(totals.pp_goals, totals.pp_opportunities), f"{totals.pp_goals} goals / {totals.pp_opportunities} chances"),
    ("Penalty kill", percentage(totals.opponent_pp_goals, totals.opponent_pp_opportunities, True),
     f"{totals.opponent_pp_goals} goals allowed / {totals.opponent_pp_opportunities} chances")]
with st.container(key="performance_cards"):
    for card, values in zip(st.columns(5), stats):
        with card:
            metric(*values)
if season == "2025-26":
    st.caption("ⓘ Penalty kill uses individual box scores. Their season total is 92 opponent chances; "
               "the published summary lists 91. Details in Data notes below.")

overview, special_teams, game_review = st.tabs(["Team overview", "Special teams", "Game review"])
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
        st.subheader("Home & away")
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

with special_teams:
    st.subheader("Make every opportunity count")
    st.caption("Rates use total goals and opportunities across your selected games.")
    left, right = st.columns(2, gap="large")
    for panel, label, goals_col, chances_col, complement, color in [
        (left, "Power play", "pp_goals", "pp_opportunities", False, BLUE),
        (right, "Penalty kill", "opponent_pp_goals", "opponent_pp_opportunities", True, TEAL)]:
        with panel, st.container(border=True, key=f"panel_{goals_col}"):
            goals, chances = int(totals[goals_col]), int(totals[chances_col])
            successful = chances - goals if complement else goals
            st.subheader(label)
            st.metric("Success rate", percentage(goals, chances, complement))
            st.caption(f"{successful} {'kills' if complement else 'goals'} across {chances} opportunities")
            if chances:
                st.progress(successful / chances)
            else:
                st.caption("No opportunities in this selection; the rate is unavailable.")
            fig = go.Figure()
            values = games[chances_col] - games[goals_col] if complement else games[goals_col]
            custom = games[["opponent", chances_col]].values
            fig.add_bar(x=games.date, y=values, name="Kills" if complement else "Goals", marker_color=color,
                        customdata=custom, hovertemplate="%{x|%b %d}<br>%{customdata[0]}<br>%{y} successful / %{customdata[1]} chances<extra></extra>")
            fig.add_bar(x=games.date, y=games[chances_col] - values,
                        name="Goals allowed" if complement else "No goal", marker_color="#DDE5F0",
                        customdata=custom, hovertemplate="%{x|%b %d}<br>%{customdata[0]}<br>%{y} unsuccessful / %{customdata[1]} chances<extra></extra>")
            fig.update_layout(barmode="stack")
            fig.update_xaxes(type="date", tickformat="%b %d", nticks=6)
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
            "Lawrence": [str(game.goals_for), str(game.shots_for), percentage(game.goals_for, game.shots_for),
                         f"{game.pp_goals} / {game.pp_opportunities}", percentage(game.opponent_pp_goals, game.opponent_pp_opportunities, True)],
            "Opponent": [str(game.goals_against), str(game.shots_against), percentage(game.goals_against, game.shots_against),
                         f"{game.opponent_pp_goals} / {game.opponent_pp_opportunities}", percentage(game.pp_goals, game.pp_opportunities, True)]})
        st.dataframe(comparison, hide_index=True, use_container_width=True)
    with right:
        st.markdown(f"**{game.date:%B %d, %Y} · {game.location.title()}**")
        st.write(f"Lawrence vs. {game.opponent}")
        st.link_button("Open original box score ↗", game.source_url, use_container_width=True)
        st.caption("Team statistical scores exclude shootout attempts. Official overtime and shootout results are not yet recorded in this dataset.")
    st.markdown("#### Game log")
    log = games.sort_values("date", ascending=False).copy()
    log["score"] = log.goals_for.astype(str) + " – " + log.goals_against.astype(str)
    log["power_play"] = log.pp_goals.astype(str) + " / " + log.pp_opportunities.astype(str)
    log["location"] = log.location.str.title()
    st.dataframe(log[["date", "opponent", "location", "score", "shots_for", "shots_against", "power_play", "source_url"]],
        hide_index=True, use_container_width=True, column_config={
            "date": st.column_config.DateColumn("Date", format="MMM D, YYYY"),
            "opponent": "Opponent", "location": "Venue", "score": "Score (LU – Opp)",
            "shots_for": "Shots for", "shots_against": "Shots against", "power_play": "PP goals / chances",
            "source_url": st.column_config.LinkColumn("Box score", display_text="View ↗")})
    export = games.copy()
    export["date"] = export.date.dt.strftime("%Y-%m-%d")
    st.download_button("Download selected games ↓", export.to_csv(index=False), "lawrence_selected_games.csv", "text/csv")

with st.expander("Data notes & sources"):
    st.markdown("**Source:** Public Lawrence Athletics game statistics. Each game links to its original box score in Game review.")
    st.write("Percentages are calculated from summed goals and opportunities, not averages of game percentages. "
             "Zero opportunities produce N/A. Shots are shots on goal. Scores exclude shootout attempts.")
    if season == "2025-26":
        st.warning("2025–26 penalty-kill discrepancy: individual box scores total 92 opponent power-play opportunities; "
                   "the published season summary lists 91. This dashboard uses 92, giving a full-season penalty kill "
                   "of 76.1% (versus 75.8% with 91). The source discrepancy remains unresolved.")
    st.caption("Small samples, opponent strength, and schedule differences affect comparisons. "
               "These team statistics describe outcomes; they do not establish causes or measure individual player performance.")

st.markdown('<div class="page-footer"><span>LAWRENCE / HOCKEY ANALYTICS</span>'
            '<span>Independent student project · Public game statistics</span></div>', unsafe_allow_html=True)
