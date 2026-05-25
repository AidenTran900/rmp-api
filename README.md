# Rate My Professor API

Python wrapper for the RateMyProfessors GraphQL API. Scrapes professor ratings, individual reviews, and school info.

> Based on [snow4060/rmp-api](https://github.com/snow4060/rmp-api).

---

## Installation

```bash
pip install requests
```

Or install directly from GitHub for use in other projects:

```bash
pip install git+https://github.com/youruser/rate-my-prof-api.git
```

---

## Quick Start

```python
from main import search_schools, search_professors, get_professor_summary, get_all_ratings

# 1. Find school ID
schools = search_schools("UC Berkeley")
school_id = schools[0]["node"]["id"]

# 2. Get professor summary (avg rating, difficulty, etc.)
summary = get_professor_summary("John DeNero", school_id)
print(summary.avg_rating)       # e.g. 4.5
print(summary.avg_difficulty)   # e.g. 3.2
print(summary.link)             # https://www.ratemyprofessors.com/professor/...

# 3. Fetch individual ratings
professor_id = search_professors("John DeNero", school_id)[0]["node"]["id"]
ratings = get_all_ratings(professor_id)
for r in ratings:
    print(r.comment, r.course, r.clarity_rating)
```

---

## API Reference

### `search_schools(school_name: str) -> list[dict] | None`

Search schools by name. Returns raw edge list from RMP GraphQL.

```python
schools = search_schools("MIT")
school_id = schools[0]["node"]["id"]       # base64 node ID
school_name = schools[0]["node"]["name"]
```

---

### `search_professors(professor_name: str, school_id: str) -> list[dict] | None`

Search professors at a school. Returns raw edge list.

```python
results = search_professors("John DeNero", school_id)
professor_id = results[0]["node"]["id"]    # base64 node ID — use for ratings
legacy_id = results[0]["node"]["legacyId"] # integer ID — used in profile URLs
```

---

### `get_professor_summary(professor_name: str, school_id: str) -> ProfessorRating`

Convenience wrapper: searches professors, returns structured summary for the top result. Returns a `ProfessorRating` with all fields set to `-1` / empty if not found.

```python
summary = get_professor_summary("John DeNero", school_id)
```

**`ProfessorRating` fields:**

| Field | Type | Description |
|---|---|---|
| `avg_rating` | `float` | Overall rating (1–5) |
| `avg_difficulty` | `float` | Difficulty (1–5) |
| `would_take_again_percent` | `float` | % who'd take again |
| `num_ratings` | `int` | Total number of ratings |
| `formatted_name` | `str` | `"First Last"` |
| `department` | `str` | e.g. `"Computer Science"` |
| `link` | `str` | RMP profile URL |

---

### `get_ratings_page(professor_id, count=20, course_filter=None, cursor=None) -> tuple[list[Rating], bool, str | None]`

Fetch one page of individual ratings. Ratings are returned **newest first**.

```python
ratings, has_next, end_cursor = get_ratings_page(professor_id, count=20)

# Next page:
ratings2, has_next, end_cursor = get_ratings_page(professor_id, cursor=end_cursor)

# Filter by course:
ratings, _, _ = get_ratings_page(professor_id, course_filter="CS61A")
```

Returns `(ratings, has_next_page, end_cursor)`.

---

### `get_all_ratings(professor_id, course_filter=None, page_size=20) -> list[Rating]`

Paginates automatically and returns every rating. Can be slow for professors with 500+ ratings.

```python
all_ratings = get_all_ratings(professor_id)
```

---

### `Rating` dataclass

| Field | Type | Notes |
|---|---|---|
| `id` | `str` | Base64 node ID |
| `legacy_id` | `int` | Integer ID |
| `comment` | `str` | Student review text |
| `date` | `str` | ISO-ish timestamp string |
| `course` | `str` | e.g. `"CS61A"` |
| `helpful_rating` | `float` | 1–5 |
| `clarity_rating` | `float` | 1–5 |
| `difficulty_rating` | `float` | 1–5 |
| `rating_tags` | `list[str]` | e.g. `["Tough grader", "Lots of homework"]` |
| `flag_status` | `str` | `"UNFLAGGED"` or `"FLAGGED"` |
| `attendance_mandatory` | `str \| None` | `"mandatory"` / `"non mandatory"` / `None` |
| `would_take_again` | `int \| None` | `1` = yes, `0` = no, `None` = N/A |
| `grade` | `str \| None` | e.g. `"A"`, `"B+"` |
| `textbook_use` | `int \| None` | 1–5 scale |
| `is_for_online_class` | `bool` | |
| `is_for_credit` | `bool` | |
| `thumbs_up_total` | `int` | Helpful votes |
| `thumbs_down_total` | `int` | Not helpful votes |
| `teacher_note` | `str \| None` | Professor's reply, if any |

---

## Representative Sample (for AI/agent use)

Fetching all ratings for LLM context is wasteful. Stride-sample for temporal spread:

```python
def get_representative_ratings(professor_id: str, n: int = 12) -> list[Rating]:
    """Return n ratings evenly spread across time (newest → oldest)."""
    all_ratings = get_all_ratings(professor_id)
    if len(all_ratings) <= n:
        return all_ratings
    step = len(all_ratings) // n
    return all_ratings[::step][:n]
```

~12 ratings covers sentiment, difficulty, and teaching style without bloating context.

---

## Notes

- RMP returns results sorted **newest first**.
- `professor_id` (base64) is required for `get_ratings_page` / `get_all_ratings`. Get it from `search_professors`.
- No auth required — uses the same public GraphQL endpoint as the RMP website.
- RMP may rate-limit heavy pagination. Add `time.sleep(0.5)` between pages if needed.
