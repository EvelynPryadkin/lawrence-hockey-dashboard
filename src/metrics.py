"""Rates must not combine known goals with missing opportunity counts."""


def special_teams_rate(games, goals, opportunities, complement=False):
    if games.empty or games[[goals, opportunities]].isna().any().any():
        return "N/A"
    denominator = games[opportunities].sum()
    if denominator == 0:
        return "N/A"
    value = games[goals].sum() / denominator
    return f"{100 * (1 - value if complement else value):.1f}%"
