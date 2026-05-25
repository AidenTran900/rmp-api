# Scoring

Functions for computing quality signals and comparing professors. All take `list[Rating]` as input (from `get_all_ratings`) and return typed dataclasses.

---

## Weight presets

`WEIGHT_PRESETS` is a dict of named weight configurations for `compute_score`. Pass any entry directly to the `weights` parameter:

```python
from rmp_api import WEIGHT_PRESETS, compute_score

score = compute_score(ratings, weights=WEIGHT_PRESETS["best_teacher"])
```

| Key | What it emphasizes |
|-----|---------------------|
| `"overall"` | Balanced default |
| `"best_teacher"` | Teaching quality; ignores difficulty |
| `"easiest"` | Easiness (low difficulty) |
| `"rigorous"` | Harder courses score higher (negative easiness weight) |

## Custom weights

Supply any subset of these keys. Missing keys default to `0`. Values should sum to approximately `1.0`. The resulting `composite_score` is clamped to `[0, 1]`.

```python
score = compute_score(ratings, weights={
    "recency_rating":   0.4,
    "would_take_again": 0.3,
    "easiness":         0.2,
    "reliability":      0.1,
})
```

Custom weights only affect `composite_score`. All other signals (`raw_avg_rating`, `reliability_score`, etc.) are always computed regardless of weights.

---

## Sorting and comparison

When using [`compare_professors`][rmp_api.scoring.score.compare_professors], pass a [`SortBy`][rmp_api.models.SortBy] enum value or its string equivalent to choose the ranking field. Higher values always rank first -- to rank by easiness, use `SortBy.EASINESS_SCORE` rather than `SortBy.AVG_DIFFICULTY`.

```python
from rmp_api import SortBy, compare_professors

comparison = compare_professors(professors, sort_by=SortBy.WOULD_TAKE_AGAIN_PCT)
```

---

## Reference

::: rmp_api.scoring.score
    options:
      members:
        - compute_score
        - compute_score_over_time
        - compute_split_score
        - compare_professors
      show_source: false

---

::: rmp_api.scoring.presets
    options:
      show_source: false

---

::: rmp_api.scoring.signals
    options:
      show_source: false
