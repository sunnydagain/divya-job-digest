import logging

from .job import Job

log = logging.getLogger(__name__)


def exclude_by_employer(jobs: list[Job], exclusions: list[str]) -> list[Job]:
    needles = [x.lower() for x in exclusions if x]
    out = []
    for j in jobs:
        haystack = (j.company or "").lower()
        if any(n in haystack for n in needles):
            log.info("Excluded by employer: %s @ %s", j.title, j.company)
            continue
        out.append(j)
    return out


def filter_uk(jobs: list[Job], uk_locations: list[str]) -> list[Job]:
    needles = [x.lower() for x in uk_locations if x]
    out = []
    for j in jobs:
        loc = (j.location or "").lower()
        if not loc:
            # Climate board jobs often lack location — keep them, scoring won't reward them
            out.append(j)
            continue
        if any(n in loc for n in needles):
            out.append(j)
    return out


def filter_seniority(jobs: list[Job], seniority_terms: list[str]) -> list[Job]:
    needles = [x.lower() for x in seniority_terms if x]
    out = []
    for j in jobs:
        title = (j.title or "").lower()
        if any(n in title for n in needles):
            out.append(j)
    return out


def dedupe(jobs: list[Job]) -> list[Job]:
    seen = set()
    out = []
    for j in jobs:
        key = ((j.company or "").lower().strip(), (j.title or "").lower().strip())
        if key in seen:
            continue
        seen.add(key)
        out.append(j)
    return out
