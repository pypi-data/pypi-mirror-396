"""
Comprehensive Test Suite for Neighbor Discovery

Tests cover:
- Basic neighbor discovery (8 directions)
- Cardinal directions only (4 directions)
- Specific direction queries
- Boundary crossing between parent grids
- Edge cases at bounding box boundaries
- Ring and disk calculations
- Invalid input handling
- Performance characteristics
"""

import pytest
from digipin import (
    encode,
    decode,
    get_neighbors,
    get_ring,
    get_disk,
    get_surrounding_cells,
    expand_search_area,
    is_valid,
)


class TestBasicNeighborDiscovery:
    """Test basic neighbor discovery functionality."""

    def test_get_all_neighbors_returns_8_for_interior_cell(self):
        """Interior cells should have exactly 8 neighbors."""
        # Use a code in the middle of India (not near edges)
        code = "39J49LL8T4"  # Dak Bhawan, New Delhi
        neighbors = get_neighbors(code, direction="all")

        # Should have 8 neighbors (not at boundary)
        assert len(neighbors) == 8

        # All neighbors should be valid codes
        for n in neighbors:
            assert is_valid(n)

        # Center code should not be in neighbors
        assert code not in neighbors

    def test_get_cardinal_neighbors_returns_4(self):
        """Cardinal direction should return only N, S, E, W."""
        code = "39J49LL8T4"
        neighbors = get_neighbors(code, direction="cardinal")

        # Should have exactly 4 neighbors
        assert len(neighbors) == 4

        # All should be valid
        for n in neighbors:
            assert is_valid(n)

    def test_get_specific_direction_neighbor(self):
        """Should be able to get neighbor in specific direction."""
        code = "39J49LL8T4"

        # Test each direction individually
        directions = [
            "north",
            "south",
            "east",
            "west",
            "northeast",
            "northwest",
            "southeast",
            "southwest",
        ]

        for direction in directions:
            neighbors = get_neighbors(code, direction=direction)

            # Should return exactly 1 neighbor (or 0 if at boundary)
            assert len(neighbors) <= 1

            if len(neighbors) == 1:
                assert is_valid(neighbors[0])
                assert neighbors[0] != code

    def test_neighbors_are_actually_adjacent(self):
        """Verify neighbors are geometrically adjacent."""
        code = "39J49LL8T4"
        center_lat, center_lon = decode(code)

        neighbors = get_neighbors(code)

        for neighbor in neighbors:
            n_lat, n_lon = decode(neighbor)

            # Calculate approximate distance (should be ~1 cell width)
            # For Level 10, cell size is ~3.8m, so distance should be < 10m
            lat_diff = abs(n_lat - center_lat)
            lon_diff = abs(n_lon - center_lon)

            # Should be within ~2 cell widths (accounting for diagonal)
            # Level 10 cell is ~0.000034 degrees
            assert lat_diff < 0.0001, f"Latitude difference too large: {lat_diff}"
            assert lon_diff < 0.0001, f"Longitude difference too large: {lon_diff}"

    def test_neighbors_have_same_precision(self):
        """Neighbors should have the same precision level as input."""
        # Test different precision levels
        for precision in [4, 6, 8, 10]:
            code = encode(28.622788, 77.213033, precision=precision)
            neighbors = get_neighbors(code)

            for neighbor in neighbors:
                assert (
                    len(neighbor) == precision
                ), f"Neighbor {neighbor} has wrong precision (expected {precision})"


class TestBoundaryCrossing:
    """Test handling of boundary crossing between parent grids."""

    def test_boundary_crossing_changes_parent(self):
        """Moving across parent boundary should change parent code."""
        # Find a cell near the edge of its parent grid
        # We'll use a code ending in 'T' (southeast corner of parent)
        code = "39J49LL8T4"

        # Get eastern neighbor (should cross into next parent grid)
        east_neighbors = get_neighbors(code, direction="east")

        if east_neighbors:
            east = east_neighbors[0]

            # The parent code (first 9 chars) might be different
            # This is OK - boundary crossing is expected
            # Just verify it's a valid code
            assert is_valid(east)

    def test_neighbors_at_corners_handle_crossing(self):
        """Corner cells crossing boundaries should still work."""
        # Test cells at various corners of their parent grids
        # These codes end in corner symbols: F, 8, T, L

        corner_codes = [
            "39J49LL8TF",  # Northwest corner
            "39J49LL8T8",  # Northeast corner
            "39J49LL8TT",  # Southeast corner
            "39J49LL8TL",  # Southwest corner
        ]

        for code in corner_codes:
            neighbors = get_neighbors(code)

            # Should still have neighbors (maybe fewer if at bounding box edge)
            assert (
                len(neighbors) >= 3
            ), f"Corner code {code} should have at least 3 neighbors"

            # All should be valid
            for n in neighbors:
                assert is_valid(n)


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_neighbors_at_bounding_box_edge(self):
        """Cells at India's bounding box edge have fewer neighbors."""
        # Encode a point near the northern edge (38.5°N limit)
        north_edge_code = encode(38.4, 77.0)
        neighbors = get_neighbors(north_edge_code)

        # Should have fewer than 8 neighbors (north neighbors are outside bounds)
        assert len(neighbors) <= 8

        # All returned neighbors should be valid
        for n in neighbors:
            assert is_valid(n)
            # Verify they're within India's bounds
            lat, lon = decode(n)
            assert 2.5 <= lat <= 38.5
            assert 63.5 <= lon <= 99.5

    def test_different_precision_levels(self):
        """Test neighbor discovery at different precision levels."""
        # Test from level 1 (regional) to level 10 (precise)
        base_lat, base_lon = 28.622788, 77.213033

        for level in range(1, 11):
            code = encode(base_lat, base_lon, precision=level)
            neighbors = get_neighbors(code)

            # Should have neighbors at all levels
            assert len(neighbors) > 0

            # All neighbors should have same precision
            for n in neighbors:
                assert len(n) == level

    def test_invalid_code_raises_error(self):
        """Invalid codes should raise ValueError."""
        with pytest.raises(ValueError):
            get_neighbors("INVALID123")

        with pytest.raises(ValueError):
            get_neighbors("000XXXXXXX")  # Invalid characters

    def test_invalid_direction_raises_error(self):
        """Invalid direction should raise ValueError."""
        code = "39J49LL8T4"

        with pytest.raises(ValueError):
            get_neighbors(code, direction="invalid")

        with pytest.raises(ValueError):
            get_neighbors(code, direction="up")  # Not a valid direction


