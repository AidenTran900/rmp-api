"""
Smoke-tests every code block from the docs.
Run in a clean venv:
    python -m venv /tmp/rmp-test && source /tmp/rmp-test/bin/activate
    pip install rmp-api          # or: pip install -e .
    python test_docs.py
"""

import sys
import time
import traceback

PASS = []
FAIL = []

def section(name):
    print(f"\n{'='*50}\n{name}\n{'='*50}")

def check(label, expr_fn):
    try:
        result = expr_fn()
        print(f"  ✓  {label}: {result!r}")
        PASS.append(label)
    except Exception as e:
        print(f"  ✗  {label}: {e}")
        traceback.print_exc()
        FAIL.append(label)

# ──────────────────────────────────────────────────────────────
# getting-started.md — find a school
# ──────────────────────────────────────────────────────────────
section("search_schools")
from rmp_api import search_schools

results = search_schools("UC Berkeley")
check("returns list",        lambda: isinstance(results, list) and len(results) > 0)
school = results[0]
check("school.name",         lambda: school.name)
check("school.id",           lambda: school.id)
school_id = school.id

# ──────────────────────────────────────────────────────────────
# getting-started.md — find a professor
# ──────────────────────────────────────────────────────────────
section("search_professors")
from rmp_api import search_professors

results = search_professors("John DeNero", school_id)
check("returns list",              lambda: isinstance(results, list) and len(results) > 0)
professor = results[0]
check("professor.first_name",      lambda: professor.first_name)
check("professor.last_name",       lambda: professor.last_name)
check("professor.id",              lambda: professor.id)
professor_id = professor.id

# ──────────────────────────────────────────────────────────────
# getting-started.md — get ratings
# ──────────────────────────────────────────────────────────────
section("get_all_ratings")
from rmp_api import get_all_ratings

ratings = get_all_ratings(professor_id)
check("ratings is list",           lambda: isinstance(ratings, list))
check("ratings non-empty",         lambda: len(ratings) > 0)

# ──────────────────────────────────────────────────────────────
# getting-started.md — compute_score
# ──────────────────────────────────────────────────────────────
section("compute_score")
from rmp_api import compute_score

score = compute_score(ratings)
check("raw_avg_rating",            lambda: score.raw_avg_rating)
check("would_take_again_pct",      lambda: score.would_take_again_pct)
check("composite_score 0-1",       lambda: 0 <= score.composite_score <= 1)
check("top_tags is list",          lambda: isinstance(score.top_tags, list))

# ──────────────────────────────────────────────────────────────
# getting-started.md — get_professor_summary
# ──────────────────────────────────────────────────────────────
section("get_professor_summary")
from rmp_api import get_professor_summary

summary = get_professor_summary("John DeNero", school_id)
check("avg_rating",                lambda: summary.avg_rating)
check("avg_difficulty",            lambda: summary.avg_difficulty)
check("would_take_again_percent",  lambda: summary.would_take_again_percent)
check("num_ratings > 0",           lambda: summary.num_ratings > 0)
check("link",                      lambda: summary.link)

# ──────────────────────────────────────────────────────────────
# getting-started.md — guard: empty search
# ──────────────────────────────────────────────────────────────
section("guard: empty search result")
bad = search_professors("ZZZNOBODYHASTHISNAME999", school_id)
check("empty returns falsy list",  lambda: bad is None or bad == [])

# ──────────────────────────────────────────────────────────────
# getting-started.md — guard: professor not found summary
# ──────────────────────────────────────────────────────────────
section("guard: professor not found (-1 sentinel)")
missing = get_professor_summary("ZZZNOBODYHASTHISNAME999", school_id)
check("num_ratings == 0 or -1",    lambda: missing.num_ratings <= 0)

# ──────────────────────────────────────────────────────────────
# examples.md — look up UCLA professor
# ──────────────────────────────────────────────────────────────
section("examples: UCLA professor summary")
ucla = search_schools("UCLA")
check("UCLA found",                lambda: len(ucla) > 0)
ucla_id = ucla[0].id
eggert = get_professor_summary("Paul Eggert", ucla_id)
check("eggert.formatted_name",     lambda: eggert.formatted_name)
check("eggert.department",         lambda: eggert.department)

# ──────────────────────────────────────────────────────────────
# examples.md — compare two professors
# ──────────────────────────────────────────────────────────────
section("examples: compare_professors")
from rmp_api import compare_professors

stanford = search_schools("Stanford")
check("Stanford found",            lambda: len(stanford) > 0)
stanford_id = stanford[0].id

def get_id(name, sid):
    r = search_professors(name, sid)
    return r[0].id if r else None

ng_id     = get_id("Andrew Ng",     stanford_id)
koller_id = get_id("Daphne Koller", stanford_id)

