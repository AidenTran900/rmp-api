# Client

Functions for searching schools and professors, fetching ratings, and filtering reviews.

All functions communicate with the RateMyProfessors GraphQL API over HTTPS. No authentication is required.

---

## Search result types

`search_schools` returns `list[SchoolResult]` and `search_professors` returns `list[ProfessorResult]`. Both are typed dataclasses -- use attribute access, not dict indexing.

```python
school = search_schools("UC Berkeley")[0]
school.id           # base64 node ID -- pass this to other functions
school.legacy_id    # integer -- only useful for building profile URLs
school.name         # "University of California, Berkeley"

professor = search_professors("John DeNero", school.id)[0]
professor.id        # base64 node ID -- pass this to get_all_ratings, etc.
professor.legacy_id # integer -- only useful for building profile URLs
```

See [Models](models.md) for the full field list on each type.

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