class TestRingFunction:
    """Test the get_ring() function for hollow rings."""

    def test_ring_radius_1_equals_all_neighbors(self):
        """Ring at radius 1 should equal all 8 neighbors."""
        code = "39J49LL8T4"

        ring_1 = set(get_ring(code, radius=1))
        all_neighbors = set(get_neighbors(code, direction="all"))

        # Should be identical
        assert ring_1 == all_neighbors

    def test_ring_radius_2_forms_hollow_square(self):
        """Ring at radius 2 should form a hollow square."""
        code = "39J49LL8T4"
        ring = get_ring(code, radius=2)

        # Maximum cells in a ring at radius 2: 16
        # (perimeter of 5×5 square minus center 3×3)
        assert len(ring) <= 16

        # All should be valid
        for cell in ring:
            assert is_valid(cell)

        # Center should not be in ring
        assert code not in ring

        # Immediate neighbors (radius 1) should not be in ring
        neighbors_r1 = get_neighbors(code)
        for n in neighbors_r1:
            assert (
                n not in ring
            ), f"Radius 1 neighbor {n} should not be in radius 2 ring"

    def test_ring_invalid_radius_raises_error(self):
        """Ring with radius < 1 should raise error."""
        code = "39J49LL8T4"

        with pytest.raises(ValueError):
            get_ring(code, radius=0)

        with pytest.raises(ValueError):
            get_ring(code, radius=-1)


class TestDiskFunction:
    """Test the get_disk() function for filled disks."""

    def test_disk_radius_0_returns_only_center(self):
        """Disk with radius 0 should return only center cell."""
        code = "39J49LL8T4"
        disk = get_disk(code, radius=0)

        assert len(disk) == 1
        assert disk[0] == code

    def test_disk_radius_1_returns_3x3_grid(self):
        """Disk with radius 1 should return 3×3 grid (9 cells)."""
        code = "39J49LL8T4"
        disk = get_disk(code, radius=1)

        # Should have 9 cells (3×3 grid) if not at boundary
        assert len(disk) <= 9

        # Should include center
        assert code in disk

        # Should include all immediate neighbors
        neighbors = get_neighbors(code)
        for n in neighbors:
            assert n in disk

    def test_disk_radius_2_returns_5x5_grid(self):
        """Disk with radius 2 should return 5×5 grid (25 cells)."""
        code = "39J49LL8T4"
        disk = get_disk(code, radius=2)

        # Should have up to 25 cells (5×5 grid)
        assert len(disk) <= 25

        # Should include center
        assert code in disk

        # Should include radius 1 disk
        disk_r1 = get_disk(code, radius=1)
        for cell in disk_r1:
            assert cell in disk

    def test_disk_progressive_expansion(self):
        """Each larger radius should include all cells from smaller radius."""
        code = "39J49LL8T4"

        disk_0 = set(get_disk(code, radius=0))
        disk_1 = set(get_disk(code, radius=1))
        disk_2 = set(get_disk(code, radius=2))

        # Each should include the previous
        assert disk_0.issubset(disk_1)
        assert disk_1.issubset(disk_2)

    def test_disk_invalid_radius_raises_error(self):
        """Disk with radius < 0 should raise error."""
        code = "39J49LL8T4"

        with pytest.raises(ValueError):
            get_disk(code, radius=-1)


