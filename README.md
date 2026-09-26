# 🏺 BharatVerse — PLAY • EXPLORE • DISCOVER

A game-first educational platform where students travel through time, make
decisions inside real historical situations, and discover the history
behind their choices — built for **Smart India Hackathon 2026**,
Problem Statement **26208** (AICTE — Toys & Games).

This README covers everything from "I've never used Flask" to
"deploy this and demo it to judges." Read it top to bottom the first time.

---

## 📖 Table of Contents

1. [What You're Building](#1-what-youre-building)
2. [Tech Stack & Beginner Glossary](#2-tech-stack--beginner-glossary)
3. [Folder Structure](#3-folder-structure)
4. [How the Pieces Talk to Each Other](#4-how-the-pieces-talk-to-each-other)
5. [Database Schema](#5-database-schema)
6. [Installation (Windows + VS Code)](#6-installation-windows--vs-code)
7. [Running the App](#7-running-the-app)
8. [Testing Checklist](#8-testing-checklist)
9. [Common Errors & Fixes](#9-common-errors--fixes)
10. [Git & GitHub](#10-git--github)
11. [Deployment (Vercel)](#11-deployment-vercel)
12. [Future Scalability](#12-future-scalability)
13. [SIH Presentation Support](#13-sih-presentation-support)

---

## 1. What You're Building

**BharatVerse** is not a quiz app. The core idea:

> We don't ask students to study history before they play.
> We make them play first — and discover the history behind their choices.

**User flow:** Login → Dashboard → Time Machine → Choose Era → Play Level →
Make a Decision → See Consequences → Read the Historical Record → Earn XP,
Treasures, Achievements → Unlock the Next Level → Complete the Realm →
Unlock the Civilization Map & Timeline → Hall of Legends leaderboard.

The MVP fully implements **one realm — Indus Valley Civilization — with 8
playable levels**. The other four realms (Ancient Kingdoms, Trade &
Exploration, Architecture & Heritage, Traditional Games) are shown as
"Locked / Coming Soon" on purpose — see [Section 12](#12-future-scalability)
for why, and how to add them later without rewriting the game engine.

---

## 2. Tech Stack & Beginner Glossary

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript (no frameworks — kept simple on purpose) |
| Backend | Python + **Flask** |
| Database | **SQLite** (a database stored in a single file, no server needed) |
| Auth | Flask sessions + Werkzeug password hashing |
| Deployment | Vercel (serverless Flask function) |

**Glossary** (terms used throughout this project):

- **Flask** — a Python framework that helps us build the backend (server-side
  logic) of our website.
- **Backend** — the part of the app that handles logic and data (Python files).
- **Frontend** — the part of the app the user sees and clicks on (HTML/CSS/JS).
- **Database** — a place where user accounts, scores, and progress are stored
  so they survive after the browser is closed.
- **Route** — a URL path (like `/dashboard`) that tells Flask which Python
  function should run and which page to show.
- **API** — a way for two pieces of software to talk to each other. This MVP
  does **not** depend on any external API — it runs 100% locally.
- **Blueprint** — Flask's way of grouping related routes into their own file
  (we have one blueprint per feature: `auth`, `dashboard`, `game`, etc.)
- **Session** — a small signed cookie Flask uses to remember which user is
  logged in between page loads.
- **Hashing** — turning a password into a scrambled, irreversible string
  before storing it, so even we (the developers) never see real passwords.

---

## 3. Folder Structure

```
bharatverse/
├── app.py                  # Main entry point — creates & wires the Flask app
├── config.py                # App settings (secret key, DB path)
├── requirements.txt          # Python dependencies
├── .gitignore
│
├── database/
│   └── init_db.py            # Creates tables + inserts starting data
│                              # (bharatverse.db is created here on first run)
│
├── models/
│   └── models.py             # All database read/write functions
│
├── routes/                    # One Flask Blueprint per feature
│   ├── auth.py                # Register / Login / Logout
│   ├── dashboard.py           # Student dashboard
│   ├── realms.py               # Realm selection, Time Machine, level journey
│   ├── game.py                 # The game screen, decisions, results, records
│   ├── map.py                   # Civilization Map
│   ├── timeline.py              # Historical Timeline
│   ├── leaderboard.py            # Hall of Legends + Profile
│   └── utils.py                   # @login_required decorator
│
├── game_engine/
│   ├── engine.py               # THE reusable decision/consequence engine
│   ├── scoring.py               # XP → Rank calculations
│   └── rewards.py                # Treasure/achievement message formatting
│
├── data/
│   ├── realms.json              # 5 realms, sites, timeline, treasures, achievements
│   └── indus_valley.json         # All 8 Indus Valley levels + choices + records
│
├── templates/                    # Jinja2 HTML templates (16 pages)
└── static/
    ├── css/                       # style.css (global) + per-page stylesheets
    └── js/                          # main.js + per-page interaction scripts
```

---

## 4. How the Pieces Talk to Each Other

```
Browser  →  routes/*.py (Blueprint)  →  game_engine/engine.py  →  models/models.py  →  SQLite DB
                    ↓
              templates/*.html  (renders the response back to the browser)
```

- **Routes** receive a URL request, call the engine or models to get/change
  data, then hand data to a template to render as HTML.
- **The Game Engine is data-driven.** `engine.py` doesn't contain any
  Indus-Valley-specific code. It reads whatever level/choice rows exist in
  the database and applies the same logic every time. This is what lets you
  add "Ancient Kingdoms" later by adding new JSON data, not new Python code.
- **Models never contain HTML**, and **templates never talk to the database
  directly** — this separation is what keeps a beginner codebase manageable.

---

## 5. Database Schema

| Table | Purpose |
|---|---|
| `users` | Account info + hashed password |
| `player_stats` | Each player's water/food/settlement/infrastructure/wellbeing/XP |
| `realms` | The 5 historical realms (only `indus_valley` is `active`) |
| `levels` | Each playable level, linked to a realm |
| `choices` | 2–4 choices per level, with `effects_json` (e.g. `{"water": 15}`) |
| `player_progress` | Per-user, per-level status: `locked` / `unlocked` / `completed` |
| `treasures` / `player_treasures` | Collectibles and who has unlocked them |
| `achievements` / `player_achievements` | Badges and who has unlocked them |
| `civilization_sites` | Real archaeological sites shown on the Civilization Map |
| `timeline_events` | Real historical periods shown on the Timeline |

Run `python database/init_db.py` any time to (re)create the schema and
seed it — it's safe to run repeatedly; it won't duplicate data.

---

## 6. Installation (Windows + VS Code)

Assume you know almost nothing — follow these exactly.

1. **Install Python**
   Go to https://python.org/downloads, download the latest Python 3, and
   run the installer. **Check the box "Add Python to PATH"** before clicking Install.

2. **Check Python installed correctly**
   Open Command Prompt (search "cmd" in the Start menu) and type:
   ```
   python --version
   ```
   You should see something like `Python 3.12.x`.

3. **Install VS Code**
   Download from https://code.visualstudio.com and install it.

4. **Create your project folder**
   Extract/copy the `bharatverse` folder somewhere easy to find, e.g.
   `C:\Users\YourName\Projects\bharatverse`.

5. **Open the folder in VS Code**
   In VS Code: `File → Open Folder...` → select the `bharatverse` folder.

6. **Open a terminal inside VS Code**
   `Terminal → New Terminal`. Make sure it shows the `bharatverse` folder path.

7. **Create a virtual environment**
   A virtual environment keeps this project's Python packages separate from
   everything else on your computer.
   ```
   python -m venv venv
   ```

8. **Activate the virtual environment**
   On Windows (Command Prompt):
   ```
   venv\Scripts\activate
   ```
   On Windows (PowerShell):
   ```
   venv\Scripts\Activate.ps1
   ```
   On Mac/Linux:
   ```
   source venv/bin/activate
   ```
   You'll know it worked because you'll see `(venv)` at the start of your terminal line.

9. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

10. **Initialize the database**
    ```
    python database/init_db.py
    ```
    You should see: `Database ready at: ...bharatverse.db (fresh install)`

11. **Run Flask**
    ```
    python app.py
    ```
    You should see output ending with something like:
    `Running on http://127.0.0.1:5000`

12. **Open your browser**
    Go to `http://127.0.0.1:5000`. You should see the BharatVerse landing page.

13. **Test the application**
    Click "Enter the Time Machine" → Register a new account → you should land
    on your Dashboard. See [Section 8](#8-testing-checklist) for a full checklist.

To stop the server, click into the terminal and press `Ctrl + C`.

---

## 7. Running the App

Every time you come back to work on the project:

```
cd bharatverse
venv\Scripts\activate        (Windows)   or   source venv/bin/activate   (Mac/Linux)
python app.py
```

If you ever want to **reset all progress and start fresh**, delete
`database/bharatverse.db` and run `python database/init_db.py` again.

---

## 8. Testing Checklist

Go through this list manually after any major change:

- [ ] Registration with a new username/email works
- [ ] Registration rejects duplicate username/email
- [ ] Registration rejects mismatched passwords
- [ ] Login with correct credentials works
- [ ] Login rejects wrong password
- [ ] Logout clears the session
- [ ] Dashboard shows correct XP, stats, and rank
- [ ] Realm selection shows Indus Valley as playable, others as locked
- [ ] Time Machine animation plays and redirects to the level journey
- [ ] Level 1 is unlocked by default; Levels 2–8 start locked
- [ ] Making a decision updates stats and shows the Result screen
- [ ] XP accumulates correctly across levels
- [ ] Treasures and achievements appear when a level awards them
- [ ] Completing a level unlocks the next one
- [ ] Historical Record page shows gameplay vs. historical context separately
- [ ] Civilization Map is locked until all 8 levels are completed
- [ ] Civilization Map markers show site details on click
- [ ] Historical Timeline is locked until all 8 levels are completed
- [ ] Hall of Legends shows demo entries + real players sorted by XP
- [ ] Profile page shows the logged-in player's own stats/treasures/achievements
- [ ] Logging out and back in preserves all progress (data persists in SQLite)
- [ ] Visiting an unknown URL shows the custom 404 page
- [ ] Layout looks correct on a narrow/mobile browser window

All of the above were run automatically with Flask's test client and a real
local server during development (see the notes below the table in this repo's
build history) — but you should re-verify manually before your SIH demo.

---

## 9. Common Errors & Fixes

| Error | Why it happens | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'flask'` | Dependencies aren't installed, or your virtual environment isn't activated | Run `venv\Scripts\activate` then `pip install -r requirements.txt` |
| `TemplateNotFound: dashboard.html` | Flask can't find your `templates/` folder, usually because you ran `app.py` from the wrong directory | `cd` into the `bharatverse` folder itself before running `python app.py` |
| `sqlite3.OperationalError: no such table: users` | The database was never initialized | Run `python database/init_db.py` |
| `Address already in use` / `port 5000 already in use` | Another program (or a previous Flask run) is already using port 5000 | Close the old terminal, or run `python app.py` after changing `port=5000` to `port=5001` in `app.py`'s last line |
| CSS/JS not loading (page looks unstyled) | Wrong path passed to `url_for('static', ...)`, or browser cache | Hard-refresh with `Ctrl+Shift+R`; check the exact filename matches what's in `static/css/` or `static/js/` |
| Flask route returns a blank page or 500 error | A Python exception happened inside the route | Look at the terminal running `python app.py` — the full error traceback is printed there |
| `sqlite3.IntegrityError: UNIQUE constraint failed` | Trying to register a username/email that already exists | This is expected — our code already shows a friendly flash message for this case |
| Session doesn't persist / keeps logging you out | `SECRET_KEY` changes every restart | Make sure `config.py`'s `SECRET_KEY` isn't regenerated randomly each run (ours uses a fixed dev default, or an environment variable) |

---

## 10. Git & GitHub

1. **Initialize Git** (inside the `bharatverse` folder):
   ```
   git init
   ```

2. **Check status** (see what Git has noticed):
   ```
   git status
   ```

3. **Stage all files**:
   ```
   git add .
   ```
   (`.gitignore` already excludes `venv/`, `__pycache__/`, and the local
   `.db` file so you don't accidentally commit them.)

4. **Commit**:
   ```
   git commit -m "Initial BharatVerse project"
   ```

5. **Create a new empty repository on GitHub** (via github.com → New Repository).
   **Do not** initialize it with a README (you already have one).

6. **Connect your local project to GitHub**:
   ```
   git remote add origin https://github.com/YOUR-USERNAME/bharatverse.git
   ```

7. **Push your code**:
   ```
   git branch -M main
   git push -u origin main
   ```

From now on, after making changes: `git add .` → `git commit -m "message"` →
`git push`.

**Never commit:** `venv/`, `.env` files, the `.db` file with real user data,
or any API keys/secrets.

---

## 11. Deployment (Vercel)

The repository includes `vercel.json` and `api/index.py`, so Vercel can run
the Flask app as a Python serverless function.

1. Push the repository to GitHub. Do not commit `venv/`, `.env`, or a real
   SQLite database.
2. Go to https://vercel.com, choose **Add New → Project**, and import the
   GitHub repository.
3. Keep the detected framework as **Other**. Vercel will install the packages
   from `requirements.txt` and use `api/index.py` as the entry point.
4. Add this environment variable in the Vercel project settings:
   - `SECRET_KEY`: a long random value, different from local development.
5. Deploy, then test `/`, `/login`, `/register`, `/dashboard`, `/profile`,
   `/leaderboard`, and one playable level.

**Important SQLite note:** Vercel's serverless filesystem is ephemeral and
read-only except for `/tmp`. The deployed app automatically uses
`/tmp/bharatverse.db`, which prevents write errors and is suitable for a demo,
but user accounts and progress can be lost when the function is recreated.
For persistent production data, set `DATABASE_PATH` only when using a mounted
database volume, or migrate the model layer to a hosted database such as
PostgreSQL. Do not put a production SQLite file in the repository.

---

## 12. Future Scalability

Because the game engine is **data-driven** (levels/choices/records live in
the database, not in Python `if` statements), adding a new realm mostly means:

1. Add a new `realms.json`-style entry with `status: "active"`.
2. Write a new `<realm>.json` file with levels, choices, and historical records
   in the same shape as `data/indus_valley.json`.
3. Extend `database/init_db.py`'s seeding functions to load it (or write a
   small generic loader once you have 2+ realms, since the pattern repeats).
4. No changes needed to `game_engine/engine.py`, `routes/game.py`, or any
   template — they already work for any realm/level/choice combination.

Other future directions explicitly scoped out of the MVP (kept simple on
purpose per SIH beginner-team guidance):

- More realms: Ancient Kingdoms, Trade & Exploration, Architecture & Heritage,
  Traditional Games (playable mini-games)
- Multilingual support (Hindi + regional languages)
- AI Historical Guide / AI narrator / AI hints (clearly optional, not MVP)
- Voice narration
- Teacher dashboard & classroom mode with student analytics
- Daily challenges and multiplayer competitions
- More archaeological sites and richer maps
- Mobile app / AR-VR experiences

---

## 13. SIH Presentation Support

**Problem:** Students rarely engage with history because it's usually taught
as facts to memorize, not experiences to live through.

**Solution:** BharatVerse flips the order — students play a decision-based
simulation first, then are shown the real historical context behind their
in-game choices, clearly separated from fiction.

**Innovation:** A single reusable, data-driven game engine can power many
historical eras — we just add new JSON content, not new code — while every
decision maps to sourced historical facts (never invented ones).

**Technical Approach:** Flask + SQLite kept deliberately simple and fully
local (no paid APIs, no complex cloud dependencies), so a first-year team can
build, understand, explain, and maintain 100% of the stack.

**User Workflow:** Login → Time Machine → Realm → Level → Decision →
Consequence → Historical Record → XP/Rewards → Unlock next level → complete
realm → Map & Timeline → Hall of Legends.

**Feasibility:** Fully working MVP with one polished realm and 8 complete
levels, rather than five shallow ones — judges can play a complete loop start
to finish.

**Scalability:** Architecture supports unlimited future realms/levels as pure
data; database can migrate from SQLite to PostgreSQL for production scale.

**Future Scope:** Multilingual support, AI-guided narration, teacher/classroom
mode, daily challenges, multiplayer, AR/VR — all layered onto the same core
engine without rearchitecting.

### 60–90 Second Demo Script

1. **(5s)** "This is BharatVerse — students don't study history, they *play*
   it first." Show the landing page.
2. **(10s)** Log in → land on Dashboard, point out XP/stats/rank.
3. **(10s)** Click "Enter Time Machine" → show the activation animation →
   land on the Indus Valley level journey.
4. **(15s)** Open Level 3: "The Water Challenge." Read the scenario, pick a
   choice.
5. **(10s)** Show the Result screen: stats changing, XP increasing, a
   treasure/achievement popup.
6. **(15s)** Click "View Historical Record" — show the scroll UI, and point
   out the clear separation between "gameplay decision" and "historical
   context."
7. **(10s)** Jump ahead (pre-completed account) to show the unlocked
   Civilization Map — click a site marker (Dholavira).
8. **(5s)** Quick look at the Historical Timeline.
9. **(10s)** End on the Hall of Legends leaderboard: "And every future
   historical era — kingdoms, trade, heritage, traditional games — plugs into
   this exact same engine."

---

Built with Flask, SQLite, and a lot of respect for real archaeological
scholarship. Good luck at SIH 2026! 🏺
