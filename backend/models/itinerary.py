#
#   Imports
#

from pydantic import BaseModel
from typing import Optional

#
#   Itinerary
#

class Itinerary(BaseModel):
    """
        One itinerary.
    """

    positions: list[list[float]]
    start_station_name: str
    end_station_name: str
    nb_acc: int
    popup_text : Optional[str] = None

