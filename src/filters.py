import logging
import re

from .job import Job

log = logging.getLogger(__name__)

# Trailing legal-form suffixes that should NOT change a firm's identity for dedupe purposes.
# Strictly legal forms only — "Group", "Partners", "Capital", "Holdings" are name parts
# (Cygnum Capital, Development Partners International, etc.) and must NOT be stripped.
# Longer alternatives come first so "incorporated" matches before "inc".
_CORP_SUFFIX_RE = re.compile(
    r"[\s,.\-]*\b(?:incorporated|corporation|limited|gmbh|sarl|llp|llc|inc|ltd|plc|corp)\b\.?",
    flags=re.IGNORECASE,
)


def _norm_company(name: str) -> str:
    """Lowercase, trim, and strip trailing corporate suffixes for dedupe keys only.
    Display still uses the original name."""
    n = (name or "").lower().strip()
    for _ in range(4):  # strip stacked suffixes like "Co., Ltd"
        new = _CORP_SUFFIX_RE.sub("", n).strip(" ,.–-")
        if new == n or not new:
            break
        n = new
    return n


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
        key = (_norm_company(j.company), (j.title or "").lower().strip())
        if key in seen:
            log.info("Dedup'd: %s @ %s", j.title, j.company)
            continue
        seen.add(key)
        out.append(j)
    return out
