"""
presets.py

Named weight configurations for compute_score.
Pass a preset to the `weights` argument, or build a custom dict with the same keys.
"""

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
