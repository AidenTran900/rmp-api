# Client

Functions for searching schools and professors, fetching ratings, and filtering reviews.

All functions communicate with the RateMyProfessors GraphQL API over HTTPS. No authentication is required.

---

## ID formats

Two ID formats appear throughout this module:

- **`node["id"]`** -- Base64-encoded string (e.g. `"U2Nob29sLTEyMw=="`). Pass this as `school_id` or `professor_id` to all functions below.
- **`node["legacyId"]`** -- Plain integer (e.g. `1234`). Only useful for building profile URLs like `https://www.ratemyprofessors.com/professor/1234`.

Using `legacyId` where `id` is expected won't raise an error -- you'll just get empty results.

---

## Error handling

Functions that make network requests return `None` or `[]` on failure and print the exception to stdout. They do not raise. If you're getting empty results unexpectedly, check for printed error messages.

---

## Caching

`search_schools`, `search_professors`, `get_courses`, and the internal paginator are decorated with `lru_cache`. Repeated calls with the same arguments return cached results without hitting the network. The cache lasts for the lifetime of the Python process. Call `.cache_clear()` on any of these functions to invalidate manually.

---

## Functions

::: rmp_api.client
    options:
      members:
        - search_schools
        - search_professors
        - get_professor_summary
        - get_ratings_page
        - get_all_ratings
        - get_representative_ratings
        - get_courses
        - filter_ratings_by_keywords
      show_source: false
