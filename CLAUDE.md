# CLAUDE.md — Divya's Job Search Automation

Act like a CTO - be the complete technical owner. Don't be a people pleaser. Ask clarifying questions. Be very careful that everything (except claude pro) is in free tier. It is critical important that this remains as a free project.

## Working rules

The four rules below are derived from Andrej Karpathy's observations on common LLM coding failure modes (popularised in the Forrest Chang CLAUDE.md). They apply throughout this project.

1. **Think before coding.** State assumptions out loud. When a request has multiple plausible interpretations, list them and ask. Do not silently pick one and run with it.
2. **Simplicity first.** Write the minimum code that solves the stated problem. No unrequested abstractions, no speculative features, no "future-proofing" that wasn't asked for.
3. **Surgical changes.** Touch only what the current task requires. Every changed line should trace directly to the ask. No drive-by refactors, no opportunistic cleanups.
4. **Goal-driven execution.** Before starting any task, convert it into a verifiable success criterion. "Fix the email formatting" becomes "the email renders with each job's title, firm, link, and one-line fit summary, verified by a test run."
5. **Self-update at end of session.** Before ending the conversation, edit the **Session log** and **Build order** sections of this file to reflect what was actually accomplished. Append a new dated entry to the Session log (one or two lines, what happened + open thread). Tick or untick checkboxes in Build order to match reality. This is how the next session starts already in context instead of re-asking what's done.

Keep this file under \~250 lines. Keep instructions specific. Surface contradictions when you find them.

## Session log

Most recent first. One entry per session, dated, ≤2 lines. Update at end of each session per Working Rule #5.

- **2026-05-24 (Tier 1 ATS sweep)** — Investigated all 9 Tier 1 firms' careers pages via WebSearch + WebFetch + curl. Added BambooHR support to `src/sources/firms.py` (public JSON endpoint at `<slug>.bamboohr.com/careers/list`). Confirmed: LeapFrog (BambooHR, slug `leapfrog`) and BlueOrchard (BambooHR, slug `blueorchard`, 4 open roles today). Helios explicitly tagged `workday` (skipped). Five firms (Actis, DPI, AfricInvest, Climate Fund Managers, Ninety One, Cordiant) stay `unknown` — Actis migrated to General Atlantic post-acquisition with JS-rendered postings; others have either no public ATS or aggressive scraping blocks. Commit `4ab3b36`. **Score normalised to 0–100** earlier this session (commit `5d1dc5d`); **dedupe now strips legal-form suffixes** (Ltd/LLP/Inc/etc., commit `8cff1cc`). **Open thread:** workflow re-trigger to see Climate17 dedup'd + new BambooHR firms surface.
- **2026-05-24 (after first run)** — First digest landed with 5 matches (Climate17 ×2, BlackRock, etc.). Three email tweaks shipped (commit `cf167b2`): (1) score normalised to /100; (2) Adzuna salary captured and rendered when present; (3) header clarifies whether the 10-cap was hit.
- **2026-05-24 (end of day)** — First manual workflow run on GitHub Actions succeeded. v1 is live; the daily cron at 19:00 UTC will now run unattended. CLAUDE.md was moved into the repo root and is committed publicly per Divya's call (commit `ffa8fac`).
- **2026-05-24 (later)** — Pushed v1 build to GitHub via git (init → commit → merge unrelated histories with `-X ours` → push). Remote is `https://github.com/sunnydagain/divya-job-digest`, branch `main`, commit `b1b2a0e`. CLAUDE.md "How to work with Divya" section rewritten: Claude now drives the terminal directly (git, gh, etc.) rather than walking her through browser clicks.
- **2026-05-24** — Wrote the entire v1 codebase locally at `divya-job-digest/` (13 files: src + config + workflow + README). All Python and YAML drafted from CLAUDE.md spec.

## Project goal

