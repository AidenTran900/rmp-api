"""
rmp_api

Python wrapper for the RateMyProfessors GraphQL API.
"""

from .client import (
    get_all_ratings,
    get_professor_summary,
    get_ratings_page,
    get_representative_ratings,
    search_professors,
    search_schools,
)
from .models import ProfessorRating, ProfessorScore, Rating
from .scoring import WEIGHT_PRESETS, compute_score

__all__ = [
    # Client
    "search_schools",
    "search_professors",
    "get_professor_summary",
    "get_ratings_page",
    "get_all_ratings",
    "get_representative_ratings",
    # Models
    "Rating",
    "ProfessorRating",
    # Scoring
    "compute_score",
    "ProfessorScore",
    "WEIGHT_PRESETS",
]
