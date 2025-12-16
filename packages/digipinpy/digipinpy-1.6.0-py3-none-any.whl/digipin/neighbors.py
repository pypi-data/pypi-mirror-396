"""
Neighbor Discovery Module for DIGIPIN

This module provides functionality to identify adjacent grid cells
for any given DIGIPIN code. It enables "proximity search" and
"area expansion" use cases.

This is a CRITICAL feature for production applications:
- Delivery routing: "Find warehouses near this address"
- Emergency services: "Which ambulances can reach this location?"
- Real estate: "Show properties within 100m of this pin"
- Restaurant search: "What's nearby?"

Algorithm:
----------
Instead of trying to manipulate DIGIPIN codes directly (complex due to
the spiral labeling and hierarchical structure), we use a robust
coordinate-based approach:

1. Decode the center code to lat/lon
2. Calculate offset coordinates (±1 cell in each direction)
3. Re-encode to get neighbor codes
4. This naturally handles boundary crossing between parent grids

Example of Boundary Crossing:
-----------------------------
Center: 39J49LL8T4 (ends in 'T' - southeast corner of parent grid)
East neighbor: Actually in a DIFFERENT parent grid
Direct calculation: Would need complex spiral unwrapping
Our approach: Decode → offset → encode (automatic!)
"""

from typing import List, Set
from .decoder import decode
from .encoder import encode
from .utils import get_grid_size, is_valid_coordinate, is_valid_digipin


def get_neighbors(code: str, direction: str = "all") -> List[str]:
    """
    Get immediate neighboring grid cells for a DIGIPIN code.

    This function handles the complexity of "boundary crossing" where a
    neighbor might reside in a different parent grid (e.g., moving East
    from a cell ending in 'T' changes the parent code).

    Args:
        code: The central DIGIPIN code (1-10 characters).
        direction: Which neighbors to fetch.
                   Options:
                   - 'all' (8 neighbors - default)
                   - 'cardinal' (4 neighbors: N, S, E, W)
                   - Specific: 'north', 'south', 'east', 'west',
                              'northeast', 'northwest', 'southeast', 'southwest'

    Returns:
        List of valid DIGIPIN codes for the neighbors.

        Note: Returns fewer than requested if a neighbor falls outside
        the official India bounding box (e.g., ocean or border edges).
        The center code itself is never included in the results.

    Raises:
        ValueError: If code is invalid or direction is not recognized

    Examples:
        >>> # Get all 8 surrounding cells
        >>> get_neighbors('39J49LL8T4')
        ['39J49LL8T9', '39J49LL8TC', '39J49LL8T5', ...]

        >>> # Get only cardinal directions (N, S, E, W)
        >>> get_neighbors('39J49LL8T4', direction='cardinal')
        ['39J49LL8T9', '39J49LL8T3', '39J49LL8T5', '39J49LL8TF']

        >>> # Get specific direction
        >>> get_neighbors('39J49LL8T4', direction='north')
        ['39J49LL8T9']

        >>> # Edge case: Code at boundary may have fewer neighbors
        >>> # (neighbors outside India's bounding box are excluded)
        >>> get_neighbors('2XXXXXXXXX')  # Near southern edge
        [...]  # May return only 5-6 neighbors instead of 8

    Performance:
        - Time complexity: O(n) where n = number of directions (max 8)
        - Each neighbor requires: 1 decode + 1 encode + 1 validation
        - Typical execution: ~200μs for all 8 neighbors
    """
    # Validate input code
    if not is_valid_digipin(code):
        raise ValueError(
            f"Invalid DIGIPIN code: '{code}'. "
            f"Must be 1-10 characters using alphabet: 23456789CFJKLMPT"
        )

    code = code.upper()  # Normalize to uppercase
    level = len(code)

    # Get geometric properties of the current cell
    center_lat, center_lon = decode(code)

    # Get the dimensions of a single cell at this level
    lat_span, lon_span = get_grid_size(level)

    # Define offsets for all 8 directions
    # Format: (latitude_multiplier, longitude_multiplier)
    # Remember: Latitude increases northward, Longitude increases eastward
    offsets = {
        "north": (1, 0),  # Move up
        "northeast": (1, 1),  # Move up and right
        "east": (0, 1),  # Move right
        "southeast": (-1, 1),  # Move down and right
        "south": (-1, 0),  # Move down
        "southwest": (-1, -1),  # Move down and left
        "west": (0, -1),  # Move left
        "northwest": (1, -1),  # Move up and left
    }

    # Filter offsets based on requested direction
    if direction == "all":
        selected_offsets = offsets
    elif direction == "cardinal":
        selected_offsets = {k: offsets[k] for k in ["north", "south", "east", "west"]}
    elif direction in offsets:
        selected_offsets = {direction: offsets[direction]}
    else:
        valid_options = list(offsets.keys()) + ["all", "cardinal"]
        raise ValueError(
            f"Invalid direction '{direction}'. "
            f"Must be one of: {', '.join(valid_options)}"
        )

    neighbors = []

    # Calculate and encode neighbors
    for _, (lat_mult, lon_mult) in selected_offsets.items():
        # Calculate neighbor centroid
        # We use 1.0 * span to move exactly one cell over
        n_lat = center_lat + (lat_mult * lat_span)
        n_lon = center_lon + (lon_mult * lon_span)

        # Check if the calculated coordinate is valid (inside India bounds)
        # This handles the "Edge of Coverage" problem
        if is_valid_coordinate(n_lat, n_lon):
            try:
                # Encode back to DIGIPIN at the SAME level/precision
                n_code = encode(n_lat, n_lon, precision=level)

                # Prevent returning self (rare edge case with floating point)
                if n_code != code:
                    neighbors.append(n_code)
            except ValueError:
                # Should be caught by is_valid_coordinate, but safety first
                continue

    return neighbors


