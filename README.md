# [rmp-api](https://github.com/AidenTran900/rmp-api)

An UNOFFICIAL Python library for querying the RateMyProfessors GraphQL API. Search for professors, fetch their ratings, and compute quality signals from the data.

---

## What it does

- Search for schools and professors by name
- Fetch individual student ratings with comments, grades, tags, and difficulty scores
- Compute quality signals: recency-weighted rating, reliability score, easiness, would-take-again rate
- Compare multiple professors side-by-side on any signal
- Track how a professor's score has changed over time (by year, semester, or quarter)
- Filter ratings by course code, keyword, or delivery format

---

## Documentation

Full docs at **[docs.aidentran.dev/rmp-api/](https://docs.aidentran.dev/rmp-api/)** (Getting Started, API Reference, Examples, Troubleshooting).

---

## Installation

```bash
pip install rmp-api
```

Or with `uv`:

```bash
uv add rmp-api
```

Or clone and install locally:

```bash
git clone https://github.com/AidenTran900/rmp-api.git
cd rate-my-prof-api
pip install -e .
```

---

## Quick start

```python
from rmp_api import (
    search_schools,
    search_professors,
    get_professor_summary,
    get_all_ratings,
    get_courses,
    filter_ratings_by_keywords,
    compute_score,
)

# 1. Find a school
schools = search_schools("UC Berkeley")
school_id = schools[0].id

# 2. Find a professor
professors = search_professors("John DeNero", school_id)
professor_id = professors[0].id

# 3. Quick aggregate summary (single request, no pagination)
summary = get_professor_summary("John DeNero", school_id)
print(summary.avg_rating)               # 4.2
print(summary.avg_difficulty)           # 2.8
print(summary.would_take_again_percent) # 92.0
print(summary.link)                     # https://www.ratemyprofessors.com/professor/...

# 4. Courses taught
courses = get_courses(professor_id)
print(courses[:3])  # [{'courseName': 'CS61A', 'courseCount': 42}, ...]

# 5. All ratings (auto-paginated); filter to a course
ratings = get_all_ratings(professor_id, course_filter="CS61A")

# 6. Filter by keyword
hard_ratings = filter_ratings_by_keywords(ratings, "hard")

# 7. Compute quality signals
score = compute_score(ratings)
print(score.composite_score)  # 0.82
print(score.raw_avg_rating)   # 4.1
print(score.top_tags[:3])     # [('Respected', 14), ('Clear grading', 11), ...]
```

---


## Notes

- Uses RateMyProfessors' public GraphQL endpoint. No auth required.
- This wraps an **unofficial API**!!! It may break if RMP changes their internal schema.
- Ratings are returned newest first.
- Results are cached per process. Call `.cache_clear()` on `search_schools`, `search_professors`, or `get_courses` to invalidate.
- RMP may rate-limit heavy requests. Add `time.sleep(0.5)` between calls when fetching many professors.

---

> Built off [snow4060/rmp-api](https://github.com/snow4060/rmp-api).
