"""
OSRM Engine wrapper

High-level Python interface for OSRM services
"""

from __future__ import annotations

from ._libosrmpy import OSRM as _OSRM, EngineConfig, Algorithm, StorageConfig
from .schema import (
    Coordinate,
    TableResult,
    RouteResult,
    NearestResult,
    MatchResult,
    TripResult,
    TripSource,
    TripDestination,
)


class Engine:
    """
    OSRM Engine for routing services

    Example:
        >>> from libosrmpy.schema import Coordinate
        >>> engine = Engine("/data/berlin.osrm")
        >>> coords = [
        ...     Coordinate(longitude=13.388, latitude=52.517),
        ...     Coordinate(longitude=13.397, latitude=52.529),
        ... ]
        >>> result = engine.table(coords)
        >>> print(result.durations)
    """

    def __init__(
        self,
        data_path: str,
        algorithm: Algorithm = Algorithm.MLD,
        use_shared_memory: bool = False,
    ):
        """
        Initialize OSRM engine

        Args:
            data_path: Path to .osrm data file (without extension)
            algorithm: Routing algorithm (Algorithm.CH or Algorithm.MLD)
            use_shared_memory: Use shared memory for data (requires osrm-datastore)
        """
        config = EngineConfig()
        config.storage_config = StorageConfig(data_path)
        config.algorithm = algorithm
        config.use_shared_memory = use_shared_memory
        self._osrm = _OSRM(config)

    def table(
        self,
        coordinates: list[Coordinate],
        sources: list[int] | None = None,
        destinations: list[int] | None = None,
    ) -> TableResult:
        """
        Calculate duration/distance matrix between coordinates

        Args:
            coordinates: List of Coordinate objects
            sources: Source indices (default: all coordinates)
            destinations: Destination indices (default: all coordinates)

        Returns:
            TableResult with durations and distances matrices
        """
        num_coords = len(coordinates)

        if sources:
            for s in sources:
                if not (0 <= s < num_coords):
                    raise IndexError(f"Source index {s} is out of bounds (0 to {num_coords - 1})")

        if destinations:
            for d in destinations:
                if not (0 <= d < num_coords):
                    raise IndexError(
                        f"Destination index {d} is out of bounds (0 to {num_coords - 1})"
                    )

        coords_tuples = [c.to_tuple() for c in coordinates]
        raw = self._osrm._table_raw(coords_tuples, sources, destinations)
        return TableResult.from_raw(raw)

    def route(
        self,
        coordinates: list[Coordinate],
    ) -> RouteResult:
        """
        Calculate route between coordinates

        Args:
            coordinates: List of Coordinate objects (at least 2)

        Returns:
            RouteResult with distance, duration, and waypoints
        """
        if len(coordinates) < 2:
            raise ValueError("At least 2 coordinates are required")

        coords_tuples = [c.to_tuple() for c in coordinates]
        raw = self._osrm._route_raw(coords_tuples)
        return RouteResult.from_raw(raw)

    def nearest(
        self,
        coordinate: Coordinate,
        number_of_results: int = 1,
    ) -> NearestResult:
        """
        Find nearest road network point(s) to a coordinate

        Args:
            coordinate: Coordinate to snap to road network
            number_of_results: Number of nearest points to return (default: 1)

        Returns:
            NearestResult with list of nearest waypoints
        """
        if number_of_results < 1:
            raise ValueError("number_of_results must be at least 1")

        coord_tuple = coordinate.to_tuple()
        raw = self._osrm._nearest_raw(coord_tuple, number_of_results)
        return NearestResult.from_raw(raw)

    def match(
        self,
        coordinates: list[Coordinate],
        timestamps: list[int] | None = None,
        radiuses: list[float] | None = None,
    ) -> MatchResult:
        """
        Match GPS trace to road network

        Args:
            coordinates: List of GPS coordinates (at least 2)
            timestamps: Optional Unix timestamps for each coordinate
            radiuses: Optional search radius in meters for each coordinate

        Returns:
            MatchResult with matched routes and tracepoints
        """
        if len(coordinates) < 2:
            raise ValueError("At least 2 coordinates are required for matching")

        num_coords = len(coordinates)

        if timestamps is not None and len(timestamps) != num_coords:
            raise ValueError(
                f"timestamps length ({len(timestamps)}) must match coordinates length ({num_coords})"
            )

        if radiuses is not None and len(radiuses) != num_coords:
            raise ValueError(
                f"radiuses length ({len(radiuses)}) must match coordinates length ({num_coords})"
            )

        coords_tuples = [c.to_tuple() for c in coordinates]
        raw = self._osrm._match_raw(coords_tuples, timestamps, radiuses)
        return MatchResult.from_raw(raw)

    def trip(
        self,
        coordinates: list[Coordinate],
        roundtrip: bool = True,
        source: TripSource = TripSource.ANY,
        destination: TripDestination = TripDestination.ANY,
    ) -> TripResult:
        """
        Calculate optimal trip visiting all coordinates (TSP solver)

        Args:
            coordinates: List of coordinates to visit (at least 2)
            roundtrip: Return to starting point (default: True)
            source: Source constraint - ANY or FIRST (default: ANY)
            destination: Destination constraint - ANY or LAST (default: ANY)

        Returns:
            TripResult with optimized route and waypoints
        """
        if len(coordinates) < 2:
            raise ValueError("At least 2 coordinates are required for trip")

        coords_tuples = [c.to_tuple() for c in coordinates]
        raw = self._osrm._trip_raw(
            coords_tuples,
            roundtrip,
            source.value,
            destination.value,
        )
        return TripResult.from_raw(raw)
