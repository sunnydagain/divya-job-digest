import logging
import requests
from bs4 import BeautifulSoup

from ..job import Job

log = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; divya-job-digest/1.0)",
    "Accept": "text/html,application/xhtml+xml",
}


def fetch() -> list[Job]:
    jobs: list[Job] = []
    for fn in (_fetch_climatebase, _fetch_workonclimate):
        try:
            jobs.extend(fn())
        except Exception as e:
            log.warning("%s failed: %s", fn.__name__, e)
    log.info("Climate boards: %d jobs", len(jobs))
    return jobs


def _fetch_climatebase() -> list[Job]:
    # Climatebase has a public listings page. We do a single page fetch and parse anchors.
    # Light-touch — they may render via JS; if so, we get nothing and move on.
    url = "https://climatebase.org/jobs?l=London&q=&p=0&remote=false"
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    jobs: list[Job] = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/job/" not in href:
            continue
        title = a.get_text(strip=True)
        if not title:
            continue
        full_url = href if href.startswith("http") else "https://climatebase.org" + href
        jobs.append(
            Job(
                title=title,
                company="",  # unknown without deeper fetch
                location="London",  # we filtered by London in the URL
                url=full_url,
                description="",
                posted="",
                source="Climatebase",
            )
        )
    return jobs


def _fetch_workonclimate() -> list[Job]:
    # Work on Climate's public job board lives at workonclimate.org/jobs.
    # Similar best-effort parse.
    url = "https://workonclimate.org/jobs"
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    jobs: list[Job] = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/jobs/" not in href:
            continue
        title = a.get_text(strip=True)
        if not title:
            continue
        full_url = href if href.startswith("http") else "https://workonclimate.org" + href
        jobs.append(
            Job(
                title=title,
                company="",
                location="",
                url=full_url,
                description="",
                posted="",
                source="Work on Climate",
            )
        )
    return jobs
