# divya-job-digest

A free, fully-automated daily job-search digest. Runs on GitHub Actions at 19:00 UK time (give or take an hour for daylight savings), scrapes a few sources, filters and scores roles against Divya's criteria, and emails the top 10.

## What it does each day

1. **Scrapes** three sources:
   - **Adzuna** (UK API): private credit, PE, infrastructure, climate keywords.
   - **Climate job boards**: Climatebase + Work on Climate (light HTML fetch).
   - **Curated firms**: 30+ firms listed in `config/firms_list.yml` whose careers pages run on Greenhouse or Lever (free public APIs).
2. **De-dupes** and **filters**: drops anything from the exclusions list (Cygnum + AGG LPs), anything outside the UK, anything below mid-senior level.
3. **Scores** each role against the rubric in `config/criteria.yml` (tier of firm, title keywords, description keywords, location).
4. **Emails** the top 10 to `RECIPIENT_EMAIL` via Gmail SMTP. If 0 matches, sends an empty-state email so you know the job ran.

## How to trigger a manual run

1. Open the repo on github.com.
2. Click **Actions** in the top bar.
3. In the left sidebar, click **Daily job digest**.
4. Click the **Run workflow** dropdown on the right, then the green **Run workflow** button.
5. Wait \~1 minute, refresh — the run appears at the top. Click it to watch logs.
6. Check your inbox.

## How to edit the firms list

1. Open `config/firms_list.yml` on github.com.
2. Click the pencil icon (✏️ top-right) to edit.
3. Make changes. The most useful edit is filling in `ats:` and `slug:` for firms currently marked `unknown` — see the comments at the top of the file for how.
4. Scroll down, write a short commit message, click **Commit changes**.

The next scheduled run (or manual trigger) picks up the change immediately.

## How to read failures

1. **Actions** tab → click the failing run → click the **digest** job → expand any red step.
2. Most likely culprit: a source returned an unexpected shape. Errors are caught per-source, so one breaking won't kill the email. The empty-state mail tells you what was scanned.

## Secrets the workflow needs

Set in **Settings → Secrets and variables → Actions**:

- `ADZUNA_APP_ID`
- `ADZUNA_APP_KEY`
- `GMAIL_USER`
- `GMAIL_APP_PASSWORD`
- `RECIPIENT_EMAIL`

## What's not in v1

- Aggressive UK Sponsor Register matching (the email reminds you to check manually).
- Workday-based firms (each tenant is a snowflake).
- LinkedIn.
- AI-powered re-ranking against a CV.
- Slack / Telegram delivery.

These are upgrades for once v1 has run for a couple of weeks.
