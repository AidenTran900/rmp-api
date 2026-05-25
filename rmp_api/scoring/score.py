"""
score.py

Main entry point for professor scoring. Orchestrates all signals into a
single ProfessorScore with a composite score.
"""

from ..models import ProfessorScore, Rating, ScoreTimeline, SplitScore
from .helpers import _overall, _parse_date
from .presets import WEIGHT_PRESETS
from .signals import (
    compute_difficulty_histogram,
    compute_easiness_score,
    compute_recency_weighted_rating,
    compute_reliability_score,
    compute_review_velocity,
    compute_tag_frequencies,
)


def compute_score(
    ratings: list[Rating],
    weights: dict[str, float] | None = None,
    half_life_days: float = 365.0,
) -> ProfessorScore:
    """
    Compute all quality signals for a professor from their Rating list.

    Aggregates raw stats, derives recency-weighted and reliability signals,
    then combines them into a single ``composite_score`` in ``[0, 1]``.

    Args:
        ratings: Output of :func:`~client.get_all_ratings` or
            :func:`~client.get_ratings_page`.
        weights: Score component weights. Use a :data:`WEIGHT_PRESETS` entry
            or supply a custom dict with keys
            ``recency_rating``, ``would_take_again``, ``easiness``, ``reliability``.
            Values should sum to ~1.0; composite is clamped to ``[0, 1]``.
            Defaults to ``WEIGHT_PRESETS["overall"]``.
        half_life_days: Recency decay half-life. At ``365`` days, a one-year-old
            rating contributes half the weight of a brand-new one.

    Returns:
        :class:`ProfessorScore` with all signals populated. Returns a
        zero-valued instance if ``ratings`` is empty.
    """
    if weights is None:
        weights = WEIGHT_PRESETS["overall"]

    if not ratings:
        return ProfessorScore(
            num_ratings=0,
            raw_avg_rating=0.0,
            avg_clarity=0.0,
            avg_helpfulness=0.0,
            avg_difficulty=0.0,
            recency_weighted_rating=0.0,
            reliability_score=0.0,
            easiness_score=0.0,
            would_take_again_pct=0.0,
            last_review_date=None,
            review_velocity=0.0,
        )

    n = len(ratings)

    # Raw aggregates
    raw_avg = sum(_overall(r) for r in ratings) / n
    avg_clarity = sum(r.clarity_rating for r in ratings) / n
    avg_helpful = sum(r.helpful_rating for r in ratings) / n
    diff_vals = [r.difficulty_rating for r in ratings if r.difficulty_rating is not None]
    avg_difficulty = sum(diff_vals) / len(diff_vals) if diff_vals else 0.0

    # Derived signals
    recency_rating = compute_recency_weighted_rating(ratings, half_life_days)
    reliability = compute_reliability_score(n)
    easiness = compute_easiness_score(ratings)

    wta_vals = [r.would_take_again for r in ratings if r.would_take_again is not None]
    wta_pct = sum(wta_vals) / len(wta_vals) if wta_vals else 0.0

    # Activity
    dates = [d for r in ratings if r.date and (d := _parse_date(r.date)) is not None]
    last_review = max(dates).strftime("%Y-%m-%d") if dates else None
    velocity = compute_review_velocity(ratings)

    # Composite — normalise recency_rating from [1, 5] to [0, 1] before weighting
    recency_norm = (recency_rating - 1) / 4.0
    composite = (
        weights.get("recency_rating",   0) * recency_norm
        + weights.get("would_take_again", 0) * wta_pct
        + weights.get("easiness",         0) * easiness
        + weights.get("reliability",      0) * reliability
    )
    composite = max(0.0, min(1.0, composite))

    return ProfessorScore(
        num_ratings=n,
        raw_avg_rating=raw_avg,
        avg_clarity=avg_clarity,
        avg_helpfulness=avg_helpful,
        avg_difficulty=avg_difficulty,
        recency_weighted_rating=recency_rating,
        reliability_score=reliability,
        easiness_score=easiness,
        would_take_again_pct=wta_pct,
        last_review_date=last_review,
        review_velocity=velocity,
        top_tags=top_tags[:10] if (top_tags := compute_tag_frequencies(ratings)) else [],
        difficulty_histogram=compute_difficulty_histogram(ratings),
        composite_score=composite,
    )


