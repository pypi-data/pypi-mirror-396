"""
Polyfill Module for DIGIPIN

Converts geometric shapes (Polygons) into sets of DIGIPIN codes.
Essential for geofencing, delivery zone definition, and service area mapping.

Requires:
    pip install digipinpy[geo]
"""

try:
    from shapely.geometry import Polygon, Point, box
    from shapely.prepared import prep

    SHAPELY_AVAILABLE = True
except ImportError:
    SHAPELY_AVAILABLE = False

from typing import List, Union, Tuple
from .encoder import encode
from .decoder import get_bounds
from .utils import get_grid_size


def polyfill(
    polygon: Union["Polygon", List[Tuple[float, float]]],
    precision: int = 7,
    algorithm: str = "quadtree",
) -> List[str]:
    """
    Fill a polygon with DIGIPIN codes of a specific precision.

    Two algorithms available:
    - 'quadtree' (default): O(Perimeter) - Fast, recommended for all use cases
    - 'grid': O(Area) - Legacy grid scan, kept for backwards compatibility

    The quadtree algorithm is 50-1000x faster on large polygons by only
    subdividing cells that intersect the polygon boundary.

    Args:
        polygon: A shapely Polygon object OR a list of (lat, lon) coordinates
                 defining the boundary.
        precision: The DIGIPIN level to use for filling (1-10).
                   Warning: High precision (9-10) on large areas will
                   generate huge lists. Recommended: 6-8 for city zones.
        algorithm: Algorithm to use - 'quadtree' (fast) or 'grid' (legacy).
                   Default: 'quadtree'

    Returns:
        List of DIGIPIN strings found inside the polygon.

    Raises:
        ImportError: If shapely is not installed.
        ValueError: If precision is invalid or algorithm is unknown.

    Example:
        >>> zone = [(28.63, 77.22), (28.62, 77.21), (28.62, 77.23)]
        >>> codes = polyfill(zone, precision=8)  # Uses quadtree by default
        >>> len(codes)
        156
    """
    if not SHAPELY_AVAILABLE:
        raise ImportError(
            "The 'shapely' library is required for polyfill operations. "
            "Install it with: pip install digipinpy[geo]"
        )

    # Validate algorithm choice
    if algorithm not in ("quadtree", "grid"):
        raise ValueError(
            f"Unknown algorithm '{algorithm}'. Must be 'quadtree' or 'grid'"
        )

    # Use optimized quadtree algorithm by default
    if algorithm == "quadtree":
        from .polyfill_quadtree import polyfill_quadtree

        return polyfill_quadtree(polygon, precision)

    # Legacy grid scan algorithm below
    # (kept for backwards compatibility and testing)

    # 1. Normalize Input
    if isinstance(polygon, list):
        # Swap input from (lat, lon) to (x=lon, y=lat) for Shapely
        # Shapely uses Cartesian (x, y), so we map (lon, lat)
        shell = [(lon, lat) for lat, lon in polygon]
        polygon = Polygon(shell)

    if not (1 <= precision <= 10):
        raise ValueError("Precision must be between 1 and 10")

    # 2. Get Bounding Box
    min_lon, min_lat, max_lon, max_lat = polygon.bounds

    # 3. Determine Grid Step Size
    lat_step, lon_step = get_grid_size(precision)

    # Optimize: Use prepared geometry for faster contains checks
    prepared_poly = prep(polygon)

    codes = []

    # 4. Grid Scan Algorithm
    # Start from bottom-left, move to top-right
    current_lat = min_lat + (lat_step / 2)

    while current_lat < max_lat:
        current_lon = min_lon + (lon_step / 2)
        while current_lon < max_lon:
            # Check if point is inside
            if prepared_poly.contains(Point(current_lon, current_lat)):
                # Encode this center point
                # Note: encode expects (lat, lon)
                try:
                    code = encode(current_lat, current_lon, precision=precision)
                    codes.append(code)
                except ValueError:
                    pass  # Skip points outside India bounds

            current_lon += lon_step
        current_lat += lat_step

    return codes


def get_polygon_boundary(codes: List[str]) -> Tuple[float, float, float, float]:
    """
    Calculate the bounding box that encompasses a list of DIGIPIN codes.
    Useful for zooming a map to show a set of search results.

    Args:
        codes: List of DIGIPIN codes

    Returns:
        (min_lat, max_lat, min_lon, max_lon)
    """
    if not codes:
        return (0.0, 0.0, 0.0, 0.0)

    # Initialize with first code
    min_lat, max_lat, min_lon, max_lon = get_bounds(codes[0])

    for code in codes[1:]:
        c_min_lat, c_max_lat, c_min_lon, c_max_lon = get_bounds(code)

        min_lat = min(min_lat, c_min_lat)
        max_lat = max(max_lat, c_max_lat)
        min_lon = min(min_lon, c_min_lon)
        max_lon = max(max_lon, c_max_lon)

    return min_lat, max_lat, min_lon, max_lon
