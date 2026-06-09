import operator
from typing import Annotated, TypedDict


class TripState(TypedDict):
    destination: str
    days: int
    budget: int
    travel_style: str

    research_parts: Annotated[list[str], operator.add]
    research: str
    itinerary: str

    approved: bool
    review_score: int
    improvement_count: int
