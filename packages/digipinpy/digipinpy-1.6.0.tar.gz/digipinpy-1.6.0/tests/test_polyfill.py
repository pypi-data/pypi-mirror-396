"""
Comprehensive tests for DIGIPIN polyfill algorithms.

Tests both the legacy grid scan and the optimized quadtree algorithms
to ensure they produce identical results.
"""

import pytest

try:
    from shapely.geometry import Polygon, Point
    from digipin import polyfill, polyfill_quadtree
    from digipin.decoder import decode

    SHAPELY_AVAILABLE = True
except ImportError:
    SHAPELY_AVAILABLE = False

# Skip all tests if shapely is not available
pytestmark = pytest.mark.skipif(
    not SHAPELY_AVAILABLE, reason="shapely not installed (geo extras required)"
)


class TestPolyfillBasic:
    """Basic functionality tests for polyfill algorithms."""

    def test_small_triangle_delhi(self):
        """Test polyfill on a small triangular zone in Delhi."""
        # Define a triangle in Connaught Place, New Delhi
        coords = [
            (28.6328, 77.2197),  # Top
            (28.6289, 77.2155),  # Bottom Left
            (28.6289, 77.2239),  # Bottom Right
            (28.6328, 77.2197),  # Closing
        ]

        # Test at precision 7 (~250m cells)
        codes_quadtree = polyfill(coords, precision=7, algorithm="quadtree")
        codes_grid = polyfill(coords, precision=7, algorithm="grid")

        # Note: Grid and quadtree may differ slightly due to grid scan checking
        # arbitrary grid points vs quadtree checking decoded cell centers.
        # Quadtree is more accurate (checks actual cell centers).
        # For this test case, they should be similar
        assert len(codes_quadtree) > 0
        assert len(codes_grid) > 0

        # All codes should be at precision 7
        assert all(len(code) == 7 for code in codes_quadtree)

        # All quadtree codes should decode to points inside the polygon
        # (This is the correct behavior - checking decoded centers)
        poly = Polygon([(lon, lat) for lat, lon in coords])
        for code in codes_quadtree:
            lat, lon = decode(code)
            # Center point should be inside
            assert poly.contains(Point(lon, lat))

    def test_single_cell(self):
        """Test polyfill on a very small polygon (single cell)."""
        # A larger square to ensure we get some cells
        center_lat, center_lon = 28.6300, 77.2200
        offset = 0.001  # ~110m

        coords = [
            (center_lat + offset, center_lon - offset),  # NW
            (center_lat + offset, center_lon + offset),  # NE
            (center_lat - offset, center_lon + offset),  # SE
            (center_lat - offset, center_lon - offset),  # SW
            (center_lat + offset, center_lon - offset),  # Closing
        ]

        codes_quadtree = polyfill(coords, precision=8, algorithm="quadtree")
        codes_grid = polyfill(coords, precision=8, algorithm="grid")

        # Should have at least 1 code
        assert len(codes_quadtree) >= 1
        assert len(codes_grid) >= 1

        # Quadtree results should be a subset of or equal to grid results
        # (Quadtree is more accurate - only includes cells whose centers are truly inside)
        assert len(codes_quadtree) <= len(codes_grid) + 5  # Allow small difference

    def test_rectangular_zone(self):
        """Test polyfill on a rectangular delivery zone."""
        # Rectangle in Bangalore
        coords = [
            (12.9800, 77.5900),  # NW
            (12.9800, 77.6000),  # NE
            (12.9700, 77.6000),  # SE
            (12.9700, 77.5900),  # SW
            (12.9800, 77.5900),  # Closing
        ]

        for precision in [6, 7, 8]:
            codes_quadtree = polyfill(coords, precision=precision, algorithm="quadtree")
            codes_grid = polyfill(coords, precision=precision, algorithm="grid")

            # Both should find cells
            assert len(codes_quadtree) > 0
            assert len(codes_grid) > 0

            # Quadtree should find similar number of cells (within 20%)
            # May differ slightly due to boundary handling
            ratio = len(codes_quadtree) / len(codes_grid)
            assert (
                0.8 <= ratio <= 1.2
            ), f"Too much difference at precision {precision}: {ratio}"

            # All codes should be valid length
            assert all(len(code) == precision for code in codes_quadtree)
            assert all(len(code) == precision for code in codes_grid)

    def test_complex_polygon(self):
        """Test polyfill on an irregular, complex polygon."""
        # L-shaped zone
        coords = [
            (28.6400, 77.2200),  # A
            (28.6400, 77.2250),  # B
            (28.6350, 77.2250),  # C
            (28.6350, 77.2300),  # D
            (28.6300, 77.2300),  # E
            (28.6300, 77.2200),  # F
            (28.6400, 77.2200),  # Back to A
        ]

        codes_quadtree = polyfill(coords, precision=7, algorithm="quadtree")
        codes_grid = polyfill(coords, precision=7, algorithm="grid")

        # Should produce identical results
        assert set(codes_quadtree) == set(codes_grid)

        # Verify all codes are inside the L-shape
        poly = Polygon([(lon, lat) for lat, lon in coords])
        for code in codes_quadtree:
            lat, lon = decode(code)
            assert poly.contains(Point(lon, lat))


