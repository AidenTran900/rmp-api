"""Named weight configurations for `compute_score`. Pass a preset to `weights=`, or build a custom dict with the same keys."""

WEIGHT_PRESETS: dict[str, dict[str, float]] = {
    # Balanced default
    "overall": {
        "recency_rating":   0.35,
        "would_take_again": 0.30,
        "easiness":         0.15,
        "reliability":      0.20,
    },
    # Prioritises easy grades
    "easiest": {
        "recency_rating":   0.20,
        "would_take_again": 0.20,
        "easiness":         0.45,
        "reliability":      0.15,
    },
    # Prioritises teaching quality; ignores difficulty
    "best_teacher": {
        "recency_rating":   0.50,
        "would_take_again": 0.35,
        "easiness":         0.00,
        "reliability":      0.15,
    },
    # Harder courses score higher (negative easiness weight)
    "rigorous": {
        "recency_rating":   0.40,
        "would_take_again": 0.30,
        "easiness":         -0.10,
        "reliability":      0.20,
    },
}
"""Named weight configurations for [`compute_score`][rmp_api.scoring.score.compute_score].

Each value is a dict of component weights (``recency_rating``, ``would_take_again``,
``easiness``, ``reliability``). Pass an entry to the ``weights`` parameter, or build a
custom dict with the same keys.

Presets:
    overall:      Balanced default.
    easiest:      Prioritises low difficulty (high easiness weight).
    best_teacher: Prioritises teaching quality; ignores difficulty.
    rigorous:     Rewards harder courses (negative easiness weight).
"""
