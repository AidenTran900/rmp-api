"""
main.py

API usage example for the rmp-api package.
"""

from rmp_api import get_all_ratings, get_ratings_page, search_professors, search_schools

if __name__ == "__main__":
    schools = search_schools("University of California Berkeley")
    if schools:
        school_id = schools[0].id

        results = search_professors("Jean Frechet", school_id)
        if results:
            professor_id = results[0].id

            # Fetch one page of ratings
            ratings, has_next, end_cursor = get_ratings_page(professor_id, count=10)
            for r in ratings:
                print(r)

            # Or fetch every rating at once
            all_ratings = get_all_ratings(professor_id)
            print(f"Total ratings fetched: {len(all_ratings)}")
