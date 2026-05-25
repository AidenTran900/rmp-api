# FAQ

**Does this require an API key or account?**

No. It uses RateMyProfessors' public GraphQL endpoint, which doesn't require authentication.

---

**Is this official?**

No. This is an unofficial wrapper. RMP doesn't publish a public API, so this library queries the same endpoint the website uses internally. It can break if RMP changes their API structure.

---

**What's the difference between `get_professor_summary` and `get_all_ratings` + `compute_score`?**

`get_professor_summary` pulls the aggregated stats directly from RMP's own profile data in a single request. It's fast but limited: you get average rating, average difficulty, would-take-again percent, and rating count.

`get_all_ratings` + `compute_score` fetches every individual rating and computes signals from the raw data. It's slower (one paginated request sequence) but gives you much more: recency-weighted scores, tag frequencies, difficulty histograms, per-course filtering, trend analysis, and comparison tools.

Use `get_professor_summary` for quick lookups. Use the full pipeline when you need detailed analysis.

---

**What's the difference between `node["id"]` and `node["legacyId"]`?**

`node["id"]` is a base64-encoded string like `"VGVhY2hlci0xMjM0NTY="`. This is what the API functions expect for `school_id` and `professor_id`.

`node["legacyId"]` is a plain integer like `123456`. This is only useful for constructing RMP profile URLs: `https://www.ratemyprofessors.com/professor/123456`.

Passing `legacyId` where `id` is expected will silently fail -- you'll get empty results.

---

**Why does `would_take_again_percent` sometimes return -1?**

RMP only started recording would-take-again responses partway through the platform's history. Professors with mostly older ratings may not have enough responses for RMP to display the metric. The library returns `-1` to distinguish "no data" from "0% would take again."

If you need this metric, `compute_score(ratings).would_take_again_pct` computes it from the individual rating objects and returns `0.0` when there are no responses (instead of `-1`).

---

**Are results cached?**

Yes, within a single process. `search_schools`, `search_professors`, `get_courses`, and the pagination layer are all decorated with `lru_cache`. If you call the same function with the same arguments twice, the second call returns the cached result without hitting the network.

The cache does not persist between Python runs. To clear it manually, call `function.cache_clear()` on the relevant function.

---

**What order are ratings returned in?**

Newest first, as returned by the RMP API. `get_all_ratings` preserves this order across pages.

---

**Can I filter by course?**

Yes. Pass `course_filter` to `get_all_ratings` or `get_ratings_page`:

```python
ratings = get_all_ratings(professor_id, course_filter="CS61A")
```

Use `get_courses(professor_id)` to see all course codes available for a professor, sorted by review count.

---

**How does `composite_score` work?**

It's a weighted sum of four normalized signals: recency-weighted rating, would-take-again rate, easiness score, and reliability score. The weights are determined by the preset or custom dict you pass to `compute_score`.

The default preset (`"overall"`) weights them roughly equally. You can pass `WEIGHT_PRESETS["best_teacher"]` to emphasize recency and would-take-again, or `WEIGHT_PRESETS["easiest"]` to prioritize easiness. The result is clamped to `[0, 1]`.

---

**Can I use this in an async application?**

The library is synchronous. All network calls use `requests`, which is blocking. If you need async support, wrap calls with `asyncio.to_thread` or run them in a thread pool.

---

**Why does `compute_score_over_time` return an empty timeline?**

If no ratings have parseable dates, the function returns an empty `ScoreTimeline`. This can happen if ratings have unexpected date formats. Check `ratings[0].date` to see the raw date string.

---

**What Python version is required?**

Python 3.10 or later. The library uses `match`-style type union syntax (`str | None`) which requires 3.10+.
