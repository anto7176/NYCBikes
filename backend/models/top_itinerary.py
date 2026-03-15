#
#   Imports
#

from pydantic import BaseModel

#
#   TopItinerary
#

class TopItinerary(BaseModel):
    """
        Top itinerary (start lat, start lng, end lat, end lng).
    """

    start_lat: float
    start_lng: float
    end_lat: float
    end_lng: float
    count: int

    def positions(self) -> list[list[float]]:
        return [
            [self.start_lat, self.start_lng],
            [self.end_lat, self.end_lng],
        ]