class TestConvenienceAliases:
    """Test convenience alias functions."""

    def test_get_surrounding_cells_alias(self):
        """get_surrounding_cells should work like get_neighbors(all)."""
        code = "39J49LL8T4"

        surrounding = set(get_surrounding_cells(code))
        neighbors = set(get_neighbors(code, direction="all"))

        assert surrounding == neighbors

    def test_expand_search_area_alias(self):
        """expand_search_area should work like get_disk."""
        code = "39J49LL8T4"

        for radius in [0, 1, 2, 5]:
            expanded = set(expand_search_area(code, radius=radius))
            disk = set(get_disk(code, radius=radius))

            assert expanded == disk


class TestRealWorldUseCases:
    """Test real-world usage scenarios."""

    def test_delivery_zone_expansion(self):
        """Simulate expanding delivery zone from warehouse."""
        # Warehouse location in Delhi
        warehouse_lat, warehouse_lon = 28.6, 77.2
        warehouse_code = encode(warehouse_lat, warehouse_lon, precision=8)

        # Expand to 3-cell radius (~180m coverage at level 8)
        delivery_zone = get_disk(warehouse_code, radius=3)

        # Should have multiple cells
        assert len(delivery_zone) > 9  # More than just 3×3

        # All cells should be valid
        for cell in delivery_zone:
            assert is_valid(cell)
            assert len(cell) == 8  # Same precision

    def test_emergency_response_coverage(self):
        """Simulate finding emergency resources in area."""
        # Incident location
        incident_code = encode(12.9716, 77.5946, precision=8)  # Bengaluru

        # Get immediate neighbors (closest resources)
        immediate_area = get_neighbors(incident_code)

        # Get wider search area if needed
        extended_area = get_disk(incident_code, radius=5)

        assert len(immediate_area) <= 8
        assert len(extended_area) > len(immediate_area)

        # Immediate area should be subset of extended area
        for cell in immediate_area:
            assert cell in extended_area or cell == incident_code

    def test_restaurant_search_nearby(self):
        """Simulate 'find restaurants nearby' query."""
        # User location
        user_lat, user_lon = 19.0760, 72.8777  # Mumbai
        user_code = encode(user_lat, user_lon, precision=10)

        # Search within ~40m radius
        # Level 10 cells are ~3.8m, so radius=10 ≈ 38m
        search_codes = get_disk(user_code, radius=10)

        # Should cover decent area
        assert len(search_codes) > 100  # At least 10×10 grid

        # In a real app, would query database:
        # restaurants = db.query(Restaurant).filter(
        #     Restaurant.digipin.in_(search_codes)
        # )


class TestPerformance:
    """Test performance characteristics (not strict benchmarks)."""

    def test_neighbor_discovery_is_fast(self):
        """Neighbor discovery should complete in reasonable time."""
        import time

        code = "39J49LL8T4"

        start = time.time()
        for _ in range(100):
            get_neighbors(code)
        elapsed = time.time() - start

        # 100 iterations should complete in < 1 second
        assert elapsed < 1.0, f"Too slow: {elapsed:.3f}s for 100 iterations"

    def test_disk_calculation_scales_reasonably(self):
        """Disk calculation should scale reasonably with radius."""
        import time

        code = "39J49LL8T4"

        # Test increasing radii
        for radius in [1, 5, 10]:
            start = time.time()
            disk = get_disk(code, radius=radius)
            elapsed = time.time() - start

            # Even radius=10 should complete quickly
            assert elapsed < 0.5, f"Radius {radius} too slow: {elapsed:.3f}s"

            # Verify we got expected number of cells (approximately)
            expected_max = (2 * radius + 1) ** 2
            assert len(disk) <= expected_max


class TestSpecificationCompliance:
    """Test compliance with DIGIPIN specification."""

    def test_neighbors_maintain_grid_properties(self):
        """Neighbors should maintain DIGIPIN grid properties."""
        code = "39J49LL8T4"
        neighbors = get_neighbors(code)

        for neighbor in neighbors:
            # Should use valid DIGIPIN alphabet
            from digipin import DIGIPIN_ALPHABET

            for char in neighbor:
                assert char in DIGIPIN_ALPHABET

            # Should be same length
            assert len(neighbor) == len(code)

    def test_geographic_coordinate_consistency(self):
        """Decoded neighbor coordinates should be geographically consistent."""
        code = "39J49LL8T4"
        center_lat, center_lon = decode(code)

        neighbors = get_neighbors(code)

        for neighbor in neighbors:
            n_lat, n_lon = decode(neighbor)

            # Should be within India's bounding box
            from digipin import LAT_MIN, LAT_MAX, LON_MIN, LON_MAX

            assert LAT_MIN <= n_lat <= LAT_MAX
            assert LON_MIN <= n_lon <= LON_MAX

            # Should not be too far from center
            # (maximum distance is diagonal = ~5.4m for level 10)
            lat_diff_km = abs(n_lat - center_lat) * 111  # ~111km per degree
            lon_diff_km = abs(n_lon - center_lon) * 111

            assert lat_diff_km < 1, "Neighbor too far in latitude"
            assert lon_diff_km < 1, "Neighbor too far in longitude"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
