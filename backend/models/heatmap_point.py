#
#   Imports
#

from pydantic import BaseModel

#
#   HeatmapPoint
#

class HeatmapPoint(BaseModel):
    """
        One point for the heatmap (lat, lng, count).
    """

    lat: float
    lng: float
    count: int = 1
