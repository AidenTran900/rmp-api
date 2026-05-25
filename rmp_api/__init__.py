"""
rmp_api

Python wrapper for the RateMyProfessors GraphQL API.
"""

from .client import (
    filter_ratings_by_keywords,
    get_all_ratings,
    get_courses,
    get_professor_summary,
    get_ratings_page,
    get_representative_ratings,
    search_professors,
    search_schools,
)
from .models import ProfessorComparison, ProfessorRating, ProfessorScore, Rating, ScoreTimeline, SplitScore
from .scoring import (
    SORTABLE_FIELDS,
    WEIGHT_PRESETS,
    compare_professors,
    compute_score,
    compute_score_over_time,
    compute_split_score,
)

__all__ = [
    # Client
    "search_schools",
    "search_professors",
    "get_professor_summary",
    "get_ratings_page",
    "get_all_ratings",
    "get_representative_ratings",
    "get_courses",
    "filter_ratings_by_keywords",
    # Models
    "Rating",
    "ProfessorRating",
    # Scoring
    "compute_score",
    "compute_split_score",
    "compute_score_over_time",
    "compare_professors",
    "ProfessorScore",
    "SplitScore",
    "ScoreTimeline",
    "ProfessorComparison",
    "WEIGHT_PRESETS",
    "SORTABLE_FIELDS",
]
