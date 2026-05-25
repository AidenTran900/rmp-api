# [rmp-api](https://pypi.org/project/rmp-api/)

A Python library for querying the RateMyProfessors GraphQL API. Search for professors, fetch their ratings, and compute quality signals from the data.

No API key required. No scraping. Requires Python 3.10+.

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
from rmp_api import search_schools, search_professors, get_all_ratings, compute_score

schools = search_schools("UC Berkeley")
school_id = schools[0].id

professors = search_professors("John DeNero", school_id)
professor_id = professors[0].id

ratings = get_all_ratings(professor_id)
score = compute_score(ratings)

print(score.composite_score)     # 0.82
print(score.raw_avg_rating)      # 4.1
print(score.top_tags[:3])        # [('Respected', 14), ('Clear grading', 11), ...]
```

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

## Notes

- Uses RateMyProfessors' public GraphQL endpoint. No auth required.
- This wraps an **unofficial API**!!! It may break if RMP changes their internal schema.
- Ratings are returned newest first.
- Results are cached per process. Call `.cache_clear()` on `search_schools`, `search_professors`, or `get_courses` to invalidate.
- RMP may rate-limit heavy requests. Add `time.sleep(0.5)` between calls when fetching many professors.

---

> Built off [snow4060/rmp-api](https://github.com/snow4060/rmp-api).
