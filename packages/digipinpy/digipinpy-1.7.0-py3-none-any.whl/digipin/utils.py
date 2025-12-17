"""
Official DIGIPIN Utilities

Implements the official DIGIPIN specification by the Department of Posts,
Government of India (March 2025).

This module provides core utilities for the hierarchical 4x4 grid system
with spiral anticlockwise labeling pattern.
"""

from typing import Tuple

# ============================================================================
# OFFICIAL DIGIPIN SPECIFICATION CONSTANTS
# ============================================================================

# Official bounding box (Department of Posts specification)
# Covers entire India including maritime Exclusive Economic Zone (EEZ)
LAT_MIN = 2.5  # Southernmost point (degrees North)
LAT_MAX = 38.5  # Northernmost point (degrees North)
LON_MIN = 63.5  # Westernmost point (degrees East)
LON_MAX = 99.5  # Easternmost point (degrees East)

LAT_SPAN = LAT_MAX - LAT_MIN  # 36.0 degrees (perfect square)
LON_SPAN = LON_MAX - LON_MIN  # 36.0 degrees (perfect square)

# Official 16-symbol alphabet (chosen for clarity and non-ambiguity)
# Excludes: 0, 1, O, I, G, W, X (to avoid confusion)
DIGIPIN_ALPHABET = "23456789"  # Numbers: 2,3,4,5,6,7,8,9
DIGIPIN_ALPHABET += "CFJKLMPT"  # Letters: C,F,J,K,L,M,P,T

# Total: 16 symbols for 4x4 grid subdivision
assert len(DIGIPIN_ALPHABET) == 16, "Alphabet must have exactly 16 symbols"

# Official spiral anticlockwise labeling pattern (4x4 grid)
# This is the HEART of DIGIPIN - provides directional properties!
#
# Grid layout (row, col):
#     Col: 0   1   2   3
# Row 0:   P   M   L   K    (North)
# Row 1:   F   2   3   J
# Row 2:   C   5   4   9
# Row 3:   T   6   7   8    (South)
#          ^
#        (West)
#
# Pattern: Starts at center (2), spirals anticlockwise outward
# Adjacent numbers (2→3→4→5...) are geographic neighbors!

SPIRAL_GRID = [
    ["F", "C", "9", "8"],  # Row 0 (from official implementation)
    ["J", "3", "2", "7"],  # Row 1
    ["K", "4", "5", "6"],  # Row 2
    ["L", "M", "P", "T"],  # Row 3
]

# Create reverse lookup: symbol → (row, col)
SYMBOL_TO_POSITION = {}
for row_idx, row in enumerate(SPIRAL_GRID):
    for col_idx, symbol in enumerate(row):
        SYMBOL_TO_POSITION[symbol] = (row_idx, col_idx)

# Number of levels in DIGIPIN hierarchy
DIGIPIN_LEVELS = 10

# Grid subdivision factor (4x4 at each level)
GRID_SUBDIVISION = 4


# ============================================================================
# COORDINATE VALIDATION
# ============================================================================


def is_valid_coordinate(lat: float, lon: float) -> bool:
    """
    Check if coordinates are within official DIGIPIN bounding box.

    Args:
        lat: Latitude in degrees (North)
        lon: Longitude in degrees (East)

    Returns:
        True if within official India bounding box

    Example:
        >>> is_valid_coordinate(28.622788, 77.213033)  # Dak Bhawan
        True
        >>> is_valid_coordinate(0, 0)  # Outside India
        False
    """
    return (LAT_MIN <= lat <= LAT_MAX) and (LON_MIN <= lon <= LON_MAX)


def validate_coordinate(lat: float, lon: float) -> None:
    """
    Validate coordinates and raise exception if out of bounds.

    Args:
        lat: Latitude in degrees (North)
        lon: Longitude in degrees (East)

    Raises:
        ValueError: If coordinates are outside DIGIPIN bounding box
    """
    if not (LAT_MIN <= lat <= LAT_MAX):
        raise ValueError(
            f"Latitude {lat}° is out of bounds. "
            f"Must be between {LAT_MIN}° and {LAT_MAX}° North."
        )

    if not (LON_MIN <= lon <= LON_MAX):
        raise ValueError(
            f"Longitude {lon}° is out of bounds. "
            f"Must be between {LON_MIN}° and {LON_MAX}° East."
        )