def get_ring(code: str, radius: int) -> List[str]:
    """
    Get all grid cells at exactly 'radius' distance from center (hollow ring).

    Uses Chebyshev distance (chessboard distance) where diagonal moves
    count as 1 step, same as cardinal moves.

    Args:
        code: Center DIGIPIN code
        radius: Distance in cells (must be >= 1)

    Returns:
        List of unique codes forming the ring at specified radius.
        Excludes cells outside India's bounding box.

    Raises:
        ValueError: If radius < 1 or code is invalid

    Examples:
        >>> # Get cells exactly 1 step away (8 immediate neighbors)
        >>> get_ring('39J49LL8T4', radius=1)
        ['39J49LL8T9', '39J49LL8TC', ...]  # 8 neighbors

        >>> # Get cells exactly 2 steps away (16 cells forming outer ring)
        >>> get_ring('39J49LL8T4', radius=2)
        [...]  # Up to 16 cells (may be fewer at boundaries)

    Performance:
        - For radius R: Returns up to 8*R cells
        - Time complexity: O(R)
    """
    if radius < 1:
        raise ValueError(f"Radius must be >= 1, got {radius}")

    if not is_valid_digipin(code):
        raise ValueError(f"Invalid DIGIPIN code: '{code}'")

    code = code.upper()
    level = len(code)
    center_lat, center_lon = decode(code)
    lat_span, lon_span = get_grid_size(level)

    codes = set()

    # For a ring at radius R, we need cells where max(|dx|, |dy|) = R
    # This means either |dx| = R or |dy| = R (or both)

    # Top and bottom edges (full width)
    for dx in range(-radius, radius + 1):
        for dy in [radius, -radius]:
            n_lat = center_lat + (dy * lat_span)
            n_lon = center_lon + (dx * lon_span)

            if is_valid_coordinate(n_lat, n_lon):
                try:
                    n_code = encode(n_lat, n_lon, precision=level)
                    if n_code != code:
                        codes.add(n_code)
                except ValueError:
                    continue

    # Left and right edges (excluding corners already added)
    for dy in range(-radius + 1, radius):
        for dx in [radius, -radius]:
            n_lat = center_lat + (dy * lat_span)
            n_lon = center_lon + (dx * lon_span)

            if is_valid_coordinate(n_lat, n_lon):
                try:
                    n_code = encode(n_lat, n_lon, precision=level)
                    if n_code != code:
                        codes.add(n_code)
                except ValueError:
                    continue

    return list(codes)