Build a fully free, fully automated daily job-search digest for Divya Samtani. A scheduled job runs at 19:00 Europe/London every day, gathers private credit and private equity roles matching her criteria, filters them, ranks the top 10, and emails her the digest. Everything must work on free tiers — GitHub Actions for hosting, free API tiers for data, Gmail SMTP for delivery. No paid services.

## About the user

Divya Samtani is the *end user* and the *builder* of this project. She is currently Investment Director at Cygnum Capital Group (AfricaGoGreen Fund) in London. CFA charterholder, MSc from Bayes Business School (Distinction). Recent transactions in e-mobility, green buildings, and energy efficiency across Africa, with ticket sizes of $3M–$18M.

She is non-technical (no GitHub UI familiarity yet, no Python experience), but she runs Claude Code locally and is happy for Claude to drive the terminal directly. **Use git freely** — `git init`, `git add`, `git commit`, `git remote`, `git push` are all fair game. Same for any other CLI work that gets the job done faster than browser clicks. She doesn't need to learn the commands; she just wants the result. Only fall back to "click here, then here" instructions when something genuinely requires the browser (e.g. setting GitHub secrets, generating an OAuth token, viewing Actions logs).

## Search criteria

**Must-have (hard filters):**

* UK-based role (London preferred, broader UK acceptable)
* Employer on the UK Visa Sponsor Register (gov.uk/government/publications/register-of-licensed-sponsors-workers)
* Seniority: AVP, VP, Director, Principal, or similar mid-senior level
* NOT in the exclusions list below

**Strong preference:**

* Asset class: private credit, private equity, infrastructure debt/equity
* Sector: climate, sustainability, energy transition, ESG-led, Real estate
* Geography exposure: emerging markets, Africa, Asia

**Nice to have:**

* Real estate / real assets where private credit skills transfer
* EM debt or impact credit roles

## Exclusions (hard filter — never surface these employers)

Current employer:

* Cygnum Capital Group (any subsidiary or fund)

AGG (Africa Go Green Fund) limited partners — applying to these would be a conflict given Divya's current role:

* British International Investment (BII)
* KfW
* DEG (KfW subsidiary)
* International Finance Corporation (IFC)
* African Development Bank (AfDB)
* Sustainable Energy Fund for Africa (SEFA)
* Nordic Development Fund (NDF)
* Calvert Impact Capital
* OEEB (Austrian Development Bank)
* responsAbility (M\&G)

Match employer names case-insensitively with substring matching. When uncertain whether a hit qualifies (e.g., a JV partly owned by an excluded entity), drop it — false negatives are cheap, false positives are not.

## Data sources

1. **Adzuna API** (developer.adzuna.com) — free tier, \~1,000 calls/month, structured UK job data. Primary aggregator.
2. **Climatebase** (climatebase.org) — climate jobs, public listings, light HTML fetch.
3. **Work on Climate** (workonclimate.org) — climate jobs, similar.
4. **Curated firms list** — see below. Daily HTML fetch of each careers page. Most use Greenhouse, Lever, or Workday — predictable URL structures.

## Curated firms list

**Tier 1 — EM + climate + credit/infra (strongest fit):**

* Actis
* Helios Investment Partners
* Development Partners International (DPI)
* AfricInvest
* LeapFrog Investments
* BlueOrchard Finance (Schroders)
* Climate Fund Managers
* Ninety One
* Cordiant Capital

**Tier 2 — climate infrastructure \& energy transition:**

* Macquarie Asset Management Green Investment Group
* Schroders Greencoat
* Foresight Group
* Quinbrook Infrastructure Partners
* BlackRock Climate Infrastructure (London team)
* Brookfield Global Transition Fund
* Just Climate
* Climate Asset Management (HSBC × Pollination JV)

**Tier 3 — broader sustainable/impact asset managers with private credit arms:**

* Bridges Fund Management
* Federated Hermes
* M\&G Investments
* Aviva Investors
* Generation Investment Management
* Triple Point Investment Management
* Pollination

