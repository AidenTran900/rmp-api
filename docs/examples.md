# Examples

Practical code for common use cases. Each example is self-contained and copy-paste ready.

---

## Look up a professor and print their profile

The simplest thing you can do: search by name and get their stats.

```python
from rmp_api import search_schools, get_professor_summary

schools = search_schools("UCLA")
school_id = schools[0].id

summary = get_professor_summary("Paul Eggert", school_id)

print(summary.formatted_name)           # Paul Eggert
print(summary.department)               # Computer Science
print(summary.avg_rating)               # 4.1
print(summary.avg_difficulty)           # 3.8
print(summary.would_take_again_percent) # 88.0
print(summary.num_ratings)              # 340
print(summary.link)                     # https://www.ratemyprofessors.com/professor/...
```

---

## Compare two professors

Fetch ratings for both and run them through `compare_professors`. By default it ranks on composite score, but you can sort by any signal.

```python
from rmp_api import search_schools, search_professors, get_all_ratings, compare_professors

schools = search_schools("Stanford")
school_id = schools[0].id

def get_professor_id(name):
    results = search_professors(name, school_id)
    return results[0].id

ratings_a = get_all_ratings(get_professor_id("Andrew Ng"))
ratings_b = get_all_ratings(get_professor_id("Daphne Koller"))

comparison = compare_professors({
    "Andrew Ng": ratings_a,
    "Daphne Koller": ratings_b,
})

print(f"Best: {comparison.best}")
for label, score in comparison.ranking:
    print(f"  {label}: {score.composite_score:.2f}")
```

Sort by a different signal, like easiness:

```python
from rmp_api import compare_professors, SortBy

comparison = compare_professors(
    {"Prof A": ratings_a, "Prof B": ratings_b},
    sort_by=SortBy.EASINESS_SCORE,
)
```

See [Models](api/models.md) for all `SortBy` options.

---

## Filter ratings by course

Limit `get_all_ratings` to a specific course code. Useful when a professor teaches multiple courses and you want to isolate one.

```python
from rmp_api import search_schools, search_professors, get_all_ratings, compute_score

schools = search_schools("UC Berkeley")
school_id = schools[0].id

professor_id = search_professors("Dan Garcia", school_id)[0].id

# Only ratings for CS61A
ratings = get_all_ratings(professor_id, course_filter="CS61A")
score = compute_score(ratings)

print(f"CS61A-only: {score.raw_avg_rating:.2f} avg, {len(ratings)} ratings")
```

Pass a list to combine multiple courses:

```python
ratings = get_all_ratings(professor_id, course_filter=["CS61A", "CS61C"])
```

---

## See what courses a professor has taught

```python
from rmp_api import search_schools, search_professors, get_courses

schools = search_schools("MIT")
school_id = schools[0].id

professor_id = search_professors("Erik Demaine", school_id)[0].id
courses = get_courses(professor_id)

for course in courses[:5]:
    print(f"  {course['courseName']} ({course['courseCount']} ratings)")
```

Results are sorted by rating count, most-reviewed first.

---

## Track a professor's score over time

`compute_score_over_time` buckets ratings by year, semester, or quarter and computes a full score for each period.

```python
from rmp_api import search_schools, search_professors, get_all_ratings, compute_score_over_time, TimePeriod

schools = search_schools("UC Berkeley")
school_id = schools[0].id

professor_id = search_professors("John DeNero", school_id)[0].id
ratings = get_all_ratings(professor_id)

timeline = compute_score_over_time(ratings, period=TimePeriod.YEAR)

for period_label, score in timeline.periods:
    print(f"  {period_label}: {score.composite_score:.2f}  ({score.num_ratings} ratings)")

print(f"\nTrend: {timeline.trend:+.4f}")  # positive = improving over time
print(f"Span: {timeline.total_span_years:.1f} years of data")
```

Use `TimePeriod.SEMESTER` or `TimePeriod.QUARTER` for finer granularity.

---

## Compare online vs. in-person ratings

```python
from rmp_api import search_schools, search_professors, get_all_ratings, compute_split_score

schools = search_schools("UC Berkeley")
school_id = schools[0].id

professor_id = search_professors("John DeNero", school_id)[0].id
ratings = get_all_ratings(professor_id)

split = compute_split_score(ratings)

print(f"In-person: {split.in_person.raw_avg_rating:.2f}  ({split.in_person.num_ratings} ratings)")
print(f"Online:    {split.online.raw_avg_rating:.2f}  ({split.online.num_ratings} ratings)")
print(f"Combined:  {split.combined.raw_avg_rating:.2f}  ({split.combined.num_ratings} ratings)")
```

---

## Search comments for a keyword

Filter ratings whose comment text contains a given word or phrase.

```python
from rmp_api import search_schools, search_professors, get_all_ratings, filter_ratings_by_keywords

schools = search_schools("Harvard")
school_id = schools[0].id

professor_id = search_professors("Michael Sandel", school_id)[0].id
ratings = get_all_ratings(professor_id)

# Find ratings that mention "exam" or "midterm"
relevant = filter_ratings_by_keywords(ratings, ["exam", "midterm"])
print(f"Found {len(relevant)} ratings mentioning exams")

# Require both keywords (AND logic)
both = filter_ratings_by_keywords(ratings, ["exam", "midterm"], match_all=True)
```

---

## Use a custom scoring preset

`WEIGHT_PRESETS` has four built-in configurations. Pass any of them (or a custom dict) to `compute_score`.

```python
from rmp_api import compute_score, WEIGHT_PRESETS

# Built-in presets
score = compute_score(ratings, weights=WEIGHT_PRESETS["best_teacher"])
score = compute_score(ratings, weights=WEIGHT_PRESETS["easiest"])
score = compute_score(ratings, weights=WEIGHT_PRESETS["rigorous"])
score = compute_score(ratings, weights=WEIGHT_PRESETS["overall"])

# Custom weights -- values should sum to ~1.0
score = compute_score(ratings, weights={
    "recency_rating":   0.5,
    "would_take_again": 0.3,
    "easiness":         0.1,
    "reliability":      0.1,
})

print(score.composite_score)
```

---

## Get a representative sample of ratings

If you need a handful of ratings spread across a professor's history (useful for LLM summarization or display), use `get_representative_ratings`. It samples evenly by index so you get temporal coverage.

```python
from rmp_api import get_representative_ratings

# Returns up to 12 ratings sampled across the full history
sample = get_representative_ratings(professor_id, n=12)

for rating in sample:
    print(f"[{rating.date[:10]}] {rating.comment[:80]}")
```
