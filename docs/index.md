# Rate My Professor API

A Python library for querying the RateMyProfessors GraphQL API. Search for professors, pull their ratings, and compute quality signals from the data.


---

## Install

```bash
pip install rmp-api
```

Requires Python 3.10+.

---

## Example

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

# Find a school
schools = search_schools("UC Berkeley")
school_id = schools[0].id

# Find a professor
professors = search_professors("John DeNero", school_id)
professor_id = professors[0].id

# Quick aggregate summary (single request, no pagination)
summary = get_professor_summary("John DeNero", school_id)
print(summary.avg_rating)               # 4.2
print(summary.avg_difficulty)           # 2.8
print(summary.would_take_again_percent) # 92.0
print(summary.link)                     # https://www.ratemyprofessors.com/professor/...

# Courses taught
courses = get_courses(professor_id)
print(courses[:3])  # [{'courseName': 'CS61A', 'courseCount': 42}, ...]

# All ratings (auto-paginated); optionally filter to a course
ratings = get_all_ratings(professor_id, course_filter="CS61A")

# Filter by keyword
hard_ratings = filter_ratings_by_keywords(ratings, "hard")

# Compute quality signals
score = compute_score(ratings)
print(score.composite_score)  # 0.82
print(score.top_tags[:3])     # [('Respected', 14), ('Clear grading', 11), ...]
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
