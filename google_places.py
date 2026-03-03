import os
import time
import googlemaps
from dotenv import load_dotenv

load_dotenv()

_api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
if not _api_key:
    raise EnvironmentError(
        "GOOGLE_MAPS_API_KEY not set. Copy .env.example to .env and add your key."
    )

gmaps = googlemaps.Client(key=_api_key)


def search_businesses(category: str, city: str, min_stars: float, max_results: int = 50) -> list[dict]:
    """Search Google Places for businesses matching category + city, filtered by min_stars."""
    query = f"{category} in {city}"
    results = []

    response = gmaps.places(query=query)
    results.extend(response.get("results", []))

    # Paginate up to 3 pages (60 results max)
    pages = 1
    while pages < 3:
        next_page_token = response.get("next_page_token")
        if not next_page_token:
            break
        time.sleep(2)  # Required delay before next_page_token is valid
        response = gmaps.places(query=query, page_token=next_page_token)
        results.extend(response.get("results", []))
        pages += 1

    # Filter by minimum star rating and require at least one review
    filtered = [
        r for r in results
        if r.get("rating", 0) >= min_stars and r.get("user_ratings_total", 0) > 0
    ]

    return filtered[:max_results]


def get_place_details(place_id: str) -> dict:
    """Fetch full details for a place including phone, address, website, hours, and reviews."""
    fields = [
        "name",
        "rating",
        "user_ratings_total",
        "formatted_phone_number",
        "formatted_address",
        "website",
        "url",
        "opening_hours",
        "reviews",
        "type",
    ]

    response = gmaps.place(place_id=place_id, fields=fields)
    time.sleep(0.1)  # Rate limiting

    return response.get("result", {})
