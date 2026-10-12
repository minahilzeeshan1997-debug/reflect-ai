# Reflect — working MVP (local pilot v0.3)

A runnable local web application inspired by the Reflect Figma flow: **dark forest green, sage accents, frosted cards**, and an end-to-end leadership-reflection workflow.

## Run locally

1. Install **Python 3.10+**.
2. Open a terminal in the `Reflect_MVP` folder.
3. Run `python server.py` (Windows: `py server.py`).
4. Open **http://127.0.0.1:8765** in a browser.
5. Create your account and start writing reflections.

No packages or API keys are needed for password login and the basic MVP. Google login is optional and needs Google OAuth configuration and two Python dependencies (see v0.3 section). The first run creates `reflect.sqlite3` locally. The SQLite database is **not** included in the ZIP and is ignored when sharing the source. Set `REFLECT_DB` to place it somewhere else. Stop with Ctrl+C.

## Supported workflow

Sign up / sign in (optional Google OAuth) → dashboard → guided reflection → generate one evidence-linked insight → inspect cited reflection entries → confirm or dismiss → choose a small action → review the outcome → revisit private history.

### Functional features

- Password-based local accounts using salted PBKDF2-SHA256 and per-account SQLite data.
- HTTP-only SameSite session cookies, CSRF tokens on state-changing requests.
- Guided reflections with event date, situation, response and learning.
- Private reflection history.
- Conservative **rule-based pilot insight detector** with three states (`pattern`, `observation`, `insufficient_evidence`) and reflection ID citations.
- Confirm / dismiss insight feedback.
- Create actions and review tried / not yet / different with outcomes.
- Responsive desktop/mobile layout, dark-forest/sage style, keyboard focus and reduced-motion accommodation.

### Critical AI limitation

**No language model is included or called.** The insight detector currently recognizes a small list of phrases about ownership, feedback, priorities and meetings. It can suggest a possible recurring theme only when two or more matching reflection entries are on distinct dates. This is a *candidate*, not reliable proof of a semantic pattern. It can still make false positives and false negatives. Citation IDs are real user entries; the app does not claim full semantic groundedness. For detailed reflections without recurrence, it shows a one-time observation. For vague entries, it says evidence is insufficient. Never use these insights for employee or HR decisions.

Next AI milestone: independently label at least 30 synthetic examples, run this baseline, measure precision/recall and citation relevance, then add a validated LLM-based evaluator if it improves results.

## Privacy and deployment cautions

This is a **local development/pilot prototype**, **not production-ready**. Do **not** deploy it publicly with actual sensitive leadership or employee information. In particular, production still requires HTTPS and `Secure` cookies, stricter auth/session lifecycle, login rate limits, account recovery/email verification, deletion/export workflows, formal retention policy, monitoring, backups, and security review. Authentication is demonstrated but not production hardened. Serve from localhost, and only use fictional/test data when demonstrating publicly.

## API reference

- `POST /api/signup`, `POST /api/login`, `POST /api/logout`, `GET /api/me`
- `GET/POST /api/reflections`
- `GET /api/insights`, `POST /api/insights/generate`, `POST /api/insights/feedback`
- `GET/POST /api/actions`, `POST /api/actions/review`

Protected POST endpoints require header `X-CSRF-Token` returned by `/api/me` or auth response. Cross-user record lookups use the authenticated user ID.

## MVP versus production roadmap

1. **v0.1** Local workflow and rule-based evidence links (this package).
2. **v0.2** Edit/delete reflections, account recovery, consent and exports, design polish and usability tests.
3. **v0.3** LLM-backed generation with structured outputs, strict per-user retrieval, source-ID validation, human semantic-groundedness evaluations, safe fallback states, and performance/cost telemetry.
4. **v1.0** HTTPS hosting, hardened auth, database hosting, observability, privacy/security controls, evaluation gate and launch instrumentation.

## Testing

Run `python -m unittest discover -s tests -v` from this directory. The tests cover deterministic pattern states and password verification.

## v0.2 password update

Password fields on both Sign In and Sign Up now offer a **Show/Hide** toggle. It does not alter the password or submit the form; pressing Hide masks it again.

## v0.3 — sign out, profile menu, navigation and real Google OAuth

