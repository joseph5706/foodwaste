# FoodWise AI — Streamlit version

This version runs natively on Streamlit Community Cloud. It does not start Flask or require `templates/` or `static/` to run.

## Deploy to Streamlit Community Cloud
1. Upload `app.py` and `requirements.txt` to the root of your GitHub repository.
2. Commit to your deployment branch.
3. In Streamlit Community Cloud, set the main file path to `app.py` and reboot the app.

## Optional AI recipes
Set `OPENAI_API_KEY` in Streamlit app Settings → Secrets. Optional values: `OPENAI_BASE_URL`, `OPENAI_MODEL`. Without a key, the app uses demo recipe suggestions.

## Data note
Pantry and impact records use Streamlit session state and are temporary. They can reset when the session/server restarts. Add a database for persistent multi-user storage.
