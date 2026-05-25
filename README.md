# rmp-api

Python wrapper for the RateMyProfessors GraphQL API. Fetch professor ratings, reviews, and computed quality signals.

> Based on [snow4060/rmp-api](https://github.com/snow4060/rmp-api).

---

## Installation

```bash
pip install git+https://github.com/youruser/rate-my-prof-api.git
```

Or clone and install locally:

```bash
git clone https://github.com/youruser/rate-my-prof-api.git
cd rate-my-prof-api
pip install -e .
```

---

## Quick Start

```python
from rmp_api import search_schools, search_professors, get_professor_summary, get_all_ratings, compute_score, WEIGHT_PRESETS

# Find a school
schools = search_schools("UC Berkeley")
school_id = schools[0].id

# Get aggregate stats
summary = get_professor_summary("John DeNero", school_id)
print(summary.avg_rating, summary.link)

# Fetch all individual ratings
professor_id = search_professors("John DeNero", school_id)[0].id
ratings = get_all_ratings(professor_id)

# Compute quality signals
score = compute_score(ratings, weights=WEIGHT_PRESETS["best_teacher"])
print(score.composite_score, score.top_tags)
```

---

## Notes

- No auth required — uses the public GraphQL endpoint.
- Ratings are returned **newest first**.
- `search_schools` and `search_professors` return typed dataclasses. Use `.id` for API calls, `.legacy_id` only for building profile URLs.
- RMP may rate-limit heavy pagination. Add `time.sleep(0.5)` between requests if needed.
