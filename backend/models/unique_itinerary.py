#
#   Imports
#

from pydantic import BaseModel

#
#   HeatmapPoint
#

class UniqueItinerary(BaseModel):
    """
        One itinerary (start lat, start lng, end lat, end lng).
    """

    start_lat: float
    start_lng: float
    end_lat: float
    end_lng: float

    def positions(self) -> list[list[float]]:
        return [
            [self.start_lat, self.start_lng],
            [self.end_lat, self.end_lng],
        ]