def get_disk(code: str, radius: int = 1) -> List[str]:
    """
    Get all grid cells within a specific cell radius (filled disk).

    Uses Chebyshev distance (chessboard distance). The result is a
    square area of (2*radius + 1) × (2*radius + 1) cells centered
    on the input code.

    This is the most useful function for "search nearby" queries.

    Args:
        code: Center DIGIPIN code
        radius: Number of cell layers to expand (must be >= 0)
                - 0: Just the center cell
                - 1: 3×3 grid (center + 8 neighbors)
                - 2: 5×5 grid (25 cells total)
                - n: (2n+1)×(2n+1) grid

    Returns:
        List of unique codes covering the disk area, including center.
        Excludes cells outside India's bounding box.

    Raises:
        ValueError: If radius < 0 or code is invalid

    Examples:
        >>> # Just the center cell
        >>> get_disk('39J49LL8T4', radius=0)
        ['39J49LL8T4']

        >>> # Center + 8 immediate neighbors (3×3 grid)
        >>> get_disk('39J49LL8T4', radius=1)
        ['39J49LL8T4', '39J49LL8T9', '39J49LL8TC', ...]  # 9 cells

        >>> # 5×5 grid for wider search area
        >>> codes = get_disk('39J49LL8T4', radius=2)
        >>> len(codes)
        25  # (or fewer if near boundary)

    Use Cases:
        >>> # Delivery search: Find warehouses within ~40m
        >>> # (Level 10 cells are ~3.8m, so radius=10 ≈ 38m)
        >>> customer_code = encode(lat, lon)
        >>> search_area = get_disk(customer_code, radius=10)
        >>> nearby_warehouses = db.query(Warehouse).filter(
        ...     Warehouse.digipin.in_(search_area)
        ... )

        >>> # Emergency response: Alert users in flood zone
        >>> # (Level 8 cells are ~60m, so radius=5 ≈ 300m)
        >>> incident_code = encode(incident_lat, incident_lon, precision=8)
        >>> affected_area = get_disk(incident_code, radius=5)
        >>> users_at_risk = User.objects.filter(digipin__in=affected_area)

    Performance:
        - For radius R: Returns up to (2R+1)² cells
        - Time complexity: O(R²)
        - Radius 1: ~9 cells, ~300μs
        - Radius 10: ~121 cells, ~4ms
        - Radius 100: ~10,000 cells, ~400ms
    """
    if radius < 0:
        raise ValueError(f"Radius must be >= 0, got {radius}")

    if not is_valid_digipin(code):
        raise ValueError(f"Invalid DIGIPIN code: '{code}'")

    code = code.upper()
    level = len(code)
    center_lat, center_lon = decode(code)
    lat_span, lon_span = get_grid_size(level)

    codes = set()

    # Iterate through the square grid from -R to +R
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            n_lat = center_lat + (dy * lat_span)
            n_lon = center_lon + (dx * lon_span)

            if is_valid_coordinate(n_lat, n_lon):
                try:
                    n_code = encode(n_lat, n_lon, precision=level)
                    codes.add(n_code)
                except ValueError:
                    continue

    return list(codes)


# Convenience aliases for common use cases
def get_surrounding_cells(code: str) -> List[str]:
    """
    Alias for get_neighbors(code, direction='all').
    Returns all 8 immediate neighbors.
    """
    return get_neighbors(code, direction="all")


def expand_search_area(code: str, radius: int = 1) -> List[str]:
    """
    Alias for get_disk(code, radius).
    Returns all cells within radius distance (including center).
    """
    return get_disk(code, radius)
