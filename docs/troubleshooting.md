# Troubleshooting

Common problems and how to fix them.

---

## Search returns no results

**Symptom:** `search_professors` or `search_schools` returns an empty list.

**Causes:**
- The name is misspelled or abbreviated differently than RMP stores it
- The school doesn't exist in RMP's database
- The professor hasn't been rated at that school yet

**Fix:** Try a shorter search string. RMP's search is partial-match, so `"DeNero"` will find `"John DeNero"` even without the first name. Also try common abbreviations: `"UC Berkeley"` vs `"University of California Berkeley"`.

```python
results = search_schools("Berkeley")   # broader, more likely to match
```

If the school search works but the professor search returns nothing, the professor may exist at RMP but under a different school entry (some campuses have multiple RMP entries).

---

## Search returns the wrong professor

**Symptom:** The first result is not the professor you want.

**Cause:** RMP's search ranking isn't exact. If a school has multiple professors with similar names, or the name is common, you may get the wrong one.

**Fix:** Check the result before using it:

```python
results = search_professors("Smith", school_id)
for result in results:
    print(result.first_name, result.last_name, result.department)
```

Pick the correct entry by index or by checking the department.

---

## `get_professor_summary` returns -1 values

**Symptom:** `summary.avg_rating` is `-1`, `summary.num_ratings` is `0`.

**Cause:** `get_professor_summary` returns a sentinel object when `search_professors` finds no match. This is not an error -- it just means no professor was found.

**Fix:** Always check `num_ratings` before using the other fields:

```python
summary = get_professor_summary("Some Prof", school_id)

if summary.num_ratings == 0:
    print("Not found on RMP")
else:
    print(summary.avg_rating)
```

---

## `would_take_again_percent` is -1 or 0

**Symptom:** `summary.would_take_again_percent` comes back as `-1` even when the professor has many ratings.

**Cause:** RMP only records would-take-again responses for ratings submitted after they added that feature. If many of the professor's reviews are old, there may not be enough responses to display the metric.

This is a data gap in RMP's system, not a library bug. The sentinel value `-1` means "not enough data", distinct from `0` which would mean "0% would take again."

**Workaround:** Use `compute_score(ratings).would_take_again_pct` instead, which computes this from the individual rating objects and uses whatever responses are available:

```python
score = compute_score(get_all_ratings(professor_id))
print(score.would_take_again_pct)  # 0.0 if no responses, not -1
```

---

## `get_all_ratings` returns an empty list

**Symptom:** `get_all_ratings(professor_id)` returns `[]` even though the professor has ratings on the RMP site.

**Likely causes:**

1. **Wrong ID.** Make sure you're passing `professor.id` (the `ProfessorResult` attribute), not something else like an integer or a manually constructed string.

   ```python
   results = search_professors("Some Prof", school_id)
   professor_id = results[0].id   # correct -- base64 string from ProfessorResult
   ```

2. **Network failure.** The function returns `[]` on request errors. Check if any error messages were printed to stdout.

3. **Course filter mismatch.** If you passed a `course_filter`, the course code may not match exactly how RMP stores it. Try `get_courses(professor_id)` first to see the exact codes.

   ```python
   courses = get_courses(professor_id)
   print(courses[:5])  # See exact course code strings
   ```

---

## Rate limiting / HTTP 429

**Symptom:** Requests start failing with HTTP 429 errors or connection errors after many calls.

**Cause:** RMP's API doesn't publish rate limit numbers, but heavy pagination across many professors will trigger throttling.

**Fix:** Add a sleep between professor fetches:

```python
import time

for professor_id in professor_ids:
    ratings = get_all_ratings(professor_id)
    # ... do work
    time.sleep(0.5)
```

For very large batches (hundreds of professors), consider 1-2 second delays. The library's `lru_cache` means repeated calls for the same professor don't hit the network again, so caching helps if you query the same professors multiple times.

---

## Network errors / connection failures

**Symptom:** Functions return `None` or `[]` and print an error like `Error searching school: ...` or `Error fetching ratings: ...`.

**Cause:** The library catches all exceptions from the network layer and returns safe sentinel values rather than raising. The error is printed to stdout.

**Fix:** Check your network connection. If the issue is intermittent, it's likely a transient failure from the RMP server. Retry after a few seconds.

---

## Stale cached results

**Symptom:** You're seeing old data even after a professor's rating count changed.

**Cause:** `search_schools`, `search_professors`, `get_courses`, and the internal ratings paginator are all `lru_cache`-decorated. The cache lives for the duration of the Python process.

**Fix:** Clear the relevant cache:

```python
from rmp_api.client import (
    search_schools,
    search_professors,
    get_courses,
    _fetch_all_ratings_cached,
)

search_schools.cache_clear()
search_professors.cache_clear()
get_courses.cache_clear()
_fetch_all_ratings_cached.cache_clear()
```

Or just restart your process. The cache doesn't persist between runs.

---

## `compute_score` returns all zeros

**Symptom:** `compute_score(ratings)` returns a `ProfessorScore` with `composite_score = 0.0` and all other fields at `0`.

**Cause:** You passed an empty list. `compute_score([])` returns a zero-valued sentinel.

**Fix:** Check that `get_all_ratings` returned something before scoring:

```python
ratings = get_all_ratings(professor_id)

if not ratings:
    print("No ratings found")
else:
    score = compute_score(ratings)
```

---

## `compute_score_over_time` raises ValueError

**Symptom:** `ValueError: period must be one of ...`

**Cause:** You passed an invalid string to the `period` argument.

**Fix:** Use `TimePeriod` enum values or their exact string equivalents:

```python
from rmp_api import TimePeriod

timeline = compute_score_over_time(ratings, period=TimePeriod.YEAR)
# or
timeline = compute_score_over_time(ratings, period="year")
# Valid strings: "year", "semester", "quarter"
```

---

## `compare_professors` raises ValueError

**Symptom:** `ValueError: sort_by must be one of ...`

**Cause:** You passed an invalid string to `sort_by`.

**Fix:** Use `SortBy` enum values:

```python
from rmp_api import SortBy, compare_professors

comparison = compare_professors(professors, sort_by=SortBy.EASINESS_SCORE)
```

Run `list(SortBy)` to see all valid options.
