"""
Official DIGIPIN Encoder

Implements hierarchical 4x4 grid subdivision encoding as per the official
DIGIPIN specification by Department of Posts, Government of India.

This is the CORE algorithm that converts latitude/longitude coordinates
into 10-character DIGIPIN codes using spiral anticlockwise labeling.
"""

from typing import Tuple
from .utils import (
    LAT_MIN,
    LAT_MAX,
    LON_MIN,
    LON_MAX,
    DIGIPIN_LEVELS,
    GRID_SUBDIVISION,
    validate_coordinate,
    get_symbol_from_position,
)


def encode(lat: float, lon: float, *, precision: int = 10) -> str:
    """
    Encode latitude and longitude into an official DIGIPIN code.

    Implements the hierarchical 4x4 grid subdivision algorithm with
    spiral anticlockwise labeling pattern as specified by Department
    of Posts, Government of India (March 2025).

    Algorithm:
    1. Start with official India bounding box (36° x 36°)
    2. For each of 10 levels:
       a. Divide current region into 4x4 grid
       b. Find which sub-grid contains the point
       c. Map position to symbol using spiral pattern
       d. Append symbol to code
       e. Narrow bounds to selected sub-grid
    3. Return 10-character code

    Args:
        lat: Latitude in degrees North (must be 2.5° to 38.5°)
        lon: Longitude in degrees East (must be 63.5° to 99.5°)
        precision: Code length (1-10), default 10 for full precision (~3.8m)

    Returns:
        DIGIPIN code string

    Raises:
        ValueError: If coordinates are outside official bounding box

    Example:
        >>> encode(28.622788, 77.213033)  # Dak Bhawan, New Delhi
        '39J49LL8T4'

        >>> encode(12.9716, 77.5946)  # Bengaluru
        '58C4K9FF72'

        >>> encode(19.0760, 72.8777, precision=6)  # Mumbai, 6 chars
        '48F4F8'
    """
    # Validate coordinates
    validate_coordinate(lat, lon)

    # Validate precision
    if not (1 <= precision <= DIGIPIN_LEVELS):
        raise ValueError(
            f"Precision must be between 1 and {DIGIPIN_LEVELS}, got {precision}"
        )

    # Initialize bounding box
    min_lat, max_lat = LAT_MIN, LAT_MAX
    min_lon, max_lon = LON_MIN, LON_MAX

    code = ""

    # Hierarchical subdivision: 10 levels
    for level in range(1, precision + 1):
        # Calculate grid cell size at this level
        lat_span = (max_lat - min_lat) / GRID_SUBDIVISION
        lon_span = (max_lon - min_lon) / GRID_SUBDIVISION

        # Determine which 4x4 sub-grid contains the point
        # Row: 0 (North) to 3 (South)
        # Col: 0 (West) to 3 (East)

        # Calculate grid position (from official implementation)
        # Row is REVERSED: calculate from bottom (min_lat) then flip
        row = 3 - int((lat - min_lat) / lat_span)

        # Column: calculate from left (min_lon)
        col = int((lon - min_lon) / lon_span)

        # Clamp to valid range [0, 3]
        row = max(0, min(row, 3))
        col = max(0, min(col, 3))

        # Get symbol for this grid position using official grid
        symbol = get_symbol_from_position(row, col)
        code += symbol

        # Update bounds using official logic (reversed for row)
        # Row bounds (note the reversed logic from official JS implementation)
        max_lat = min_lat + lat_span * (4 - row)
        min_lat = min_lat + lat_span * (3 - row)

        # Column bounds
        min_lon = min_lon + lon_span * col
        max_lon = min_lon + lon_span

    return code


def batch_encode(coordinates: list, **kwargs) -> list:
    """
    Encode multiple coordinate pairs in batch.

    Args:
        coordinates: List of (lat, lon) tuples
        **kwargs: Additional arguments passed to encode()

    Returns:
        List of DIGIPIN codes

    Example:
        >>> coords = [(28.622788, 77.213033), (12.9716, 77.5946)]
        >>> batch_encode(coords)
        ['39J49LL8T4', '58C4K9FF72']
    """
    return [encode(lat, lon, **kwargs) for lat, lon in coordinates]


def encode_with_bounds(lat: float, lon: float, **kwargs) -> dict:
    """
    Encode coordinates and return code with grid cell bounds.

    Args:
        lat: Latitude
        lon: Longitude
        **kwargs: Additional arguments for encode()

    Returns:
        Dictionary with 'code' and 'bounds' (min_lat, max_lat, min_lon, max_lon)

    Example:
        >>> result = encode_with_bounds(28.622788, 77.213033)
        >>> result['code']
        '39J49LL8T4'
        >>> result['bounds']  # Grid cell boundaries
        (28.622..., 28.622..., 77.213..., 77.213...)
    """
    from .decoder import get_bounds  # Avoid circular import

    code = encode(lat, lon, **kwargs)
    bounds = get_bounds(code)

    return {"code": code, "lat": lat, "lon": lon, "bounds": bounds}