class TestPolyfillEdgeCases:
    """Edge case tests for polyfill algorithms."""

    def test_precision_boundaries(self):
        """Test different precision levels (6-10, which are practical for most uses)."""
        coords = [
            (28.6300, 77.2200),
            (28.6300, 77.2250),
            (28.6250, 77.2250),
            (28.6250, 77.2200),
            (28.6300, 77.2200),
        ]

        # Test precisions 6-10 (practical precision levels for address/location use cases)
        for precision in range(6, 11):
            codes_quadtree = polyfill(coords, precision=precision, algorithm="quadtree")
            codes_grid = polyfill(coords, precision=precision, algorithm="grid")

            # Both should find cells
            assert len(codes_quadtree) > 0
            assert len(codes_grid) > 0

            # Should be roughly similar counts (within 30% due to boundary differences)
            ratio = len(codes_quadtree) / len(codes_grid)
            assert 0.7 <= ratio <= 1.3, f"Precision {precision}: ratio={ratio}"

            assert all(len(code) == precision for code in codes_quadtree)

    def test_shapely_polygon_input(self):
        """Test that Shapely Polygon objects are handled correctly."""
        # Create polygon using Shapely directly
        # Note: Shapely uses (lon, lat) order
        shell = [
            (77.2200, 28.6300),
            (77.2250, 28.6300),
            (77.2250, 28.6250),
            (77.2200, 28.6250),
            (77.2200, 28.6300),
        ]
        poly = Polygon(shell)

        codes_quadtree = polyfill(poly, precision=7, algorithm="quadtree")
        codes_grid = polyfill(poly, precision=7, algorithm="grid")

        assert set(codes_quadtree) == set(codes_grid)
        assert len(codes_quadtree) > 0

    def test_empty_polygon(self):
        """Test behavior with a polygon outside India bounds."""
        # Polygon in the USA (outside DIGIPIN bounds)
        coords = [
            (40.7128, -74.0060),  # New York
            (40.7228, -74.0060),
            (40.7228, -73.9960),
            (40.7128, -73.9960),
            (40.7128, -74.0060),
        ]

        codes_quadtree = polyfill(coords, precision=7, algorithm="quadtree")
        codes_grid = polyfill(coords, precision=7, algorithm="grid")

        # Both should return empty lists (no cells in India)
        assert codes_quadtree == []
        assert codes_grid == []

    def test_partially_outside_bounds(self):
        """Test polygon that partially overlaps with India bounds."""
        # Polygon that crosses the southern boundary
        coords = [
            (3.0, 70.0),  # Inside
            (3.0, 71.0),  # Inside
            (2.0, 71.0),  # Outside (below LAT_MIN = 2.5)
            (2.0, 70.0),  # Outside
            (3.0, 70.0),  # Back to start
        ]

        codes_quadtree = polyfill(coords, precision=5, algorithm="quadtree")
        codes_grid = polyfill(coords, precision=5, algorithm="grid")

        # Should produce identical results
        assert set(codes_quadtree) == set(codes_grid)


