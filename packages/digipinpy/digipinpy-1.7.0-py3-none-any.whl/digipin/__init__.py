"""
digipin — Official DIGIPIN Implementation for India

A Python reference implementation of the official DIGIPIN specification
published by the Department of Posts, Government of India (March 2025).

DIGIPIN is India’s national geocoding and addressing grid system,
dividing the entire geographic territory into uniform 3.8m × 3.8m cells,
each assigned a unique 10-character alphanumeric code.

Basic Usage:
    >>> from digipin import encode, decode, is_valid

    # Encode coordinates to a DIGIPIN code
    >>> code = encode(28.622788, 77.213033)  # Dak Bhawan, New Delhi
    >>> print(code)
    '39J49LL8T4'

    # Decode a DIGIPIN code back to coordinates
    >>> lat, lon = decode("39J49LL8T4")
    >>> print(f"({lat:.6f}, {lon:.6f})")
    (28.622788, 77.213033)

    # Validate a DIGIPIN code
    >>> is_valid("39J49LL8T4")
    True

Official Specification:
    Department of Posts, Ministry of Communications
    Government of India — March 2025

Project Links:
    GitHub: https://github.com/DEADSERPENT/digipin
    PyPI:   https://pypi.org/project/digipinpy

Pandas Integration (Optional):
    For data science workflows, install with pandas support:
        pip install digipinpy[pandas]

    Then import the pandas accessor:
        import digipin.pandas_ext

    This enables DataFrame operations:
        df['code'] = df.digipin.encode('lat', 'lon')

Django Integration (Optional):
    For web applications, install with Django support:
        pip install digipinpy[django]

    Then use DigipinField in your models:
        from digipin.django_ext import DigipinField
        class MyModel(models.Model):
            code = DigipinField()

FastAPI Integration (Optional):
    For high-performance APIs and microservices:
        pip install digipinpy[fastapi]

    Then mount the pre-built router:
        from fastapi import FastAPI
        from digipin.fastapi_ext import router as digipin_router
        app = FastAPI()
        app.include_router(digipin_router, prefix="/api/v1")

Visualization (Optional):
    For interactive map visualization:
        pip install digipinpy[viz]

    Then visualize DIGIPIN codes:
        from digipin.viz import plot_pins
        m = plot_pins(['39J49LL8T4', '39J49LL8T5'])
        m.save('map.html')
"""

__version__ = "1.7.0"
__author__ = "SAMARTHA H V"
__license__ = "MIT"


# Core functions
from .encoder import encode, batch_encode, encode_with_bounds
from .decoder import (
    decode,
    get_bounds,
    decode_with_bounds,
    batch_decode,
    get_parent,
    is_within,
)
from .neighbors import (
    get_neighbors,
    get_ring,
    get_disk,
    get_surrounding_cells,
    expand_search_area,
)
from .utils import (
    is_valid_digipin as is_valid,
    is_valid_coordinate,
    get_precision_info,
    get_grid_size,
    get_approx_distance,
    # Constants
    LAT_MIN,
    LAT_MAX,
    LON_MIN,
    LON_MAX,
    DIGIPIN_ALPHABET,
    DIGIPIN_LEVELS,
)

# Geospatial functions (optional - requires shapely)
try:
    from .polyfill import polyfill, get_polygon_boundary
    from .polyfill_quadtree import polyfill_quadtree
except ImportError:
    # Allow import of package even if shapely is missing
    polyfill = None  # type: ignore
    get_polygon_boundary = None  # type: ignore
    polyfill_quadtree = None  # type: ignore

# Visualization functions (optional - requires folium)
try:
    from .viz import plot_pins, plot_coverage, plot_neighbors
except ImportError:
    # Allow import of package even if folium is missing
    plot_pins = None  # type: ignore[assignment]
    plot_coverage = None  # type: ignore[assignment]
    plot_neighbors = None  # type: ignore[assignment]

# Public API
__all__ = [
    # Core functions
    "encode",
    "decode",
    "is_valid",
    # Batch operations
    "batch_encode",
    "batch_decode",
    # Hierarchical operations
    "get_bounds",
    "encode_with_bounds",
    "decode_with_bounds",
    "get_parent",
    "is_within",
    # Neighbor discovery (NEW in v1.1.0)
    "get_neighbors",
    "get_ring",
    "get_disk",
    "get_surrounding_cells",
    "expand_search_area",
    # Geospatial operations (NEW in v1.4.0)
    "polyfill",
    "polyfill_quadtree",
    "get_polygon_boundary",
    # Visualization (NEW in v1.5.0)
    "plot_pins",
    "plot_coverage",
    "plot_neighbors",
    # Utilities
    "is_valid_coordinate",
    "get_precision_info",
    "get_grid_size",
    "get_approx_distance",
    # Constants
    "LAT_MIN",
    "LAT_MAX",
    "LON_MIN",
    "LON_MAX",
    "DIGIPIN_ALPHABET",
    "DIGIPIN_LEVELS",
    # Metadata
    "__version__",
    "__author__",
    "__license__",
]
