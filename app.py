"""Run with: python -m streamlit run app.py"""
import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st
from src.prepare_data import OUTPUT

st.set_page_config(page_title="Lawrence Hockey Analytics", page_icon="🏒", layout="wide")
st.title("Lawrence Women's Ice Hockey")
st.caption("Independent student analytics project • In development • Public game statistics")

database = OUTPUT / "hockey.db"
if not database.exists():
    st.info("Your dashboard is ready for data. No game statistics have been imported yet.")
    st.markdown("1. Add five verified games to `data/raw/games.csv`.\n"
                "2. Run `python -m src.prepare_data` in your terminal.\n"
                "3. Refresh this page. See `docs/getting-started.md` for instructions.")
    st.stop()

with sqlite3.connect(database) as connection:
    games = pd.read_sql_query("SELECT * FROM games ORDER BY date", connection)

st.sidebar.header("Filter games")
for column, label in [("season", "Season"), ("location", "Location"), ("opponent", "Opponent")]:
    options = sorted(games[column].unique())
    selected = st.sidebar.multiselect(label, options, default=options)
    games = games[games[column].isin(selected)]
if games.empty:
    st.info("No games match these filters. Select at least one option in each filter.")
    st.stop()


def percentage(numerator, denominator, complement=False):
    if denominator == 0:
        return "N/A"
    value = numerator / denominator
    return f"{100 * (1 - value if complement else value):.1f}%"


if "2025-26" in games["season"].values:
    st.warning("2025–26 source note: opponent power-play opportunities total 92 in the individual box scores, versus 91 in the season summary. This dashboard uses the box-score counts (full-season penalty kill: 76.1%). See docs/sources.md.")

totals = games.select_dtypes(include="number").sum()
cards = st.columns(5)
cards[0].metric("Games", len(games))
cards[1].metric("Goals per game", f"{games.goals_for.mean():.2f}")
cards[2].metric("Shooting", percentage(totals.goals_for, totals.shots_for))
cards[3].metric("Power play", percentage(totals.pp_goals, totals.pp_opportunities))
cards[4].metric("Penalty kill", percentage(totals.opponent_pp_goals, totals.opponent_pp_opportunities, True))

st.subheader("Scoring over time")
st.plotly_chart(px.line(games, x="date", y=["goals_for", "goals_against"],
                        markers=True, hover_data=["opponent", "location"],
                        labels={"value": "Goals", "date": "Game date", "variable": "Statistic"}),
                use_container_width=True)
left, right = st.columns(2)
comparison = games.groupby("location", as_index=False)[["goals_for", "goals_against"]].mean()
with left:
    st.subheader("Scoring by location")
    st.plotly_chart(px.bar(comparison, x="location", y=["goals_for", "goals_against"],
                           barmode="group", labels={"value": "Goals per game"}), use_container_width=True)
with right:
    st.subheader("Shots and goals")
    st.plotly_chart(px.scatter(games, x="shots_for", y="goals_for", color="location",
                               hover_data=["date", "opponent"]), use_container_width=True)
st.subheader("Game data and sources")
st.dataframe(games, hide_index=True, use_container_width=True)
st.download_button("Download filtered CSV", games.to_csv(index=False), "filtered_games.csv", "text/csv")
st.caption("Rates use totals across selected games. Small samples, opponent strength, and schedule differences limit comparisons; associations do not establish causes.")
