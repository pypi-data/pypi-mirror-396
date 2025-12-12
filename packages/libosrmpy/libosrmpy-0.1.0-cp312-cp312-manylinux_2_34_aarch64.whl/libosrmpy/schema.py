"""
OSRM response schema definitions

Dataclass-based value objects to ensure type safety and avoid dict usage
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np
from numpy.typing import NDArray


# =============================================================================
# Enums for Trip API
# =============================================================================


class TripSource(Enum):
    """Source constraint for Trip API"""

    ANY = "any"
    FIRST = "first"


class TripDestination(Enum):
    """Destination constraint for Trip API"""

    ANY = "any"
    LAST = "last"


@dataclass(frozen=True, slots=True)
class Coordinate:
    """
    Input coordinate object

    Use instead of tuple[float, float] to avoid lon/lat order confusion.
    OSRM uses (longitude, latitude) order - same as GeoJSON.
    """

    longitude: float
    latitude: float

    @classmethod
    def from_tuple(cls, coord: tuple[float, float]) -> Coordinate:
        """
        Create Coordinate from (longitude, latitude) tuple

        Args:
            coord: (longitude, latitude) tuple

        Returns:
            Coordinate object
        """
        return cls(longitude=coord[0], latitude=coord[1])

    def to_tuple(self) -> tuple[float, float]:
        """
        Convert to (longitude, latitude) tuple

        Returns:
            (longitude, latitude) tuple
        """
        return (self.longitude, self.latitude)


@dataclass(frozen=True, slots=True)
class Waypoint:
    """
    Waypoint information returned by OSRM

    Corresponds to each item in sources/destinations
    """

    location: Coordinate
    name: str = ""
    hint: str = ""
    distance: float = 0.0  # snapped distance from original coordinate

    @classmethod
    def from_raw(cls, raw: dict) -> Waypoint:
        """Create Waypoint object from raw dict"""
        loc = raw["location"]  # required
        return cls(
            location=Coordinate(longitude=loc[0], latitude=loc[1]),
            name=raw.get("name", ""),  # optional
            hint=raw.get("hint", ""),  # optional
            distance=raw["distance"],  # required
        )

    @property
    def longitude(self) -> float:
        """Backward compatibility: access longitude directly"""
        return self.location.longitude

    @property
    def latitude(self) -> float:
        """Backward compatibility: access latitude directly"""
        return self.location.latitude


@dataclass
class TableResult:
    """
    OSRM Table API response result

    Attributes:
        durations: Duration matrix in seconds. shape=(len(sources), len(destinations))
                   np.nan if unreachable
        distances: Distance matrix in meters. shape=(len(sources), len(destinations))
                   np.nan if unreachable
        sources: List of source waypoints (snapped)
        destinations: List of destination waypoints (snapped)
    """

    durations: NDArray[np.float64]
    distances: NDArray[np.float64]
    sources: list[Waypoint]
    destinations: list[Waypoint]

    @classmethod
    def from_raw(cls, raw: dict) -> TableResult:
        """
        Convert C++ _table_raw() result to TableResult

        Args:
            raw: dict returned by _table_raw()

        Returns:
            TableResult object
        """
        # Convert durations (None -> np.nan)
        durations_raw = raw["durations"]  # required
        durations = np.array(
            [[v if v is not None else np.nan for v in row] for row in durations_raw],
            dtype=np.float64,
        )

        # Convert distances (None -> np.nan)
        distances_raw = raw["distances"]  # required
        distances = np.array(
            [[v if v is not None else np.nan for v in row] for row in distances_raw],
            dtype=np.float64,
        )

        # Convert sources/destinations
        sources = [Waypoint.from_raw(w) for w in raw["sources"]]  # required
        destinations = [Waypoint.from_raw(w) for w in raw["destinations"]]  # required

        return cls(
            durations=durations,
            distances=distances,
            sources=sources,
            destinations=destinations,
        )

    def duration_between(self, src_idx: int, dst_idx: int) -> float:
        """
        Get duration between specific source and destination (in seconds)

        Args:
            src_idx: sources index
            dst_idx: destinations index

        Returns:
            Duration in seconds. np.nan if unreachable
        """
        return float(self.durations[src_idx, dst_idx])

    def distance_between(self, src_idx: int, dst_idx: int) -> float:
        """
        Get distance between specific source and destination (in meters)

        Args:
            src_idx: sources index
            dst_idx: destinations index

        Returns:
            Distance in meters. np.nan if unreachable
        """
        return float(self.distances[src_idx, dst_idx])


@dataclass
class RouteResult:
    """
    OSRM Route API response result (minimal version)

    Attributes:
        distance: Total route distance in meters
        duration: Total route duration in seconds
        waypoints: List of waypoints (snapped to road network)
    """

    distance: float
    duration: float
    waypoints: list[Waypoint]

    @classmethod
    def from_raw(cls, raw: dict) -> RouteResult:
        """
        Convert C++ _route_raw() result to RouteResult

        Args:
            raw: dict returned by _route_raw()

        Returns:
            RouteResult object
        """
        # Get the first route (best route)
        routes = raw["routes"]  # required
        if not routes:
            raise ValueError("No routes found in response")

        route = routes[0]

        # Extract distance and duration
        distance = route["distance"]  # required
        duration = route["duration"]  # required

        # Convert waypoints
        waypoints = [Waypoint.from_raw(w) for w in raw["waypoints"]]  # required

        return cls(
            distance=distance,
            duration=duration,
            waypoints=waypoints,
        )


# =============================================================================
# Nearest API Result
# =============================================================================


@dataclass
class NearestResult:
    """
    OSRM Nearest API response result

    Attributes:
        waypoints: List of nearest waypoints (snapped to road network)
    """

    waypoints: list[Waypoint]

    @classmethod
    def from_raw(cls, raw: dict) -> NearestResult:
        """
        Convert C++ _nearest_raw() result to NearestResult

        Args:
            raw: dict returned by _nearest_raw()

        Returns:
            NearestResult object
        """
        waypoints = [Waypoint.from_raw(w) for w in raw["waypoints"]]  # required
        return cls(waypoints=waypoints)


# =============================================================================
# Match API Result
# =============================================================================


@dataclass(frozen=True, slots=True)
class Matching:
    """
    A matched route from Match API

    Attributes:
        distance: Total route distance in meters
        duration: Total route duration in seconds
        confidence: Confidence of the matching (0.0 to 1.0)
        geometry: Polyline encoded geometry string
    """

    distance: float
    duration: float
    confidence: float
    geometry: str = ""

    @classmethod
    def from_raw(cls, raw: dict) -> Matching:
        """Create Matching object from raw dict"""
        return cls(
            distance=raw["distance"],  # required
            duration=raw["duration"],  # required
            confidence=raw["confidence"],  # required
            geometry=raw.get("geometry", ""),  # optional (depends on overview param)
        )


@dataclass(frozen=True, slots=True)
class Tracepoint:
    """
    A matched point from Match API

    Attributes:
        location: Snapped coordinate
        name: Street name
        matchings_index: Index of the matching this tracepoint belongs to
        waypoint_index: Index within the matching's waypoints
    """

    location: Coordinate
    name: str = ""
    matchings_index: int = 0
    waypoint_index: int = 0

    @classmethod
    def from_raw(cls, raw: dict | None) -> Tracepoint | None:
        """Create Tracepoint object from raw dict (None if unmatched)"""
        if raw is None:
            return None
        loc = raw["location"]  # required
        return cls(
            location=Coordinate(longitude=loc[0], latitude=loc[1]),
            name=raw.get("name", ""),  # optional
            matchings_index=raw["matchings_index"],  # required
            waypoint_index=raw["waypoint_index"],  # required
        )

    @property
    def longitude(self) -> float:
        """Access longitude directly"""
        return self.location.longitude

    @property
    def latitude(self) -> float:
        """Access latitude directly"""
        return self.location.latitude


@dataclass
class MatchResult:
    """
    OSRM Match API response result

    Attributes:
        matchings: List of matched routes
        tracepoints: List of matched points (None if point was unmatched)
    """

    matchings: list[Matching]
    tracepoints: list[Tracepoint | None]

    @classmethod
    def from_raw(cls, raw: dict) -> MatchResult:
        """
        Convert C++ _match_raw() result to MatchResult

        Args:
            raw: dict returned by _match_raw()

        Returns:
            MatchResult object
        """
        matchings = [Matching.from_raw(m) for m in raw["matchings"]]  # required
        tracepoints = [Tracepoint.from_raw(t) for t in raw["tracepoints"]]  # required
        return cls(matchings=matchings, tracepoints=tracepoints)


# =============================================================================
# Trip API Result
# =============================================================================


@dataclass(frozen=True, slots=True)
class TripWaypoint:
    """
    Waypoint information for Trip API with trip-specific indices

    Attributes:
        location: Snapped coordinate
        name: Street name
        trips_index: Index of the trip this waypoint belongs to
        waypoint_index: Original index in the input coordinates
    """

    location: Coordinate
    name: str = ""
    trips_index: int = 0
    waypoint_index: int = 0

    @classmethod
    def from_raw(cls, raw: dict) -> TripWaypoint:
        """Create TripWaypoint object from raw dict"""
        loc = raw["location"]  # required
        return cls(
            location=Coordinate(longitude=loc[0], latitude=loc[1]),
            name=raw.get("name", ""),  # optional
            trips_index=raw["trips_index"],  # required
            waypoint_index=raw["waypoint_index"],  # required
        )

    @property
    def longitude(self) -> float:
        """Access longitude directly"""
        return self.location.longitude

    @property
    def latitude(self) -> float:
        """Access latitude directly"""
        return self.location.latitude


@dataclass
class TripResult:
    """
    OSRM Trip API response result

    Attributes:
        distance: Total trip distance in meters
        duration: Total trip duration in seconds
        waypoints: List of waypoints in optimized visit order
    """

    distance: float
    duration: float
    waypoints: list[TripWaypoint]

    @classmethod
    def from_raw(cls, raw: dict) -> TripResult:
        """
        Convert C++ _trip_raw() result to TripResult

        Args:
            raw: dict returned by _trip_raw()

        Returns:
            TripResult object
        """
        # Get the first trip (best trip)
        trips = raw["trips"]  # required
        if not trips:
            raise ValueError("No trips found in response")

        trip = trips[0]

        # Extract distance and duration
        distance = trip["distance"]  # required
        duration = trip["duration"]  # required

        # Convert waypoints
        waypoints = [TripWaypoint.from_raw(w) for w in raw["waypoints"]]  # required

        return cls(
            distance=distance,
            duration=duration,
            waypoints=waypoints,
        )
