# Models

Dataclasses and enums used throughout the library. Everything here is exported directly from `rmp_api`.

---

## Data flow

Most workflows follow this path:

1. [`search_schools`][rmp_api.client.search_schools] returns `list[`[`SchoolResult`][rmp_api.models.SchoolResult]`]` -- use `school.id` for professor searches.
2. [`search_professors`][rmp_api.client.search_professors] returns `list[`[`ProfessorResult`][rmp_api.models.ProfessorResult]`]` -- use `professor.id` for rating fetches.
3. [`get_professor_summary`][rmp_api.client.get_professor_summary] returns a [`ProfessorRating`][rmp_api.models.ProfessorRating] with aggregated stats.
4. [`get_all_ratings`][rmp_api.client.get_all_ratings] / [`get_ratings_page`][rmp_api.client.get_ratings_page] return `list[`[`Rating`][rmp_api.models.Rating]`]` with individual student reviews.
5. [`compute_score`][rmp_api.scoring.score.compute_score] takes `list[Rating]` and returns a [`ProfessorScore`][rmp_api.models.ProfessorScore].
6. [`compare_professors`][rmp_api.scoring.score.compare_professors] takes multiple `list[Rating]` inputs and returns a [`ProfessorComparison`][rmp_api.models.ProfessorComparison].
7. [`compute_score_over_time`][rmp_api.scoring.score.compute_score_over_time] returns a [`ScoreTimeline`][rmp_api.models.ScoreTimeline].
8. [`compute_split_score`][rmp_api.scoring.score.compute_split_score] returns a [`SplitScore`][rmp_api.models.SplitScore].

---

## Sentinel values

`ProfessorRating` uses sentinel values when no professor is found:

- `avg_rating`, `avg_difficulty`, `would_take_again_percent` are set to `-1`
- `num_ratings` is set to `0`
- `link` is set to `""`

Always check `num_ratings > 0` before using a `ProfessorRating`'s numeric fields.

`ProfessorScore` uses `0` as a sentinel (returned when `compute_score` receives an empty list).

---

## Reference

::: rmp_api.models
    options:
      show_source: false
