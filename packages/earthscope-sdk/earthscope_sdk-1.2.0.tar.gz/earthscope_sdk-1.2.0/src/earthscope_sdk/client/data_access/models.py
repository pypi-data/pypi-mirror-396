from typing import Annotated, Literal, Optional

from pydantic import BaseModel, Field, model_validator

SatelliteSystem = Literal["G", "R", "E", "J", "C", "I", "S"]
"""
GNSS satellite system abbreviation.

- G: GPS
- R: GLONASS
- E: Galileo
- J: QZSS
- C: BeiDou
- I: IRNSS / NavIC
- S: SBAS
"""


class FloatFilter(BaseModel):
    """
    A range filter on a float field.
    """

    min: Optional[float] = None
    max: Optional[float] = None
    inclusive_min: bool = True
    inclusive_max: bool = True

    @model_validator(mode="after")
    def _require_one(self):
        if self.min is None and self.max is None:
            raise ValueError("Either min or max must be provided")

        return self

    def __str__(self):
        lower = "[" if self.inclusive_min else "("
        upper = "]" if self.inclusive_max else ")"
        min = self.min if self.min is not None else ""
        max = self.max if self.max is not None else ""
        return f"{lower}{min},{max}{upper}"

    def __repr__(self):
        return f"FloatFilter(min={self.min}, max={self.max}, inclusive_min={self.inclusive_min}, inclusive_max={self.inclusive_max})"


class GeodeticCoordinate(BaseModel):
    """
    A geodetic coordinate: latitude, longitude, height in degrees and meters.
    """

    latitude: Annotated[float, Field(ge=-90, le=90)]
    longitude: Annotated[float, Field(ge=-180, le=180)]
    height: float