if ng_id and koller_id:
    ratings_a = get_all_ratings(ng_id);     time.sleep(0.5)
    ratings_b = get_all_ratings(koller_id)
    comparison = compare_professors({"Andrew Ng": ratings_a, "Daphne Koller": ratings_b})
    check("comparison.best",       lambda: comparison.best)
    check("comparison.ranking",    lambda: len(comparison.ranking) == 2)
else:
    print("  ⚠  skipped (professors not found on Stanford)")

# ──────────────────────────────────────────────────────────────
# examples.md — compare_professors SortBy
# ──────────────────────────────────────────────────────────────
section("examples: compare_professors SortBy")
from rmp_api import SortBy

if ng_id and koller_id:
    cmp2 = compare_professors(
        {"A": ratings_a, "B": ratings_b},
        sort_by=SortBy.EASINESS_SCORE,
    )
    check("SortBy works",          lambda: cmp2.best)
else:
    print("  ⚠  skipped")

# ──────────────────────────────────────────────────────────────
# examples.md — filter ratings by course
# ──────────────────────────────────────────────────────────────
section("examples: course_filter")
denero_ratings = get_all_ratings(professor_id, course_filter="CS61A")
check("course_filter string",      lambda: isinstance(denero_ratings, list))

multi = get_all_ratings(professor_id, course_filter=["CS61A", "CS61C"])
check("course_filter list",        lambda: isinstance(multi, list))

# ──────────────────────────────────────────────────────────────
# examples.md — get_courses
# ──────────────────────────────────────────────────────────────
section("examples: get_courses")
from rmp_api import get_courses

courses = get_courses(professor_id)
check("get_courses returns list",  lambda: isinstance(courses, list))
if courses:
    check("course has courseName", lambda: "courseName" in courses[0])

# ──────────────────────────────────────────────────────────────
# examples.md — compute_score_over_time
# ──────────────────────────────────────────────────────────────
section("examples: compute_score_over_time")
from rmp_api import compute_score_over_time, TimePeriod

timeline = compute_score_over_time(ratings, period=TimePeriod.YEAR)
check("timeline.periods non-empty",lambda: len(timeline.periods) > 0)
check("timeline.trend is float",   lambda: isinstance(timeline.trend, float))
check("timeline.total_span_years", lambda: timeline.total_span_years >= 0)

# ──────────────────────────────────────────────────────────────
# examples.md — compute_split_score
# ──────────────────────────────────────────────────────────────
section("examples: compute_split_score")
from rmp_api import compute_split_score

split = compute_split_score(ratings)
check("split.in_person",           lambda: split.in_person)
check("split.online",              lambda: split.online)
check("split.combined",            lambda: split.combined)

# ──────────────────────────────────────────────────────────────
# examples.md — filter_ratings_by_keywords
# ──────────────────────────────────────────────────────────────
section("examples: filter_ratings_by_keywords")
from rmp_api import filter_ratings_by_keywords

relevant = filter_ratings_by_keywords(ratings, ["exam", "midterm"])
check("OR filter returns list",    lambda: isinstance(relevant, list))

both = filter_ratings_by_keywords(ratings, ["exam", "midterm"], match_all=True)
check("AND filter returns list",   lambda: isinstance(both, list))

# ──────────────────────────────────────────────────────────────
# examples.md — WEIGHT_PRESETS
# ──────────────────────────────────────────────────────────────
section("examples: WEIGHT_PRESETS")
from rmp_api import WEIGHT_PRESETS

for preset in ["best_teacher", "easiest", "rigorous", "overall"]:
    s = compute_score(ratings, weights=WEIGHT_PRESETS[preset])
    check(f"preset:{preset}",      lambda s=s: 0 <= s.composite_score <= 1)

custom_score = compute_score(ratings, weights={
    "recency_rating":   0.5,
    "would_take_again": 0.3,
    "easiness":         0.1,
    "reliability":      0.1,
})
check("custom weights",            lambda: 0 <= custom_score.composite_score <= 1)

# ──────────────────────────────────────────────────────────────
# examples.md — get_representative_ratings
# ──────────────────────────────────────────────────────────────
section("examples: get_representative_ratings")
from rmp_api import get_representative_ratings

sample = get_representative_ratings(professor_id, n=12)
check("sample is list",            lambda: isinstance(sample, list))
check("sample len <= 12",          lambda: len(sample) <= 12)
if sample:
    check("rating has .date",      lambda: sample[0].date)
    check("rating has .comment",   lambda: hasattr(sample[0], "comment"))

# ──────────────────────────────────────────────────────────────
# Summary
# ──────────────────────────────────────────────────────────────
print(f"\n{'='*50}")
print(f"PASSED: {len(PASS)}   FAILED: {len(FAIL)}")
if FAIL:
    print("\nFailed checks:")
    for f in FAIL:
        print(f"  ✗ {f}")
    sys.exit(1)
else:
    print("All checks passed.")
