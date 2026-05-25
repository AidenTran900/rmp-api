# Getting Started

## Installation

```bash
pip install git+https://github.com/youruser/rate-my-prof-api.git
```

Or clone and install locally for development:

```bash
git clone https://github.com/youruser/rate-my-prof-api.git
cd rate-my-prof-api
pip install -e .
```

**Requirements:** Python 3.10+. The only runtime dependency is `requests`.

---

## Your first request

The typical flow is: find a school, find a professor at that school, fetch their ratings, do something with them. Here's each step.

### 1. Find the school

```python
from rmp_api import search_schools

results = search_schools("UC Berkeley")
school = results[0]["node"]

print(school["name"])  # "University of California, Berkeley"
school_id = school["id"]  # "U2Nob29sLTEyMw=="
```

`search_schools` returns a list of matching schools ranked by relevance. Use `results[0]` for the top match. The `id` field is what you need for the next step.

### 2. Find the professor

```python
from rmp_api import search_professors

results = search_professors("John DeNero", school_id)
professor = results[0]["node"]

print(professor["firstName"], professor["lastName"])  # John DeNero
professor_id = professor["id"]  # "VGVhY2hlci0xMjM0NTY="
```

Both IDs are base64-encoded strings. They look a bit odd but that's what the API returns. Pass them as-is.

### 3. Fetch their ratings

```python
from rmp_api import get_all_ratings

ratings = get_all_ratings(professor_id)
print(len(ratings))  # varies by professor
```

`get_all_ratings` handles pagination automatically. You always get the full set of ratings in one call.

### 4. Compute a quality score

```python
from rmp_api import compute_score

score = compute_score(ratings)

print(score.raw_avg_rating)        # 4.1  (mean of helpful + clarity)
print(score.would_take_again_pct)  # 0.87 (fraction, not percent)
print(score.composite_score)       # 0.82 (weighted quality signal, 0-1)
print(score.top_tags[:3])          # [('Respected', 14), ('Clear grading', 11), ...]
```

That's the full flow. Four calls.

---

## Quick stats without fetching all ratings

If you only need the aggregated numbers from RMP's own profile page (average rating, difficulty, would-take-again), use `get_professor_summary`. It's a single request and skips pagination entirely.

```python
from rmp_api import search_schools, get_professor_summary

schools = search_schools("UC Berkeley")
school_id = schools[0]["node"]["id"]

summary = get_professor_summary("John DeNero", school_id)

print(summary.avg_rating)                # 4.2
print(summary.avg_difficulty)            # 2.8
print(summary.would_take_again_percent)  # 92.0  (this one IS a percent)
print(summary.num_ratings)               # 215
print(summary.link)                      # https://www.ratemyprofessors.com/professor/...
```

Use `get_professor_summary` when you just need a quick overview. Use `get_all_ratings` + `compute_score` when you need detailed signals, filtering, comparisons, or trend analysis.

---

## Common mistakes

**Using the wrong ID type.** Every search result has two IDs: `node["id"]` (base64 string) and `node["legacyId"]` (integer). The functions `get_all_ratings`, `get_ratings_page`, and `get_courses` require the base64 string ID. `legacyId` is only useful for constructing profile URLs manually.

```python
# Correct
professor_id = results[0]["node"]["id"]           # "VGVhY2hlci0xMjM0NTY="

# Wrong -- will return no results or raise an error
professor_id = results[0]["node"]["legacyId"]     # 123456
```

**Not checking if the search returned anything.** Both `search_schools` and `search_professors` return `None` on network failure and an empty list when nothing matches. Check before indexing.

```python
results = search_professors("Some Prof", school_id)
if not results:
    print("No match found")
else:
    professor_id = results[0]["node"]["id"]
```

**Trusting `-1` as a valid rating.** `get_professor_summary` returns `-1` for numeric fields when no professor is found. Always check `summary.num_ratings > 0` before using those values.

```python
summary = get_professor_summary("Nonexistent Prof", school_id)
if summary.num_ratings == 0:
    print("Professor not found")
```

**Expecting `would_take_again_percent` and `would_take_again_pct` to match.** They're from different sources. `get_professor_summary` returns RMP's own aggregated `would_take_again_percent` (0-100). `compute_score` returns `would_take_again_pct` computed from individual ratings (0-1). They should be close but won't be identical.

**Hammering the API in a loop.** The library caches results per process, but the first call for each professor still hits the network. If you're fetching ratings for many professors, add a small sleep between calls to avoid getting rate-limited.

```python
import time

for professor_id in professor_ids:
    ratings = get_all_ratings(professor_id)
    time.sleep(0.5)
```

---

## Next steps

- [Examples](examples.md) - Compare professors, filter by course, track score over time
- [API Reference](api/client.md) - All functions with full parameter documentation
- [Troubleshooting](troubleshooting.md) - What to do when something goes wrong
