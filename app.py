"""Run with: python -m streamlit run app.py"""
import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st
from src.prepare_data import OUTPUT
from src.metrics import special_teams_rate

st.set_page_config(page_title="Lawrence Hockey Analytics", page_icon="🏒", layout="wide")
st.title("Lawrence Women's Ice Hockey")
st.caption("Independent student analytics project • In development • Public game statistics")

database = OUTPUT / "hockey.db"
if not database.exists():
    st.info("The game data is included. Run `python -m src.prepare_data` in your terminal, then refresh this page.")
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
if "2021-22" in games["season"].values:
    st.warning("2021–22 source note: the January 28 Finlandia box score lists one Lawrence power-play goal, but the season game table lists zero. The dataset retains the season game table value. See docs/sources.md.")
if "2024-25" in games["season"].values:
    st.warning("2024–25 source note: available box scores sum to 74 Lawrence power-play opportunities (one game missing), versus 72 in the summary; opponent opportunities total 92 versus 91. Box-score counts are retained. See docs/sources.md.")
missing_pp = int(games.pp_opportunities.isna().sum())
missing_pk = int(games.opponent_pp_opportunities.isna().sum())
if missing_pp or missing_pk:
    st.info(f"Missing opportunity counts: Lawrence power play in {missing_pp} of {len(games)} selected games; opponents in {missing_pk}. Affected rates show N/A rather than treating missing data as zero.")

totals = games.select_dtypes(include="number").sum()
cards = st.columns(5)
cards[0].metric("Games", len(games))
cards[1].metric("Goals per game", f"{games.goals_for.mean():.2f}")
cards[2].metric("Shooting", percentage(totals.goals_for, totals.shots_for))
cards[3].metric("Power play", special_teams_rate(games, "pp_goals", "pp_opportunities"))
cards[4].metric("Penalty kill", special_teams_rate(games, "opponent_pp_goals", "opponent_pp_opportunities", True))

st.subheader("Season comparison")
season_summary = games.groupby("season").agg(
    games=("date", "size"), goals_per_game=("goals_for", "mean"),
    goals_allowed_per_game=("goals_against", "mean"), shots_per_game=("shots_for", "mean"),
).round(2).reset_index()
st.dataframe(season_summary, hide_index=True, use_container_width=True)

st.subheader("Scoring over time")
scoring = games.melt(id_vars=["date", "season", "opponent", "location"],
                     value_vars=["goals_for", "goals_against"],
                     var_name="statistic", value_name="goals")
st.plotly_chart(px.line(scoring, x="date", y="goals", color="statistic", line_group="season",
                        markers=True, hover_data=["season", "opponent", "location"],
                        labels={"goals": "Goals", "date": "Game date", "statistic": "Statistic"}),
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