def compute_score_over_time(
    ratings: list[Rating],
    period: str = "year",
    weights: dict[str, float] | None = None,
    half_life_days: float = 365.0,
) -> ScoreTimeline:
    """
    Bucket ratings by time period and compute a :class:`ProfessorScore` per bucket.

    Useful for detecting whether a professor has improved or declined over time.
    Buckets with zero dated ratings are skipped. Buckets are returned oldest -> newest.

    Args:
        ratings: Output of :func:`~client.get_all_ratings` or similar.
        period: Bucketing granularity. One of:

            * ``"year"``     — annual buckets, labelled ``"2023"``.
            * ``"semester"`` — half-year buckets, labelled ``"2023-Spring"``
              (Jan–Jun) or ``"2023-Fall"`` (Jul–Dec).
            * ``"quarter"``  — quarterly buckets, labelled ``"2023-Q1"`` … ``"2023-Q4"``.

        weights: Passed through to each :func:`compute_score` call.
        half_life_days: Recency decay half-life passed to each :func:`compute_score` call.

    Returns:
        :class:`ScoreTimeline` with ``periods`` sorted oldest -> newest,
        a ``trend`` slope (positive = improving), and ``total_span_years``.
        Returns an empty timeline if no ratings have parseable dates.

    Raises:
        ValueError: If ``period`` is not one of ``"year"``, ``"semester"``, ``"quarter"``.
    """
    valid_periods = {"year", "semester", "quarter"}
    if period not in valid_periods:
        raise ValueError(f"period must be one of {valid_periods!r}, got {period!r}")

    _SEMESTER_ORDER = {"Spring": 0, "Fall": 1}

    def _bucket_key(date_str: str):
        dt = _parse_date(date_str)
        if dt is None:
            return None
        if period == "year":
            return (dt.year,)
        if period == "semester":
            half = "Spring" if dt.month <= 6 else "Fall"
            # use numeric ordinal so sorting is chronological, not alphabetical
            return (dt.year, _SEMESTER_ORDER[half], half)
        # quarter
        q = (dt.month - 1) // 3 + 1
        return (dt.year, q)

    def _bucket_label(key: tuple) -> str:
        if period == "year":
            return str(key[0])
        if period == "semester":
            # key = (year, ordinal, name)
            return f"{key[0]}-{key[2]}"
        return f"{key[0]}-Q{key[1]}"

    # Group ratings by bucket
    buckets: dict[tuple, list[Rating]] = {}
    all_dates = []
    for r in ratings:
        key = _bucket_key(r.date)
        if key is None:
            continue
        buckets.setdefault(key, []).append(r)
        dt = _parse_date(r.date)
        if dt:
            all_dates.append(dt)

    if not buckets:
        return ScoreTimeline(periods=[], trend=0.0, total_span_years=0.0)

    # Sort buckets chronologically
    sorted_keys = sorted(buckets.keys())
    period_scores: list[tuple[str, ProfessorScore]] = [
        (_bucket_label(k), compute_score(buckets[k], weights, half_life_days))
        for k in sorted_keys
    ]

    # Linear trend: slope of composite_score vs. bucket index
    composites = [score.composite_score for _, score in period_scores]
    n = len(composites)
    if n < 2:
        trend = 0.0
    else:
        xs = list(range(n))
        x_mean = sum(xs) / n
        y_mean = sum(composites) / n
        numerator   = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, composites))
        denominator = sum((x - x_mean) ** 2 for x in xs)
        trend = numerator / denominator if denominator else 0.0

    total_span = (max(all_dates) - min(all_dates)).days / 365.25 if len(all_dates) >= 2 else 0.0

    return ScoreTimeline(
        periods=period_scores,
        trend=round(trend, 6),
        total_span_years=round(total_span, 2),
    )


def compute_split_score(
    ratings: list[Rating],
    weights: dict[str, float] | None = None,
    half_life_days: float = 365.0,
) -> SplitScore:
    """
    Compute professor scores split by online vs. in-person delivery format.

    Runs :func:`compute_score` three times — once per subset and once for all
    ratings combined — so each :class:`ProfessorScore` reflects only the
    ratings relevant to that format.

    Args:
        ratings: Output of :func:`~client.get_all_ratings` or
            :func:`~client.get_ratings_page`.
        weights: Passed through to each :func:`compute_score` call. See its
            docs for valid keys and defaults.
        half_life_days: Recency decay half-life passed to each
            :func:`compute_score` call.

    Returns:
        :class:`SplitScore` with ``online``, ``in_person``, and ``combined``
        fields. Subsets with zero ratings return a zero-valued
        :class:`ProfessorScore`.
    """
    online_ratings   = [r for r in ratings if r.is_for_online_class]
    in_person_ratings = [r for r in ratings if not r.is_for_online_class]

    return SplitScore(
        online=compute_score(online_ratings, weights, half_life_days),
        in_person=compute_score(in_person_ratings, weights, half_life_days),
        combined=compute_score(ratings, weights, half_life_days),
    )
