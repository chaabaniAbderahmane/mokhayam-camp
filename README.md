# 🏕️ المخيم الصيفي — Camp Management App

Bilingual (Arabic default / French) mobile-first Streamlit app for managing a summer camp:
participants, rooms/places, attendance, payments, transport, announcements, QR participant
cards, and a private participant portal — all from your phone.

## Files
```
mokhayam/
├── app.py              # main app + routing (admin dashboard / participant portal)
├── db.py                # SQLAlchemy models + database setup (SQLite)
├── translations.py      # AR/FR dictionary (single source of truth for all text)
├── styles.py             # mobile-first CSS + Palestinian-inspired visual identity
├── utils.py              # QR code generation + Excel/CSV export
├── requirements.txt
├── .streamlit/config.toml
└── .gitignore
```

## Default login
- Username: `admin`
- Password: `admin123`

**Change this password immediately after first login is not built as a self-service
"change password" screen yet** — for now, go to "المسؤولون" (super admin only), add a new
super-admin account with a strong password, log in with it, then delete the default `admin`
account.

---

## 🚀 Deploy from your phone (no computer needed)

The easiest free option is **Streamlit Community Cloud**, which deploys straight from a
GitHub repo — both GitHub and Streamlit Cloud work fine in your phone's browser.

### Step 1 — Put the files on GitHub
1. Open **github.com** in your phone browser and sign in (create a free account if needed).
2. Tap **+ → New repository**. Name it e.g. `mokhayam-camp`. Make it **Public** (required for
   the free tier) or Private if you have Streamlit Cloud access to private repos. Create it.
3. Tap **Add file → Upload files**, and upload every file from this project
   (`app.py`, `db.py`, `translations.py`, `styles.py`, `utils.py`, `requirements.txt`,
   `.gitignore`, and the `.streamlit/config.toml` — for that last one, create the folder by
   naming the uploaded file `.streamlit/config.toml`, GitHub will create the folder automatically).
4. Commit the files (green **Commit changes** button).

### Step 2 — Deploy on Streamlit Community Cloud
1. Go to **share.streamlit.io** in your phone browser and sign in with your GitHub account.
2. Tap **Create app → Deploy a public app from GitHub**.
3. Pick your `mokhayam-camp` repository, branch `main`, and set the main file path to `app.py`.
4. Tap **Deploy**. Wait a minute or two while it installs the packages from `requirements.txt`.
5. You'll get a URL like `https://your-app-name.streamlit.app` — this is your live app.

### Step 3 — Finish setup inside the app
1. Open your new URL and log in as admin.
2. Go to **الإعدادات (Settings)** and paste your app URL (e.g.
   `https://your-app-name.streamlit.app`) into **"رابط التطبيق (لِرمز QR)"**. This makes every
   participant's QR code open their portal directly.
3. Go to **المسؤولون (Admins)** and create your own admin account, then remove/replace the
   default one.
4. Go to **معلومات المخيم (Camp Info)** and fill in the program, dates, location, rules, etc.
5. Start adding participants from **المشاركون (Participants)**.

That's it — the whole thing is manageable from your phone from here on.

---

## ⚠️ Important note about the database

This app uses **SQLite**, a single file (`camp.db`) stored on the server's disk. This is
simple and works great for running the camp, but on Streamlit Community Cloud's free tier the
filesystem **is not permanently persistent** — if the app goes to sleep for a long time or is
redeployed/rebooted, the database file can be reset to empty.

To protect your data:
- Use **الإعدادات → تحميل نسخة احتياطية (Settings → Download backup)** regularly (e.g. after
  adding participants, after each attendance day) to download `camp_backup.db` to your phone.
- For a camp you truly can't afford to lose data on, consider upgrading later to a hosted
  database (e.g. a free **Supabase** or **PlanetScale** Postgres/MySQL database) — the code is
  structured with a single database layer (`db.py`), so swapping SQLite for a hosted database
  later only requires changing the connection string, not rewriting the app.

## How the participant portal works
- Every participant gets a unique secret `qr_token`.
- Their personal link is `https://your-app-name.streamlit.app/?p=<token>` — this is exactly
  what's encoded in their QR code (see "QR" tab per participant, or the printable card).
  Scanning it (or opening it) shows **only their own information** — never anyone else's.
- On the login screen there is also a manual "enter code" fallback in case a participant can't
  scan their QR.

## Architecture notes (for future maintenance)
- **All UI text** lives in `translations.py` — add a new key there once, use `L("key")`
  everywhere, and both languages stay in sync automatically.
- **All data access** goes through SQLAlchemy models in `db.py` — one place to change the
  schema or swap databases.
- **Styling** (Palestinian-inspired black/white/green/red identity, RTL/LTR switching,
  mobile-first CSS) is centralized in `styles.py`.
- Business rules enforced in code: exactly 5 rooms, max 10 people/room, unique place numbers
  per room, unique QR tokens & registration IDs, duplicate-phone warnings.
