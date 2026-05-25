# rmp-api

A Python library for querying the RateMyProfessors GraphQL API. Search for professors, pull their ratings, and compute quality signals from the data.


---

## Install

```bash
pip install git+https://github.com/youruser/rate-my-prof-api.git
```

Requires Python 3.10+.

---

## Example

```python
from rmp_api import search_schools, search_professors, get_all_ratings, compute_score

schools = search_schools("UC Berkeley")
school_id = schools[0]["node"]["id"]

professors = search_professors("John DeNero", school_id)
professor_id = professors[0]["node"]["id"]

ratings = get_all_ratings(professor_id)
score = compute_score(ratings)

print(score.composite_score)     # 0.82
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

## Where to go next

Just getting started? Read the [Getting Started](getting-started.md) guide. It walks through installation, your first request, and the most common mistakes.

Looking for a specific function? Check the [API Reference](api/client.md).

Want to see more complete code? The [Examples](examples.md) page covers comparing professors, filtering by course, tracking trends, and more.

Something not working? See [Troubleshooting](troubleshooting.md).
