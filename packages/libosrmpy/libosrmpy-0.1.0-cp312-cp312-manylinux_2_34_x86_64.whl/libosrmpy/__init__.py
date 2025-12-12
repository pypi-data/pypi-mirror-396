"""
libosrmpy - Python bindings for libosrm

Python bindings for the OSRM (Open Source Routing Machine) C++ library
"""

# High-level API
from .engine import Engine

# Algorithm enum from C++ bindings
from ._libosrmpy import Algorithm

# Schema (DTOs)
from .schema import (
    Coordinate,
    Waypoint,
    TableResult,
    RouteResult,
    NearestResult,
    Matching,
    Tracepoint,
    MatchResult,
    TripWaypoint,
    TripResult,
    TripSource,
    TripDestination,
)

__all__ = [
    # Core
    "Engine",
    "Algorithm",
    # Schema - Input
    "Coordinate",
    # Schema - Table API
    "Waypoint",
    "TableResult",
    # Schema - Route API
    "RouteResult",
    # Schema - Nearest API
    "NearestResult",
    # Schema - Match API
    "Matching",
    "Tracepoint",
    "MatchResult",
    # Schema - Trip API
    "TripWaypoint",
    "TripResult",
    "TripSource",
    "TripDestination",
]