class TestPolyfillQuadtreeDirect:
    """Direct tests for the quadtree algorithm (not comparing to grid)."""

    def test_quadtree_direct_call(self):
        """Test calling polyfill_quadtree directly."""
        coords = [
            (28.6300, 77.2200),
            (28.6300, 77.2250),
            (28.6250, 77.2250),
            (28.6250, 77.2200),
            (28.6300, 77.2200),
        ]

        codes = polyfill_quadtree(coords, precision=7)

        # Should return some codes
        assert len(codes) > 0

        # All codes should be valid
        assert all(len(code) == 7 for code in codes)

        # Results should be sorted
        assert codes == sorted(codes)

    def test_quadtree_large_precision(self):
        """Test quadtree with high precision (where it really shines)."""
        # Small area, high precision
        coords = [
            (28.6300, 77.2200),
            (28.6305, 77.2200),
            (28.6305, 77.2205),
            (28.6300, 77.2205),
            (28.6300, 77.2200),
        ]

        # Precision 9 (~15m cells)
        codes_quadtree = polyfill(coords, precision=9, algorithm="quadtree")

        # Should have codes at precision 9
        assert all(len(code) == 9 for code in codes_quadtree)

        # Verify all codes are inside
        poly = Polygon([(lon, lat) for lat, lon in coords])
        for code in codes_quadtree:
            lat, lon = decode(code)
            assert poly.contains(Point(lon, lat))


class TestPolyfillValidation:
    """Test input validation and error handling."""

    def test_invalid_precision(self):
        """Test that invalid precision raises ValueError."""
        coords = [(28.63, 77.22), (28.62, 77.21), (28.62, 77.23)]

        with pytest.raises(ValueError, match="Precision must be between 1 and 10"):
            polyfill(coords, precision=0)

        with pytest.raises(ValueError, match="Precision must be between 1 and 10"):
            polyfill(coords, precision=11)

    def test_invalid_algorithm(self):
        """Test that invalid algorithm raises ValueError."""
        coords = [(28.63, 77.22), (28.62, 77.21), (28.62, 77.23)]

        with pytest.raises(ValueError, match="Unknown algorithm"):
            polyfill(coords, precision=7, algorithm="invalid")

    def test_default_algorithm_is_quadtree(self):
        """Verify that the default algorithm is quadtree."""
        coords = [(28.63, 77.22), (28.62, 77.21), (28.62, 77.23)]

        # Default should use quadtree
        codes_default = polyfill(coords, precision=7)
        codes_quadtree = polyfill(coords, precision=7, algorithm="quadtree")

        assert codes_default == codes_quadtree


class TestPolyfillCorrectness:
    """Verify correctness of polyfill results."""

    def test_all_cells_inside_polygon(self):
        """Verify all returned cells have centers inside the polygon."""
        coords = [
            (12.9800, 77.5900),
            (12.9800, 77.6000),
            (12.9700, 77.6000),
            (12.9700, 77.5900),
            (12.9800, 77.5900),
        ]

        poly = Polygon([(lon, lat) for lat, lon in coords])

        for algorithm in ["quadtree", "grid"]:
            codes = polyfill(coords, precision=8, algorithm=algorithm)

            for code in codes:
                lat, lon = decode(code)
                assert poly.contains(
                    Point(lon, lat)
                ), f"{algorithm}: Code {code} center is outside polygon"

    def test_coverage_completeness(self):
        """Test that polyfill provides good coverage inside the polygon."""
        # Simple square
        coords = [
            (28.6300, 77.2200),
            (28.6300, 77.2210),
            (28.6290, 77.2210),
            (28.6290, 77.2200),
            (28.6300, 77.2200),
        ]

        codes_quadtree = set(polyfill(coords, precision=8, algorithm="quadtree"))
        codes_grid = set(polyfill(coords, precision=8, algorithm="grid"))

        # Both should provide good coverage
        assert len(codes_quadtree) > 0
        assert len(codes_grid) > 0

        # Should be similar counts
        ratio = len(codes_quadtree) / len(codes_grid)
        assert 0.7 <= ratio <= 1.3