**What changed:**

- The profile chip (initial and first name) is now a button. Click it on any screen to see **My overview**, **My insights**, and **Sign out**. This menu is visible on mobile too. Sign out revokes the server-side session and clears the browser cookie; you return to Sign In.
- Sidebar order: **Overview → New reflection → Insights & patterns → Action review → Reflection history**.
- Both Sign In and Sign Up now show **Continue with Google**. This is *real* Google OpenID Connect authorization-code sign-in after you configure credentials, **not a fake button**.
- The previously-created SQLite file is backward compatible; the server creates additional `google_identities` and temporary `oauth_states` tables as needed.

### Configure Google sign-in (optional)

1. In **[Google Cloud Console](https://console.cloud.google.com/apis/credentials)**, create or select a project. Configure the Google Auth Platform branding / OAuth consent screen and add your own Google email as a **test user** when using Testing mode.
2. Create an OAuth client of type **Web application** (not Desktop). Add the exact **Authorized redirect URI**:

   `http://127.0.0.1:8765/auth/google/callback`

   Use `127.0.0.1`, not `localhost`, unless you configure the same URI on both Google Cloud and the app.
3. Install Google's verification dependencies (Google OAuth is the only feature that requires additional packages):

   `python -m pip install -r requirements-google.txt`

4. **Set the credentials in the same VS Code terminal where you run the server**. On Windows PowerShell:

   ```powershell
   $env:REFLECT_GOOGLE_CLIENT_ID="YOUR_CLIENT_ID.apps.googleusercontent.com"
   $env:REFLECT_GOOGLE_CLIENT_SECRET="YOUR_CLIENT_SECRET"
   python server.py
   ```

   The redirect URI defaults to `http://127.0.0.1:8765/auth/google/callback`. If you change port/hostname, set `REFLECT_GOOGLE_REDIRECT_URI` and add that **exact same value** in Google Cloud Console.
5. Go to `http://127.0.0.1:8765`, click **Continue with Google**, and authenticate with Google. Google returns you to Reflect with a local session.

**Important account policy:** For safety, this MVP will **not automatically link** an existing password account to a Google account merely because the email matches. If you already created a password account with that address, continue using password sign-in for that account. Google sign-in can be tested with a different Google address. Future account linking would require verifying both identities. This prevents accidental or unsafe account merges.

The app requests only Google's `openid email profile` scopes. It does not request Gmail, Drive, Calendar, or refresh tokens. The server uses a single-use state and browser cookie for OAuth CSRF protection, exchanges the authorization code server-side, and verifies Google's signed ID token using the `google-auth` library (including audience, issuer and expiry). Google's `sub` is stored as the stable account identifier. Credentials stay in server environment variables—**never** place them in `app.js` or upload them to GitHub. Google OAuth needs an internet connection and your own configuration; regular password login works offline.

**This remains a localhost MVP.** Do not deploy publicly without hardened cookie/session settings, HTTPS, account recovery, rate limiting, storage protection, and review of the authentication and linking flows.

### Updating your existing MVP without losing reflections

**Safest option: replace only the source files, keep your database.**

1. Stop the existing VS Code terminal server with `Ctrl+C`.
2. Extract v0.3 ZIP to a separate folder.
3. Copy **`server.py`**, **`static/app.js`**, **`static/app.css`**, and (optionally) **`requirements-google.txt`** from the new `Reflect_MVP` folder into your old working `Reflect_MVP` folder, replacing just those files.
4. **Do not replace or delete `reflect.sqlite3`**, because it stores your account and reflections. If you see `reflect.sqlite3-wal` or `reflect.sqlite3-shm`, stop the server cleanly and back up all three files together before copying anything.
5. Run `python server.py` and refresh the browser with `Ctrl+Shift+R`.
6. Click your profile chip, choose **Sign out**, then sign back in to test. Google login appears whether or not it's configured, but requires the one-time steps above to work.

### Tests

`python -m unittest discover -s tests -v`

Tests now include real HTTP signup → logout → login → logout checks against a temporary database, plus validation of the local insight detector. No Google credentials are included. Google sign-in itself cannot be integration-tested without your configured Google Cloud OAuth client.