**Tier 4 — generalist private credit/PE with growing climate strategies (stretch):**

* Ares Management
* Apollo Global Management
* Tikehau Capital (London)
* KKR Global Impact
* EQT Future
* Pantheon Ventures

Divya edits this list via `config/firms\_list.yml`. Tier weighting flows into the scoring rubric.

## Scoring rubric (v1: rule-based, no AI calls)

Each role gets a score from 0–100. Top 10 by score go into the daily email.

|Signal|Points|
|-|-|
|Employer in Tier 1|+30|
|Employer in Tier 2|+20|
|Employer in Tier 3|+15|
|Employer in Tier 4|+10|
|Title contains Director / VP / Vice President / Principal / AVP|+15|
|Description mentions private credit / private debt|+10|
|Description mentions climate / sustainability / energy transition / ESG|+10|
|Description mentions infrastructure|+5|
|Description mentions emerging markets / Africa / Asia / developing|+5|
|Location is London|+5|
|Description mentions CFA or financial modelling|+5|
|Employer on UK Sponsor Register|required (else drop)|
|Employer in exclusions list|required exclusion (drop)|

Sort descending. Cap at 10. If fewer than 10 hits, send what you have with a note.

## Architecture

GitHub Actions, public repo, daily cron. Python script reads sources, applies filters and scoring, sends email via Gmail SMTP.

**Repository structure:**

```
.
├── .github/workflows/daily-digest.yml   # cron at 19:00 Europe/London
├── src/
│   ├── main.py                          # orchestrator
│   ├── sources/
│   │   ├── adzuna.py
│   │   ├── climate\_boards.py
│   │   └── firms.py                     # iterates firms\_list.yml
│   ├── filters.py                       # sponsor register, exclusions
│   ├── scoring.py                       # rubric above
│   └── email\_sender.py                  # Gmail SMTP
├── config/
│   ├── firms\_list.yml                   # editable by Divya
│   ├── exclusions.yml                   # editable by Divya
│   └── criteria.yml                     # keywords, weights
├── requirements.txt
└── README.md
```

**Secrets in GitHub Actions (Settings → Secrets and variables → Actions):**

* `ADZUNA\_APP\_ID`
* `ADZUNA\_APP\_KEY`
* `GMAIL\_USER` — Divya's Gmail address
* `GMAIL\_APP\_PASSWORD` — 16-char app password from Google account
* `RECIPIENT\_EMAIL` — same as `GMAIL\_USER` (sending to herself)

No secrets in code. Public repo is fine; secrets live only in Actions secrets.

## Email format

HTML, with plain-text fallback. Subject: `Daily job digest — N matches — {date}`.

Body: numbered list. Each entry:

* Role title, linked to the posting
* Firm name and tier
* Location
* Posted date
* Score
* One-line fit summary derived from which signals fired (e.g., "Tier 1 firm, Director-level, mentions private credit and climate")

## Build order

Walk Divya through these in sequence. Verify each step before moving on.

1. ~~GitHub account, verified email.~~ ✓ Done
2. ~~New public repo: `divya-job-digest`. Initialise with README.~~ ✓ Done
3. ~~Register for Adzuna API (developer.adzuna.com). Save App ID and Key.~~ ✓ Done
4. ~~Enable 2FA on her Google account. Generate Gmail app password (Google Account → Security → 2-Step Verification → App passwords).~~ ✓ Done
5. ~~Add the 5 secrets to GitHub Actions.~~ ✓ Done
6. ~~Build the app (write source files locally at `divya-job-digest/`).~~ ✓ Done 2026-05-24
6b. ~~Push to GitHub via git (now lives at `https://github.com/sunnydagain/divya-job-digest`, commit `b1b2a0e`).~~ ✓ Done 2026-05-24
7. ~~Manually trigger the workflow and confirm email arrives.~~ ✓ Done 2026-05-24
8. ~~Daily cron is now live (19:00 UTC) — no further action needed.~~ ✓ v1 SHIPPED

