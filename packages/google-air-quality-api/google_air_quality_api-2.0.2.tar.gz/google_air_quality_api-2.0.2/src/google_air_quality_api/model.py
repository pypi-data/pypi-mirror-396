"""Google Air Quality Library API Data Model."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from mashumaro import DataClassDictMixin, field_options
from mashumaro.mixins.json import DataClassJSONMixin

from .mapping import AQICategoryMapping
from .pollutants import POLLUTANT_CODE_MAPPING


def lookup_normalized_generic(original: str) -> str:
    """Lookup normalized category for a given original string using cached reverse mapping."""
    original_lower = original.lower().strip()
    reverse_map = AQICategoryMapping.get_reverse_mapping()
    return reverse_map[original_lower]


@dataclass
class Concentration(DataClassDictMixin):
    """Represents a pollutant concentration."""

    value: float
    units: str


@dataclass
class Pollutant(DataClassDictMixin):
    """Represents a pollutant with metadata."""

    code: str
    display_name: str = field(metadata={"alias": "displayName"})
    full_name: str = field(metadata={"alias": "fullName"})
    concentration: Concentration

    def __post_init__(self) -> None:
        """Adjust concentration units and values after deserialization."""
        units = self.concentration.units

        if units == "PARTS_PER_BILLION":
            self.concentration.units = "ppb"
        elif units == "MICROGRAMS_PER_CUBIC_METER":
            self.concentration.units = "µg/m³"

        if self.code.lower() == "co" and self.concentration.units == "ppb":
            self.concentration.value = self.concentration.value / 1000
            self.concentration.units = "ppm"


class PollutantList(list[Pollutant]):
    """Allows attribute access by pollutant code."""

    def __getattr__(self, name: str) -> Pollutant:
        """Enable dynamic access to pollutants via attribute name (case-insensitive)."""
        name = name.lower()
        for pollutant in self:
            if pollutant.code.lower() == name:
                return pollutant
        message = f"No pollutant named {name!r}"
        raise AttributeError(message)


@dataclass
class Color(DataClassDictMixin):
    """Represents RGB color components."""

    red: float | None = None
    green: float | None = None
    blue: float | None = None


@dataclass
class Index(DataClassDictMixin):
    """Represents an air quality index entry."""

    code: str
    display_name: str = field(metadata={"alias": "displayName"})
    category: str = field(
        metadata=field_options(deserialize=lambda x: lookup_normalized_generic(x))
    )
    dominant_pollutant: str = field(metadata={"alias": "dominantPollutant"})
    aqi: int | None = None
    color: Color | None = field(
        default=None
    )  # Some responses may not include color, this is not allocated to a location and just happens randomly
    aqi_display: str | None = field(default=None, metadata={"alias": "aqiDisplay"})

    @property
    def category_options(self) -> list[str] | None:
        """Return the options for the index category."""
        raw = AQICategoryMapping.get(self.code)
        if raw is None:
            return None
        return [cat.normalized for cat in raw]

    @property
    def pollutant_options(self) -> list[str] | None:
        """Return supported pollutant codes for this index code."""
        return POLLUTANT_CODE_MAPPING.get(self.code)


class IndexList(list[Index]):
    """Allows attribute access by index code."""


@dataclass
class AirQualityCurrentConditionsData(DataClassJSONMixin):
    """Holds air quality data with timestamp and region."""

    date_time: datetime = field(metadata={"alias": "dateTime"})
    _indexes: list[Index] = field(metadata={"alias": "indexes"})
    _pollutants: list[Pollutant] = field(metadata={"alias": "pollutants"})
    region_code: str | None = field(metadata={"alias": "regionCode"}, default=None)

    @property
    def indexes(self) -> IndexList:
        """Returns list of indexes with attribute access."""
        return IndexList(self._indexes)

    @property
    def pollutants(self) -> PollutantList:
        """Returns list of pollutants with attribute access."""
        return PollutantList(self._pollutants)


@dataclass
class AirQualityForecastData(DataClassJSONMixin):
    """Holds air quality data with timestamp and region."""

    hourly_forecasts: list[AirQualityCurrentConditionsData] = field(
        metadata={"alias": "hourlyForecasts"}
    )
    region_code: str = field(metadata={"alias": "regionCode"})


@dataclass
class Error:
    """Error details from the API response."""

    status: str | None = None
    code: int | None = None
    message: str | None = None
    details: list[dict[str, Any]] | None = field(default_factory=list)

    def __str__(self) -> str:
        """Return a string representation of the error details."""
        error_message = ""
        if self.status:
            error_message += self.status
        if self.code:
            if error_message:
                error_message += f" ({self.code})"
            else:
                error_message += str(self.code)
        if self.message:
            if error_message:
                error_message += ": "
            error_message += self.message
        if self.details:
            error_message += f"\nError details: ({self.details})"
        return error_message


@dataclass
class ErrorResponse(DataClassJSONMixin):
    """A response message that contains an error message."""

    error: Error | None = None
