# Reflect MVP v0.5 — Product experience and local account recovery

Private leadership reflection prototype built with Python, SQLite and vanilla JavaScript. **For local use and fictional/demo reflection data only. Not production-ready.**

## Update an existing Reflect installation without losing reflections

1. Stop Reflect (`Ctrl+C` in the terminal).
2. **Back up** your original `reflect.sqlite3` using Windows File Explorer or the `sqlite3.Connection.backup()` API. If your app was running, stop it first.
3. Extract this ZIP to a **separate folder**. Copy all source files from its `Reflect_MVP` folder into your **existing** `Reflect_MVP` folder, replacing code files only. **Do not delete or replace your existing `reflect.sqlite3` database**. The ZIP contains no database.
4. In your original folder, run `python server.py --check-db` and verify your existing account and reflection totals before starting.
5. Run `python server.py`, open `http://127.0.0.1:8765` (do not switch between `localhost` and `127.0.0.1`). Force refresh using `Ctrl+Shift+R`.

## Fix sign-in for an existing local password account

If you get `401` on `/api/login`, it means your email or password was rejected: the absence of a session cookie is expected. Check the database using:

```powershell
python server.py --check-db
```

If it shows your original account(s), stop the server and run:

```powershell
python reset_local_password.py
```

Enter your registered email and a new password **locally**; the recovery utility backs up your SQLite database before changing only that account's password hash and invalidating existing sessions. Your reflections, insights, actions, and account ID remain unchanged. **Do not commit, deploy, or expose this local recovery script as an online password reset feature.** Anyone with direct local database access could use it; that is why it is intended only for local development.

If `accounts: 0` or the account email is not present, **do not reset or create a new account**: locate your original `reflect.sqlite3` first.

## Features in this release

- Dashboard: reflection totals, recent reflections, candidate insights, pending actions, unique reflection days and weekly rhythm (descriptive activity, not a leadership performance score).
- Reflection history: search by text/date, filter for recent or entries with learning, edit and delete with confirmation. Editing an entry flags linked insights for re-review; deleting removes its evidence citation and downgrades linked insights.
- Insights: original source reflection context and user confirmation/dismissal. Offline keyword baseline and optional Gemini analysis still available.
- Account: update display name, change password with current password, sign out. Email-based recovery and hosted accounts **not implemented**.
- Sign-in: generic client-side errors; local terminal shows whether email was missing or password did not match. Local password recovery tool provided.

## Optional Gemini

```powershell
$env:GEMINI_API_KEY="YOUR_KEY"
$env:REFLECT_AI_MODEL="MODEL_LISTED_FOR_YOUR_KEY"
python server.py
```

Gemini availability and free-tier rules vary by account. To verify model access independently, see your previously created `run_gemini.py --list-models` tool. Never put API keys in source code or GitHub. The default model in the server may be unavailable for your specific project; override it using `REFLECT_AI_MODEL`.

## Tests

```powershell
python -m unittest discover -s tests -v
```

## Deployment status

This release is **not deployed** and should **not** be exposed publicly. Before real hosting, implement proper email recovery, hardened auth/cookies and HTTPS, abuse controls, backups, migrations, hosted database, privacy policy and data lifecycle controls. Google OAuth is optional and uses `requirements-google.txt` when configured.
