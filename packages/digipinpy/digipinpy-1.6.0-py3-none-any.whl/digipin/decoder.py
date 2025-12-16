"""
Official DIGIPIN Decoder

Implements hierarchical 4x4 grid subdivision decoding to convert DIGIPIN
codes back to latitude/longitude coordinates.
"""

from typing import Tuple
from .utils import (
    LAT_MIN,
    LAT_MAX,
    LON_MIN,
    LON_MAX,
    DIGIPIN_LEVELS,
    GRID_SUBDIVISION,
    validate_digipin,
    get_position_from_symbol,
)


def decode(code: str) -> Tuple[float, float]:
    """
    Decode a DIGIPIN code to latitude and longitude coordinates.

    Returns the center point of the final grid cell represented by the code.

    Algorithm:
    1. Start with official India bounding box
    2. For each character in code:
       a. Map character to (row, col) using spiral pattern
       b. Divide current region into 4x4 grid
       c. Select the sub-grid at (row, col)
       d. Narrow bounds to that sub-grid
    3. Return center coordinates of final grid cell

    Args:
        code: 10-character DIGIPIN code

    Returns:
        Tuple of (latitude, longitude) in degrees
        Represents the CENTER of the grid cell

    Raises:
        ValueError: If code format is invalid

    Example:
        >>> decode('39J49LL8T4')  # Dak Bhawan
        (28.622788..., 77.213033...)

        >>> decode('58C4K9FF72')  # Bengaluru
        (12.9716..., 77.5946...)
    """
    # Validate and normalize code
    code = validate_digipin(code)

    # Initialize to full bounding box
    min_lat, max_lat = LAT_MIN, LAT_MAX
    min_lon, max_lon = LON_MIN, LON_MAX

    # Process each character to narrow down the grid
    for char in code:
        # Get grid position from symbol (using official grid)
        row, col = get_position_from_symbol(char)

        # Calculate grid cell size at this level
        lat_span = (max_lat - min_lat) / GRID_SUBDIVISION
        lon_span = (max_lon - min_lon) / GRID_SUBDIVISION

        # Update bounds using official decoding logic
        # Latitude bounds (calculated from top/maxLat)
        lat1 = max_lat - lat_span * (row + 1)
        lat2 = max_lat - lat_span * row

        # Longitude bounds (calculated from left/minLon)
        lon1 = min_lon + lon_span * col
        lon2 = min_lon + lon_span * (col + 1)

        # Update for next iteration
        min_lat = lat1
        max_lat = lat2
        min_lon = lon1
        max_lon = lon2

    # Return center point of final grid cell
    center_lat = (min_lat + max_lat) / 2
    center_lon = (min_lon + max_lon) / 2

    return center_lat, center_lon


def get_bounds(code: str) -> Tuple[float, float, float, float]:
    """
    Get the bounding box of the grid cell represented by a DIGIPIN code.

    Args:
        code: DIGIPIN code (1-10 characters)

    Returns:
        Tuple of (min_lat, max_lat, min_lon, max_lon) in degrees

    Example:
        >>> bounds = get_bounds('39J49LL8T4')
        >>> bounds  # ~3.8m x 3.8m cell boundaries
        (28.622785..., 28.622791..., 77.213029..., 77.213036...)

        >>> bounds = get_bounds('39J4')  # 4-char code = ~15km cell
        >>> bounds
        (27.5, 29.75, 74.75, 77.0)
    """
    # Validate code (can be partial - 1 to 10 chars)
    code_upper = code.upper()

    if len(code_upper) < 1 or len(code_upper) > DIGIPIN_LEVELS:
        raise ValueError(
            f"Code length must be between 1 and {DIGIPIN_LEVELS}, "
            f"got {len(code_upper)}"
        )

    # Initialize to full bounding box
    min_lat, max_lat = LAT_MIN, LAT_MAX
    min_lon, max_lon = LON_MIN, LON_MAX

    # Process each character
    for char in code_upper:
        # Get grid position
        row, col = get_position_from_symbol(char)

        # Calculate grid cell size
        lat_span = (max_lat - min_lat) / GRID_SUBDIVISION
        lon_span = (max_lon - min_lon) / GRID_SUBDIVISION

        # Update to selected sub-grid
        new_min_lat = max_lat - (row + 1) * lat_span
        new_max_lat = max_lat - row * lat_span
        new_min_lon = min_lon + col * lon_span
        new_max_lon = min_lon + (col + 1) * lon_span

        min_lat, max_lat = new_min_lat, new_max_lat
        min_lon, max_lon = new_min_lon, new_max_lon

    return min_lat, max_lat, min_lon, max_lon


def decode_with_bounds(code: str) -> dict:
    """
    Decode DIGIPIN and return both coordinates and bounding box.

    Args:
        code: DIGIPIN code

    Returns:
        Dictionary with 'lat', 'lon', and 'bounds'

    Example:
        >>> result = decode_with_bounds('39J49LL8T4')
        >>> result['lat']
        28.622788...
        >>> result['lon']
        77.213033...
        >>> result['bounds']
        (28.622785..., 28.622791..., 77.213029..., 77.213036...)
    """
    lat, lon = decode(code)
    bounds = get_bounds(code)

    return {"code": code.upper(), "lat": lat, "lon": lon, "bounds": bounds}


def batch_decode(codes: list) -> list:
    """
    Decode multiple DIGIPIN codes in batch.

    Args:
        codes: List of DIGIPIN codes

    Returns:
        List of (lat, lon) tuples

    Example:
        >>> batch_decode(['39J49LL8T4', '58C4K9FF72'])
        [(28.622788..., 77.213033...), (12.9716..., 77.5946...)]
    """
    return [decode(code) for code in codes]


def get_parent(code: str, level: int) -> str:
    """
    Get parent DIGIPIN code at a higher (coarser) level.

    Args:
        code: Full DIGIPIN code
        level: Parent level (1 to len(code)-1)

    Returns:
        Parent code (truncated to specified level)

    Example:
        >>> get_parent('39J49LL8T4', 6)  # Get neighborhood-level code
        '39J49L'

        >>> get_parent('39J49LL8T4', 1)  # Get regional-level code
        '3'
    """
    code = validate_digipin(code)

    if not (1 <= level < len(code)):
        raise ValueError(
            f"Parent level must be between 1 and {len(code)-1}, got {level}"
        )

    return code[:level]


def is_within(child_code: str, parent_code: str) -> bool:
    """
    Check if a DIGIPIN code is within a larger (parent) region.

    Args:
        child_code: Code to check
        parent_code: Parent region code (shorter)

    Returns:
        True if child is within parent region

    Example:
        >>> is_within('39J49LL8T4', '39J49L')  # Same neighborhood
        True

        >>> is_within('39J49LL8T4', '39')  # Same region
        True

        >>> is_within('39J49LL8T4', '48')  # Different region
        False
    """
    child = validate_digipin(child_code)
    parent = parent_code.upper()

    if len(parent) >= len(child):
        return False

    # Child is within parent if it starts with parent code
    return child.startswith(parent)
