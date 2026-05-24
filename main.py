import requests
from dataclasses import dataclass

API_LINK = "https://www.ratemyprofessors.com/graphql"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Content-Type": "application/json",
    "Authorization": "Basic dGVzdDp0ZXN0",
    "Sec-GPC": "1",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Priority": "u=4",
}

TEACHER_QUERY = """
query TeacherSearchResultsPageQuery(
  $query: TeacherSearchQuery!
  $schoolID: ID
  $includeSchoolFilter: Boolean!
) {
  search: newSearch {
    teachers(query: $query, first: 8, after: "") {
      edges {
        cursor
        node {
          id
          legacyId
          avgRating
          numRatings
          wouldTakeAgainPercent
          avgDifficulty
          department
          firstName
          lastName
          isSaved
          school {
            name
            id
          }
          __typename
        }
      }
    }
  }
  school: node(id: $schoolID) @include(if: $includeSchoolFilter) {
    __typename
    ... on School {
      name
    }
    id
  }
}
"""

SCHOOL_QUERY = """
query NewSearchSchoolsQuery($query: SchoolSearchQuery!) {
  newSearch {
    schools(query: $query) {
      edges {
        cursor
        node {
          id
          legacyId
          name
          city
          state
          departments {
            id
            name
          }
          numRatings
          avgRatingRounded
          summary {
            campusCondition
            campusLocation
            careerOpportunities
            clubAndEventActivities
            foodQuality
            internetSpeed
            libraryCondition
            schoolReputation
            schoolSafety
            schoolSatisfaction
            socialActivities
          }
        }
      }
    }
  }
}
"""


@dataclass
class ProfessorRating:
    avg_rating: float
    avg_difficulty: float
    would_take_again_percent: float
    num_ratings: int
    formatted_name: str
    department: str
    link: str


def search_school(school_name: str) -> list[dict] | None:
    try:
        response = requests.post(
            API_LINK,
            headers=HEADERS,
            json={
                "query": SCHOOL_QUERY,
                "variables": {"query": {"text": school_name}},
            },
        )
        response.raise_for_status()
        return response.json()["data"]["newSearch"]["schools"]["edges"]
    except Exception as e:
        print(f"Error searching school: {e}")
        return None


def search_professors_at_school_id(professor_name: str, school_id: str) -> list[dict] | None:
    try:
        response = requests.post(
            API_LINK,
            headers=HEADERS,
            json={
                "query": TEACHER_QUERY,
                "variables": {
                    "query": {
                        "text": professor_name,
                        "schoolID": school_id,
                        "fallback": True,
                        "departmentID": None,
                    },
                    "schoolID": school_id,
                    "includeSchoolFilter": True,
                },
            },
        )
        response.raise_for_status()
        return response.json()["data"]["search"]["teachers"]["edges"]
    except Exception as e:
        print(f"Error searching professors: {e}")
        return None


def get_professor_rating_at_school_id(professor_name: str, school_id: str) -> ProfessorRating:
    results = search_professors_at_school_id(professor_name, school_id)

    if not results:
        return ProfessorRating(
            avg_rating=-1,
            avg_difficulty=-1,
            would_take_again_percent=-1,
            num_ratings=0,
            formatted_name=professor_name,
            department="",
            link="",
        )

    node = results[0]["node"]
    return ProfessorRating(
        avg_rating=node["avgRating"],
        avg_difficulty=node["avgDifficulty"],
        would_take_again_percent=node["wouldTakeAgainPercent"],
        num_ratings=node["numRatings"],
        formatted_name=f"{node['firstName']} {node['lastName']}",
        department=node["department"],
        link=f"https://www.ratemyprofessors.com/professor/{node['legacyId']}",
    )


if __name__ == "__main__":
    schools = search_school("University of California Berkeley")
    if schools:
        school_id = schools[0]["node"]["id"]

        # All search results
        results = search_professors_at_school_id("Jean Frechet", school_id)
        for r in results:
            print(r)

        # Single professor rating
        rating = get_professor_rating_at_school_id("Jean Frechet", school_id)
        print(rating)
    else:
        print("Unknown school name")