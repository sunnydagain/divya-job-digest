from .job import Job


def max_possible_score(criteria: dict) -> int:
    """Highest score a single job could theoretically earn under this rubric.
    Top tier + all title signals + all description signals + all location signals.
    Re-derived from criteria.yml so it stays accurate if Divya tunes the bags."""
    tier_max = max((criteria.get("tier_points") or {}).values(), default=0)
    title_max = sum(s.get("points", 0) for s in (criteria.get("title_signals") or []))
    desc_max = sum(s.get("points", 0) for s in (criteria.get("description_signals") or []))
    loc_max = sum(s.get("points", 0) for s in (criteria.get("location_signals") or []))
    return tier_max + title_max + desc_max + loc_max


def build_firms_index(firms_config: dict) -> dict[str, str]:
    """Map lowercased firm name -> tier key (tier_1, tier_2, ...)."""
    index: dict[str, str] = {}
    for tier, firms in firms_config.items():
        if not isinstance(firms, list):
            continue
        for firm in firms:
            name = (firm.get("name") or "").lower().strip()
            if name:
                index[name] = tier
    return index


def _tier_for(company: str, firms_index: dict[str, str]) -> str | None:
    c = (company or "").lower()
    for name, tier in firms_index.items():
        if name and name in c:
            return tier
    return None


def _any_keyword(text: str, keywords: list[str]) -> bool:
    t = text.lower()
    return any(k.lower() in t for k in keywords)


def score(job: Job, criteria: dict, firms_index: dict[str, str]) -> tuple[int, list[str]]:
    points = 0
    signals: list[str] = []

    # Tier (use job.tier if set by source; otherwise look up by company name)
    tier = job.tier or _tier_for(job.company, firms_index)
    tier_points = (criteria.get("tier_points") or {})
    if tier and tier in tier_points:
        pts = tier_points[tier]
        points += pts
        signals.append(f"{tier.replace('_', ' ').title()} firm")
        job.tier = tier

    # Title signals
    for sig in criteria.get("title_signals") or []:
        if _any_keyword(job.title, sig["keywords"]):
            points += sig["points"]
            signals.append(sig["label"])

    # Description signals
    for sig in criteria.get("description_signals") or []:
        if _any_keyword(job.description, sig["keywords"]):
            points += sig["points"]
            signals.append(sig["label"])

    # Location signals
    for sig in criteria.get("location_signals") or []:
        if _any_keyword(job.location, sig["keywords"]):
            points += sig["points"]
            signals.append(sig["label"])

    return points, signals
