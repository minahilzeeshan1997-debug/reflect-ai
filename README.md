# Reflect MVP v0.4 — optional evidence-linked AI insights

**Upgrade from v0.3.2:** Copy `server.py`, `static/app.js`, and `README.md` into your current Reflect project. **Do not replace or delete `reflect.sqlite3`.** No database migration is required.

## Start locally

From the existing Reflect folder in VS Code PowerShell:

```powershell
python server.py
```

Open http://127.0.0.1:8765. Your existing password account and Google sign-in configuration remain in place.

## Choose an insight mode

- **Generate offline insight**: existing deterministic keyword baseline; no internet connection, provider account, or API key required.
- **Analyze with AI**: optional AI-powered thematic analysis that sends **up to 30 latest reflection entries** to OpenAI **only when you explicitly confirm**. Requires a personal API key; costs may apply. The key stays on the Python server and is never embedded in JavaScript or GitHub.

### Enable AI on Windows (PowerShell)

1. Create an API key in your OpenAI API account and keep it private.
2. In the same VS Code PowerShell terminal used to launch Reflect, run:

```powershell
$env:OPENAI_API_KEY="YOUR_API_KEY"
$env:REFLECT_AI_MODEL="gpt-4o-mini"
python server.py
```

3. Refresh Reflect. On **Insights & patterns**, you will see **Analyze with AI** beside **Generate offline insight**.
4. The browser asks for confirmation before transmitting your reflection text. The response is validated against your reflection IDs; you can inspect evidence and confirm or dismiss it.

Note: the AI API subscription/billing is separate from a ChatGPT Plus subscription. Never commit keys, publish them in screenshots, or paste them in chat.

## Safety and evidence guardrails

Reflect only accepts JSON insights with `pattern`, `observation`, or `insufficient_evidence` labels. A pattern needs **at least two cited reflection IDs on different dates**; an observation requires exactly one; insufficient evidence requires none. All IDs must refer to a reflection in the current signed-in user's selected history. Invalid or unavailable AI responses fail safely with a clear error; they are **not** silently converted into fabricated AI results. The offline baseline remains available.

These checks validate references and basic structure, **not semantic truth**. Users must verify whether the cited context actually supports the claim. Do not use this local prototype for HR decisions or employee evaluations. Avoid inserting confidential, identifying, or sensitive information. It is not yet hardened for internet deployment; do not expose the local server publicly.

## Testing

```powershell
python -m unittest discover -s tests -v
```

The project continues using Python 3.10+, SQLite, and the standard library only for the main MVP; the OpenAI request uses Python's built-in HTTPS client. Google sign-in setup, if used, still requires the packages in `requirements-google.txt`.

## Next AI PM milestones

Evaluate insight precision, citation relevance, failure rate, false-pattern rate, latency, and cost against labeled synthetic reflection cases. Add explicit privacy settings, a data deletion/export flow, rate limiting, and secure hosting before deployment to others.