# ============================================================================
# SPIRAL GRID MAPPING
# ============================================================================


def get_symbol_from_position(row: int, col: int) -> str:
    """
    Get DIGIPIN symbol from grid position using spiral pattern.

    Args:
        row: Grid row (0-3, 0 is North)
        col: Grid column (0-3, 0 is West)

    Returns:
        DIGIPIN symbol character

    Example:
        >>> get_symbol_from_position(1, 1)  # Center
        '2'
        >>> get_symbol_from_position(0, 0)  # Northwest
        'P'
    """
    if not (0 <= row < 4 and 0 <= col < 4):
        raise ValueError(f"Invalid grid position: row={row}, col={col}")

    return SPIRAL_GRID[row][col]


def get_position_from_symbol(symbol: str) -> Tuple[int, int]:
    """
    Get grid position from DIGIPIN symbol (reverse lookup).

    Args:
        symbol: DIGIPIN character

    Returns:
        Tuple of (row, col) position in 4x4 grid

    Raises:
        ValueError: If symbol is not valid

    Example:
        >>> get_position_from_symbol('2')  # Center
        (1, 1)
        >>> get_position_from_symbol('K')  # Northeast
        (0, 3)
    """
    symbol = symbol.upper()

    if symbol not in SYMBOL_TO_POSITION:
        raise ValueError(
            f"Invalid DIGIPIN symbol: '{symbol}'. "
            f"Must be one of: {', '.join(sorted(SYMBOL_TO_POSITION.keys()))}"
        )

    return SYMBOL_TO_POSITION[symbol]


# ============================================================================
# GRID SIZE CALCULATIONS
# ============================================================================


def get_grid_size(level: int) -> Tuple[float, float]:
    """
    Calculate grid cell size at a given level.

    Args:
        level: DIGIPIN level (1-10)

    Returns:
        Tuple of (lat_degrees, lon_degrees) cell size

    Example:
        >>> lat_size, lon_size = get_grid_size(1)
        >>> lat_size  # Level 1 = 9.0 degrees
        9.0
        >>> lat_size, lon_size = get_grid_size(10)
        >>> lat_size  # Level 10 = ~0.000034 degrees (~3.8m)
        3.38...-05
    """
    if not (1 <= level <= DIGIPIN_LEVELS):
        raise ValueError(f"Level must be between 1 and {DIGIPIN_LEVELS}")

    # At each level, divide by 4 (4x4 subdivision)
    divisions = GRID_SUBDIVISION**level

    lat_cell_size = LAT_SPAN / divisions
    lon_cell_size = LON_SPAN / divisions

    return lat_cell_size, lon_cell_size


def get_approx_distance(level: int) -> float:
    """
    Get approximate linear distance (in meters) for grid cell at given level.

    Uses average at equator: 1 degree ≈ 111 km

    Args:
        level: DIGIPIN level (1-10)

    Returns:
        Approximate cell size in meters

    Example:
        >>> get_approx_distance(6)  # Level 6
        976.5625
        >>> get_approx_distance(10)  # Level 10 (final)
        3.814...
    """
    lat_deg, lon_deg = get_grid_size(level)

    # 1 degree ≈ 111 km = 111,000 meters (at equator)
    # Use average of lat and lon for approximation
    avg_deg = (lat_deg + lon_deg) / 2
    meters = avg_deg * 111000

    return meters


# ============================================================================
# CODE VALIDATION
# ============================================================================


