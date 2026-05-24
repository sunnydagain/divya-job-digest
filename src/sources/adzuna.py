import logging
import requests

from ..job import Job

log = logging.getLogger(__name__)

ENDPOINT = "https://api.adzuna.com/v1/api/jobs/gb/search/1"

QUERIES = [
    "private credit OR private debt OR direct lending",
    "private equity OR infrastructure",
    "climate OR sustainability OR energy transition",
]


def fetch(app_id: str, app_key: str) -> list[Job]:
    if not app_id or not app_key:
        log.warning("Adzuna credentials missing — skipping source")
        return []

    jobs: list[Job] = []
    seen_urls: set[str] = set()

    for q in QUERIES:
        params = {
            "app_id": app_id,
            "app_key": app_key,
            "results_per_page": 50,
            "what": q,
            "where": "London",
            "distance": 50,
            "max_days_old": 7,
            "content-type": "application/json",
        }
        try:
            r = requests.get(ENDPOINT, params=params, timeout=20)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            log.warning("Adzuna query %r failed: %s", q, e)
            continue

        for item in data.get("results", []):
            url = item.get("redirect_url") or ""
            if url in seen_urls:
                continue
            seen_urls.add(url)
            jobs.append(
                Job(
                    title=item.get("title", "").strip(),
                    company=(item.get("company") or {}).get("display_name", "").strip(),
                    location=(item.get("location") or {}).get("display_name", "").strip(),
                    url=url,
                    description=item.get("description", "") or "",
                    posted=item.get("created", "")[:10],
                    source="Adzuna",
                )
            )

    log.info("Adzuna: %d jobs", len(jobs))
    return jobs
