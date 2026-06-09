from pydantic import BaseModel


class TripPlan(BaseModel):
    destination: str
    summary: str
    itinerary: str