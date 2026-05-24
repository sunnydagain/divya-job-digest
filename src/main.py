import logging
import os
import sys
from pathlib import Path

import yaml

from .filters import dedupe, exclude_by_employer, filter_seniority, filter_uk
from .job import Job
from .scoring import build_firms_index, max_possible_score, score
from .sources import adzuna, climate_boards, firms as firms_source
from . import email_sender

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger("main")

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config"


def _load_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> int:
    firms_cfg = _load_yaml(CONFIG / "firms_list.yml")
    exclusions_cfg = _load_yaml(CONFIG / "exclusions.yml")
    criteria_cfg = _load_yaml(CONFIG / "criteria.yml")

    adzuna_id = os.environ.get("ADZUNA_APP_ID", "")
    adzuna_key = os.environ.get("ADZUNA_APP_KEY", "")
    gmail_user = os.environ.get("GMAIL_USER", "")
    gmail_pw = os.environ.get("GMAIL_APP_PASSWORD", "")
    recipient = os.environ.get("RECIPIENT_EMAIL", gmail_user)

    if not gmail_user or not gmail_pw:
        log.error("Missing Gmail credentials — cannot send email")
        return 1

    # Gather
    all_jobs: list[Job] = []
    sources_scanned: list[str] = []

    try:
        a = adzuna.fetch(adzuna_id, adzuna_key)
        all_jobs.extend(a)
        sources_scanned.append(f"Adzuna ({len(a)})")
    except Exception as e:
        log.exception("Adzuna source failed: %s", e)
        sources_scanned.append("Adzuna (failed)")

    try:
        c = climate_boards.fetch()
        all_jobs.extend(c)
        sources_scanned.append(f"Climate boards ({len(c)})")
    except Exception as e:
        log.exception("Climate boards source failed: %s", e)
        sources_scanned.append("Climate boards (failed)")

    try:
        f = firms_source.fetch(firms_cfg)
        all_jobs.extend(f)
        sources_scanned.append(f"Curated firms ({len(f)})")
    except Exception as e:
        log.exception("Curated firms source failed: %s", e)
        sources_scanned.append("Curated firms (failed)")

    log.info("Total raw jobs: %d", len(all_jobs))

    # Count how many firms had no ATS slug — useful in the empty-state email
    firms_skipped = sum(
        1
        for tier_firms in firms_cfg.values()
        if isinstance(tier_firms, list)
        for f in tier_firms
        if (f.get("ats") or "unknown").lower() in ("unknown", "manual") or not f.get("slug")
    )

    # Filter
    jobs = dedupe(all_jobs)
    log.info("After dedupe: %d", len(jobs))

    jobs = exclude_by_employer(jobs, exclusions_cfg.get("exclusions") or [])
    log.info("After exclusions: %d", len(jobs))

    jobs = filter_uk(jobs, criteria_cfg.get("uk_locations") or [])
    log.info("After UK filter: %d", len(jobs))

    jobs = filter_seniority(jobs, criteria_cfg.get("seniority_terms") or [])
    log.info("After seniority filter: %d", len(jobs))

    # Score — raw points first, then normalise to 0–100 against the rubric ceiling
    # so the number is comparable across config tweaks.
    firms_index = build_firms_index(firms_cfg)
    max_raw = max_possible_score(criteria_cfg) or 1  # guard against div-by-zero
    for j in jobs:
        raw, j.signals = score(j, criteria_cfg, firms_index)
        j.score = round(raw * 100 / max_raw)

    jobs.sort(key=lambda x: x.score, reverse=True)
    top = jobs[:10]
    log.info("Top %d to send", len(top))
    for j in top:
        log.info("  %d  %s @ %s  [%s]", j.score, j.title, j.company, j.source)

    # Send
    email_sender.send(
        top,
        sources_scanned=sources_scanned,
        firms_skipped=firms_skipped,
        gmail_user=gmail_user,
        gmail_pw=gmail_pw,
        recipient=recipient,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