## What to do next (post-v1)

v1 is running. The next useful work, in priority order:

1. **Fill in firm ATS slugs.** `config/firms_list.yml` ships with every firm marked `ats: unknown`, so the curated-firms source produces nothing. Each slug is a 30-second lookup (visit careers page → read the URL pattern). Highest leverage upgrade.
2. **Tune the scoring/keyword bags.** After a week of digests, look for false positives and false negatives — adjust `config/criteria.yml`.
3. **Workday support** for the firms whose careers pages live on Workday (Brookfield, KKR, etc.). Per-tenant URL discovery needed.
4. Then the items under "Future upgrades" below.

### Build artifacts (current state of the codebase)

Files exist locally at `Desktop\Misc\Claudy\divya-job-digest\`. Structure:

```
divya-job-digest/
├── .github/workflows/daily-digest.yml   # cron 0 19 * * * UTC + workflow_dispatch
├── src/
│   ├── __init__.py
│   ├── main.py                          # orchestrator: load → fetch → filter → score → email
│   ├── job.py                           # Job dataclass
│   ├── filters.py                       # exclude_by_employer, filter_uk, filter_seniority, dedupe
│   ├── scoring.py                       # rubric per criteria.yml, returns (score, signals)
│   ├── email_sender.py                  # Gmail SMTP (SSL 465), HTML + text
│   └── sources/
│       ├── __init__.py
│       ├── adzuna.py                    # 3 query passes against /v1/api/jobs/gb/search/1
│       ├── climate_boards.py            # Climatebase + Work on Climate (best-effort HTML)
│       └── firms.py                     # Greenhouse + Lever public APIs; Workday skipped
├── config/
│   ├── firms_list.yml                   # all 30 firms; ats=unknown, slug=null (fill in later)
│   ├── exclusions.yml                   # Cygnum + 10 AGG LPs
│   └── criteria.yml                     # tier_points, title/description/location signals, uk_locations, seniority_terms
├── requirements.txt                     # requests, beautifulsoup4, PyYAML
└── README.md                            # manual-trigger + edit instructions
```

**v1 deviations from the original spec (worth knowing):**
- Sponsor-register check is loose: not enforced in code. Email footer reminds Divya to verify on gov.uk before applying.
- Workday firms are skipped (each tenant is bespoke; defer to v1.1).
- All curated firms ship with `ats: unknown` because slugs need manual verification from each firm's careers-page URL. Until filled in, Adzuna is the main source.
- Cron is `0 19 * * *` UTC — drifts by an hour during British Summer Time. Accepted in v1.

## How to work with Divya

* **Drive the terminal yourself.** Use git, gh, npm, python, whatever — don't make her type commands she doesn't understand. She has Claude Code locally and is happy for Claude to run things.
* Explain every concept the first time it appears — "secret", "workflow", "cron", "SMTP", "remote" each need one line of context.
* Browser steps are still needed for: setting GitHub Actions secrets, OAuth/2FA flows, reading Actions run logs, editing settings only the web UI exposes. Give click paths for those.
* Confirm a step landed by checking the result yourself (e.g. `git status`, `git log`, `gh run list`) rather than asking her to read screens.
* If something fails, fix it — don't make her debug. Read the logs, propose the fix, apply it.

## Future upgrades (not for v1)

* Optional Anthropic API scoring layer: set `ANTHROPIC\_API\_KEY`; if present, an LLM re-ranks the top 25 candidates against her CV.
* Weekly Sunday summary aggregating the week's best matches.
* Slack or Telegram delivery alternatives.
* LinkedIn jobs (deferred — fragile, high maintenance).
* Feedback loop: 👍/👎 ratings adjust weights over time.

Out of scope until she has run v1 for at least two weeks.

