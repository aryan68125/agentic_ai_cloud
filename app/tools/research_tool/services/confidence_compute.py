def compute_confidence(sources: list[str]) -> float:
    score = 0.0
    for url in sources:
        if url.endswith(".gov"):
            score += 0.4
        elif ".edu" in url:
            score += 0.3
        elif "wikipedia.org" in url:
            score += 0.25
        else:
            score += 0.15
    return min(score, 1.0)
