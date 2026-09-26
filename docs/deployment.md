# Put the dashboard online

The repository is ready for a Streamlit Community Cloud deployment. A public app still needs to be created from your account; there is no live app URL yet. The GitHub repository is currently private. A recruiter will not be able to open its links without access; the walkthrough MP4 can be shared separately.

## Check it locally

From the project folder:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests
python -m streamlit run app.py
```

A fresh checkout works without `data/processed/hockey.db`. The app validates the included `data/raw/games.csv`, loads it into an in-memory SQLite database, and reads the game table. It does not create files during startup. Missing opportunity counts stay missing. Invalid rows produce an error rather than an incomplete dashboard.

If a local `hockey.db` already exists, the app uses that import. After changing the CSV locally, run `python -m src.prepare_data` to refresh it.

## Deploy from GitHub

Push these changes to GitHub first. Then sign in to [Streamlit Community Cloud](https://share.streamlit.io/) and connect the GitHub repository. Authorize access to this private repository if prompted. Choose **Create app** and the option for an existing app. Use these settings:

| Setting | Value |
| --- | --- |
| Repository | `EvelynPryadkin/lawrence-hockey-dashboard` |
| Branch | `main` |
| Main file path | `app.py` |
| Python version | `3.12` in Advanced settings |

Choose a short app subdomain if one is available, then deploy. This app does not need API keys or secrets. These steps follow the [official Streamlit deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy).

Once it opens, select **All seasons** and check for 138 games, 135 Lawrence goals, and 2,453 Lawrence shots. Power play and penalty kill should show N/A for the full archive because some games lack opportunity counts. Try the venue filter and open an individual game.

Open the app link in a signed-out or private browser window before sharing it. Add the actual URL to the README and your résumé once you have confirmed that a visitor can use it. A localhost address will only work on your own computer.