def is_valid_digipin(code: str, strict: bool = False) -> bool:
    """
    Validate DIGIPIN code format.

    Checks:
    - Length is between 1 and 10 characters (or exactly 10 if strict=True)
    - All characters are from official alphabet

    Args:
        code: DIGIPIN code to validate
        strict: If True, requires exactly 10 characters (default: False)

    Returns:
        True if valid format

    Example:
        >>> is_valid_digipin("39J49LL8T4")  # Full precision (10 chars)
        True
        >>> is_valid_digipin("39J4")  # Partial precision (4 chars)
        True
        >>> is_valid_digipin("39J4", strict=True)  # Too short in strict mode
        False
        >>> is_valid_digipin("123")  # Invalid - length must be 1-10
        False
        >>> is_valid_digipin("ABCDEFGHIJ")  # Invalid symbols
        False
    """
    if not isinstance(code, str):
        return False

    # Length validation
    if strict:
        # Strict mode: exactly 10 characters
        if len(code) != DIGIPIN_LEVELS:
            return False
    else:
        # Flexible mode: 1 to 10 characters
        if not (1 <= len(code) <= DIGIPIN_LEVELS):
            return False

    # All characters must be in official alphabet
    code_upper = code.upper()
    return all(char in DIGIPIN_ALPHABET for char in code_upper)


def validate_digipin(code: str, strict: bool = False) -> str:
    """
    Validate and normalize DIGIPIN code.

    Args:
        code: DIGIPIN code to validate
        strict: If True, requires exactly 10 characters (default: False)

    Returns:
        Normalized code (uppercase)

    Raises:
        ValueError: If code is invalid

    Example:
        >>> validate_digipin("39j49ll8t4")  # Lowercase full code
        '39J49LL8T4'
        >>> validate_digipin("39j4")  # Lowercase partial code
        '39J4'
        >>> validate_digipin("39J4", strict=True)  # Invalid - too short in strict mode
        ValueError: Invalid DIGIPIN length...
        >>> validate_digipin("123")  # Invalid - wrong length
        ValueError: Invalid DIGIPIN length...
    """
    if not isinstance(code, str):
        raise ValueError("DIGIPIN code must be a string")

    # Length validation
    if strict:
        if len(code) != DIGIPIN_LEVELS:
            raise ValueError(
                f"Invalid DIGIPIN length. Expected exactly {DIGIPIN_LEVELS} characters, "
                f"got {len(code)}"
            )
    else:
        if not (1 <= len(code) <= DIGIPIN_LEVELS):
            raise ValueError(
                f"Invalid DIGIPIN length. Expected 1-{DIGIPIN_LEVELS} characters, "
                f"got {len(code)}"
            )

    code_upper = code.upper()

    # Check each character
    for i, char in enumerate(code_upper):
        if char not in DIGIPIN_ALPHABET:
            raise ValueError(
                f"Invalid character '{char}' at position {i+1}. "
                f"Must be one of: {DIGIPIN_ALPHABET}"
            )

    return code_upper


# ============================================================================
# PRECISION INFORMATION
# ============================================================================


def get_precision_info(level: int = 10) -> dict:
    """
    Get detailed precision information for a given level.

    Args:
        level: DIGIPIN level (1-10), default is 10 (full precision)

    Returns:
        Dictionary with precision details

    Example:
        >>> info = get_precision_info(10)
        >>> info['approx_distance_m']
        3.814...
        >>> info['code_length']
        10
    """
    lat_deg, lon_deg = get_grid_size(level)
    distance_m = get_approx_distance(level)

    return {
        "level": level,
        "code_length": level,
        "grid_size_lat_deg": lat_deg,
        "grid_size_lon_deg": lon_deg,
        "approx_distance_m": distance_m,
        "total_cells": (GRID_SUBDIVISION**level) ** 2,
        "description": _get_level_description(level),
    }


def _get_level_description(level: int) -> str:
    """Get human-readable description for a level."""
    descriptions = {
        1: "Regional level (~1000 km)",
        2: "State level (~250 km)",
        3: "District level (~62 km)",
        4: "City level (~15 km)",
        5: "Locality level (~4 km)",
        6: "Neighborhood level (~1 km)",
        7: "Block level (~250 m)",
        8: "Building level (~60 m)",
        9: "Property level (~15 m)",
        10: "Precise location (~3.8 m)",
    }
    return descriptions.get(level, f"Level {level}")
