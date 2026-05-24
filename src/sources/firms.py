import logging
import requests

from ..job import Job

log = logging.getLogger(__name__)

HEADERS = {"User-Agent": "divya-job-digest/1.0"}


def fetch(firms_config: dict) -> list[Job]:
    jobs: list[Job] = []
    skipped = 0

    for tier, firms in firms_config.items():
        if not isinstance(firms, list):
            continue
        for firm in firms:
            name = firm.get("name", "")
            ats = (firm.get("ats") or "unknown").lower()
            slug = firm.get("slug")

            if ats in ("unknown", "manual") or not slug:
                skipped += 1
                continue

            try:
                if ats == "greenhouse":
                    jobs.extend(_fetch_greenhouse(name, slug, tier))
                elif ats == "lever":
                    jobs.extend(_fetch_lever(name, slug, tier))
                elif ats == "workday":
                    log.info("Skipping Workday firm %s (not supported in v1)", name)
                else:
                    log.info("Unknown ATS %r for %s", ats, name)
            except Exception as e:
                log.warning("Failed to fetch %s (%s/%s): %s", name, ats, slug, e)

    log.info("Firms: %d jobs (%d firms skipped — no ATS configured)", len(jobs), skipped)
    return jobs


def _fetch_greenhouse(name: str, slug: str, tier: str) -> list[Job]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    data = r.json()

    jobs: list[Job] = []
    for item in data.get("jobs", []):
        jobs.append(
            Job(
                title=item.get("title", "").strip(),
                company=name,
                location=(item.get("location") or {}).get("name", "").strip(),
                url=item.get("absolute_url", ""),
                description=item.get("content", "") or "",
                posted=(item.get("updated_at") or "")[:10],
                source=f"Greenhouse/{slug}",
                tier=tier,
            )
        )
    return jobs


def _fetch_lever(name: str, slug: str, tier: str) -> list[Job]:
    url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    data = r.json()

    jobs: list[Job] = []
    for item in data:
        cats = item.get("categories") or {}
        jobs.append(
            Job(
                title=item.get("text", "").strip(),
                company=name,
                location=cats.get("location", "") or "",
                url=item.get("hostedUrl", ""),
                description=item.get("descriptionPlain", "") or item.get("description", "") or "",
                posted="",
                source=f"Lever/{slug}",
                tier=tier,
            )
        )
    return jobs
