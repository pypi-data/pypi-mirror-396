"""
Official DIGIPIN Specification Tests

Tests the implementation against the official Department of Posts specification
and verifies exact compliance with government requirements.
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from digipin import encoder, decoder, utils


class TestOfficialSpecification:
    """Test against official government specification."""

    def test_dak_bhawan_official_example(self):
        """
        TEST CASE: Dak Bhawan (India Post HQ, New Delhi)

        This is the OFFICIAL test case from Department of Posts.
        Coordinates: 28.622788°N, 77.213033°E
        Expected DIGIPIN: 39J49LL8T4

        This test MUST pass with exact match.
        """
        lat = 28.622788
        lon = 77.213033
        expected_code = "39J49LL8T4"

        # Encode
        result = encoder.encode(lat, lon)

        # CRITICAL: Must match official specification exactly
        assert result == expected_code, (
            f"Failed official Dak Bhawan test!\n"
            f"Expected: {expected_code}\n"
            f"Got:      {result}\n"
            f"This violates the official government specification!"
        )

        # Decode back
        decoded_lat, decoded_lon = decoder.decode(result)

        # Should be very close (within grid cell ~3.8m)
        lat_error = abs(decoded_lat - lat) * 111000  # degrees to meters
        lon_error = abs(decoded_lon - lon) * 111000
        total_error = (lat_error**2 + lon_error**2) ** 0.5

        assert total_error < 5.0, (
            f"Decode error too large: {total_error:.2f}m\n"
            f"Should be within ~3.8m grid cell"
        )

    def test_major_cities_encoding(self):
        """
        TEST CASE: Major Indian Cities

        Verify encoding works correctly for major cities.
        Tests both encoding and round-trip accuracy.
        """
        cities = [
            ("Bengaluru", 12.9716, 77.5946),
            ("Mumbai", 19.0760, 72.8777),
            ("Kolkata", 22.5726, 88.3639),
            ("Chennai", 13.0827, 80.2707),
        ]

        for city_name, lat, lon in cities:
            # Encode
            code = encoder.encode(lat, lon)

            # Must be 10 characters
            assert len(code) == 10, f"{city_name}: Code must be 10 chars"

            # Must use only official alphabet
            assert all(
                c in utils.DIGIPIN_ALPHABET for c in code
            ), f"{city_name}: Code contains invalid characters: {code}"

            # Round-trip test
            decoded_lat, decoded_lon = decoder.decode(code)
            lat_error = abs(decoded_lat - lat) * 111000
            lon_error = abs(decoded_lon - lon) * 111000
            total_error = (lat_error**2 + lon_error**2) ** 0.5

            assert (
                total_error < 5.0
            ), f"{city_name}: Round-trip error {total_error:.2f}m too large"


class TestEncodeDecode:
    """Test encode/decode round-trip operations."""

    def test_round_trip_precision(self):
        """Test that encode->decode returns approximately same coordinates."""
        test_cases = [
            (28.622788, 77.213033),  # Dak Bhawan
            (12.9716, 77.5946),  # Bengaluru
            (19.0760, 72.8777),  # Mumbai
            (22.5726, 88.3639),  # Kolkata
            (13.0827, 80.2707),  # Chennai
            (28.7041, 77.1025),  # Delhi
            (17.3850, 78.4867),  # Hyderabad
            (23.0225, 72.5714),  # Ahmedabad
            (26.9124, 75.7873),  # Jaipur
            (11.0168, 76.9558),  # Coimbatore
        ]

        for original_lat, original_lon in test_cases:
            # Encode
            code = encoder.encode(original_lat, original_lon)

            # Must be 10 characters
            assert len(code) == 10, f"Code must be 10 chars, got {len(code)}"

            # Must use only official alphabet
            assert all(
                c in utils.DIGIPIN_ALPHABET for c in code
            ), f"Code contains invalid characters: {code}"

            # Decode
            decoded_lat, decoded_lon = decoder.decode(code)

            # Calculate error in meters
            lat_error = abs(decoded_lat - original_lat) * 111000
            lon_error = abs(decoded_lon - original_lon) * 111000
            total_error = (lat_error**2 + lon_error**2) ** 0.5

            # Must be within ~5m (grid cell is ~3.8m)
            assert total_error < 5.0, (
                f"Round-trip error too large for {code}:\n"
                f"Original: ({original_lat}, {original_lon})\n"
                f"Decoded:  ({decoded_lat}, {decoded_lon})\n"
                f"Error:    {total_error:.2f}m"
            )

    def test_partial_precision_codes(self):
        """Test encoding with different precision levels."""
        lat, lon = 28.622788, 77.213033

        for precision in range(1, 11):
            code = encoder.encode(lat, lon, precision=precision)

            # Check length
            assert (
                len(code) == precision
            ), f"Code length {len(code)} != precision {precision}"

            # Check valid characters
            assert all(c in utils.DIGIPIN_ALPHABET for c in code)

    def test_batch_operations(self):
        """Test batch encoding and decoding."""
        coords = [
            (28.622788, 77.213033),
            (12.9716, 77.5946),
            (19.0760, 72.8777),
        ]

        # Batch encode
        codes = encoder.batch_encode(coords)
        assert len(codes) == 3
        assert codes[0] == "39J49LL8T4"  # Dak Bhawan (official test)
        # Note: Other codes verified through round-trip test below

        # Batch decode
        decoded = decoder.batch_decode(codes)
        assert len(decoded) == 3

        # Check round-trip
        for i, (original_lat, original_lon) in enumerate(coords):
            decoded_lat, decoded_lon = decoded[i]
            lat_error = abs(decoded_lat - original_lat) * 111000
            lon_error = abs(decoded_lon - original_lon) * 111000
            total_error = (lat_error**2 + lon_error**2) ** 0.5
            assert total_error < 5.0


class TestBounds:
    """Test bounding box calculations."""

    def test_get_bounds_full_precision(self):
        """Test get_bounds for 10-character codes."""
        code = "39J49LL8T4"
        min_lat, max_lat, min_lon, max_lon = decoder.get_bounds(code)

        # Bounds should be ordered correctly
        assert min_lat < max_lat
        assert min_lon < max_lon

        # Cell size should be approximately 3.8m at level 10
        lat_size = (max_lat - min_lat) * 111000  # meters
        lon_size = (max_lon - min_lon) * 111000  # meters

        # Should be close to 3.8m (allow 3-5m range)
        assert 3.0 < lat_size < 5.0, f"Lat cell size {lat_size:.2f}m out of range"
        assert 3.0 < lon_size < 5.0, f"Lon cell size {lon_size:.2f}m out of range"

    def test_get_bounds_partial_codes(self):
        """Test get_bounds for partial codes (different levels)."""
        base_code = "39J49LL8T4"

        for length in range(1, 11):
            partial = base_code[:length]
            min_lat, max_lat, min_lon, max_lon = decoder.get_bounds(partial)

            # Should always be valid bounds
            assert min_lat < max_lat
            assert min_lon < max_lon

            # Should be within India bounding box
            assert utils.LAT_MIN <= min_lat < max_lat <= utils.LAT_MAX
            assert utils.LON_MIN <= min_lon < max_lon <= utils.LON_MAX

    def test_decode_with_bounds(self):
        """Test decode_with_bounds returns correct structure."""
        code = "39J49LL8T4"
        result = decoder.decode_with_bounds(code)

        assert "code" in result
        assert "lat" in result
        assert "lon" in result
        assert "bounds" in result

        assert result["code"] == code.upper()
        assert isinstance(result["lat"], float)
        assert isinstance(result["lon"], float)
        assert isinstance(result["bounds"], tuple)
        assert len(result["bounds"]) == 4

    def test_encode_with_bounds(self):
        """Test encode_with_bounds returns correct structure."""
        lat, lon = 28.622788, 77.213033
        result = encoder.encode_with_bounds(lat, lon)

        assert "code" in result
        assert "lat" in result
        assert "lon" in result
        assert "bounds" in result

        assert result["code"] == "39J49LL8T4"
        assert result["lat"] == lat
        assert result["lon"] == lon


class TestValidation:
    """Test validation functions."""

    def test_valid_coordinates(self):
        """Test coordinate validation."""
        # Valid coordinates
        assert utils.is_valid_coordinate(28.622788, 77.213033) is True
        assert utils.is_valid_coordinate(12.9716, 77.5946) is True

        # Invalid coordinates (outside India bounding box)
        assert utils.is_valid_coordinate(0, 0) is False
        assert utils.is_valid_coordinate(50, 100) is False
        assert utils.is_valid_coordinate(-10, 70) is False

    def test_validate_coordinate_raises(self):
        """Test that validate_coordinate raises on invalid input."""
        with pytest.raises(ValueError):
            utils.validate_coordinate(0, 0)

        with pytest.raises(ValueError):
            utils.validate_coordinate(50, 100)

        with pytest.raises(ValueError):
            utils.validate_coordinate(28.0, 50.0)  # lon too low

    def test_valid_digipin_codes(self):
        """Test DIGIPIN code validation."""
        # Valid codes
        assert utils.is_valid_digipin("39J49LL8T4") is True
        assert utils.is_valid_digipin("58C4K9FF72") is True
        assert utils.is_valid_digipin("39j49ll8t4") is True  # lowercase

        # Invalid codes
        assert utils.is_valid_digipin("123") is False  # too short
        assert utils.is_valid_digipin("ABCDEFGHIJ") is False  # invalid chars
        assert utils.is_valid_digipin("39J49LL8T4X") is False  # too long
        assert utils.is_valid_digipin("") is False  # empty

    def test_validate_digipin_raises(self):
        """Test that validate_digipin raises on invalid input."""
        with pytest.raises(ValueError):
            utils.validate_digipin("123")

        with pytest.raises(ValueError):
            utils.validate_digipin("ABCDEFGHIJ")

        with pytest.raises(ValueError):
            utils.validate_digipin("39J49LL8T4X")

    def test_validate_digipin_normalizes(self):
        """Test that validate_digipin normalizes to uppercase."""
        assert utils.validate_digipin("39j49ll8t4") == "39J49LL8T4"
        assert utils.validate_digipin("58c4k9ff72") == "58C4K9FF72"


class TestHierarchy:
    """Test hierarchical operations."""

    def test_get_parent(self):
        """Test getting parent codes at different levels."""
        code = "39J49LL8T4"

        assert decoder.get_parent(code, 1) == "3"
        assert decoder.get_parent(code, 2) == "39"
        assert decoder.get_parent(code, 6) == "39J49L"
        assert decoder.get_parent(code, 9) == "39J49LL8T"

    def test_is_within(self):
        """Test hierarchical containment checking."""
        child = "39J49LL8T4"

        # Should be within all parent codes
        assert decoder.is_within(child, "3") is True
        assert decoder.is_within(child, "39") is True
        assert decoder.is_within(child, "39J") is True
        assert decoder.is_within(child, "39J49") is True
        assert decoder.is_within(child, "39J49L") is True

        # Should NOT be within different regions
        assert decoder.is_within(child, "4") is False
        assert decoder.is_within(child, "58") is False
        assert decoder.is_within(child, "39K") is False


class TestSpiralGrid:
    """Test the official spiral grid mapping."""

    def test_spiral_grid_symbols(self):
        """Test that all 16 symbols appear in grid exactly once."""
        symbols_in_grid = set()
        for row in utils.SPIRAL_GRID:
            for symbol in row:
                symbols_in_grid.add(symbol)

        # Must have exactly 16 unique symbols
        assert len(symbols_in_grid) == 16

        # Must match alphabet
        assert symbols_in_grid == set(utils.DIGIPIN_ALPHABET)

    def test_position_symbol_mapping(self):
        """Test bidirectional position-symbol mapping."""
        # Test all positions
        for row in range(4):
            for col in range(4):
                # Get symbol from position
                symbol = utils.get_symbol_from_position(row, col)

                # Reverse lookup should return same position
                reverse_row, reverse_col = utils.get_position_from_symbol(symbol)

                assert reverse_row == row
                assert reverse_col == col

    def test_official_grid_layout(self):
        """Test that grid matches official specification."""
        # Official grid from JavaScript implementation
        expected_grid = [
            ["F", "C", "9", "8"],
            ["J", "3", "2", "7"],
            ["K", "4", "5", "6"],
            ["L", "M", "P", "T"],
        ]

        assert utils.SPIRAL_GRID == expected_grid


class TestBoundaryConditions:
    """Test edge cases and boundary conditions."""

    def test_bounding_box_corners(self):
        """Test encoding at corners of bounding box."""
        corners = [
            (utils.LAT_MIN, utils.LON_MIN),  # SW corner
            (utils.LAT_MIN, utils.LON_MAX),  # SE corner
            (utils.LAT_MAX, utils.LON_MIN),  # NW corner
            (utils.LAT_MAX, utils.LON_MAX),  # NE corner
        ]

        for lat, lon in corners:
            # Should not raise
            code = encoder.encode(lat, lon)
            assert len(code) == 10

            # Should decode without error
            decoded_lat, decoded_lon = decoder.decode(code)
            assert utils.LAT_MIN <= decoded_lat <= utils.LAT_MAX
            assert utils.LON_MIN <= decoded_lon <= utils.LON_MAX

    def test_just_outside_bounds(self):
        """Test that coordinates just outside bounds raise error."""
        # Just below min
        with pytest.raises(ValueError):
            encoder.encode(utils.LAT_MIN - 0.01, 77.0)

        # Just above max
        with pytest.raises(ValueError):
            encoder.encode(utils.LAT_MAX + 0.01, 77.0)

        # Longitude out of bounds
        with pytest.raises(ValueError):
            encoder.encode(28.0, utils.LON_MIN - 0.01)

        with pytest.raises(ValueError):
            encoder.encode(28.0, utils.LON_MAX + 0.01)

    def test_center_of_bounding_box(self):
        """Test encoding at exact center of India bounding box."""
        center_lat = (utils.LAT_MIN + utils.LAT_MAX) / 2
        center_lon = (utils.LON_MIN + utils.LON_MAX) / 2

        code = encoder.encode(center_lat, center_lon)
        assert len(code) == 10

        # Decode and verify
        decoded_lat, decoded_lon = decoder.decode(code)
        lat_error = abs(decoded_lat - center_lat) * 111000
        lon_error = abs(decoded_lon - center_lon) * 111000
        total_error = (lat_error**2 + lon_error**2) ** 0.5

        assert total_error < 5.0


class TestGridSizeCalculations:
    """Test grid size and precision calculations."""

    def test_grid_size_at_each_level(self):
        """Test that grid size calculations are correct."""
        for level in range(1, 11):
            lat_size, lon_size = utils.get_grid_size(level)

            # Size should decrease with each level
            assert lat_size > 0
            assert lon_size > 0

            # At level 1: 36° / 4 = 9°
            if level == 1:
                assert abs(lat_size - 9.0) < 0.001
                assert abs(lon_size - 9.0) < 0.001

    def test_approx_distance_decreases(self):
        """Test that approximate distance decreases with level."""
        distances = [utils.get_approx_distance(i) for i in range(1, 11)]

        # Each distance should be smaller than previous
        for i in range(len(distances) - 1):
            assert distances[i] > distances[i + 1]

        # Level 10 should be approximately 3.8m
        assert 3.5 < distances[-1] < 4.5

    def test_precision_info(self):
        """Test get_precision_info returns correct structure."""
        for level in range(1, 11):
            info = utils.get_precision_info(level)

            assert info["level"] == level
            assert info["code_length"] == level
            assert "grid_size_lat_deg" in info
            assert "grid_size_lon_deg" in info
            assert "approx_distance_m" in info
            assert "total_cells" in info
            assert "description" in info


class TestConstants:
    """Test package constants."""

    def test_alphabet_length(self):
        """Test that alphabet has exactly 16 symbols."""
        assert len(utils.DIGIPIN_ALPHABET) == 16

    def test_alphabet_composition(self):
        """Test alphabet contains correct symbols."""
        # Should have 8 numbers: 2,3,4,5,6,7,8,9
        numbers = "23456789"
        # Should have 8 letters: C,F,J,K,L,M,P,T
        letters = "CFJKLMPT"

        assert utils.DIGIPIN_ALPHABET == numbers + letters

    def test_alphabet_excludes_ambiguous(self):
        """Test that alphabet excludes ambiguous characters."""
        # Should NOT contain: 0, 1, O, I, G, W, X
        forbidden = "01OIGWX"
        for char in forbidden:
            assert char not in utils.DIGIPIN_ALPHABET

    def test_bounding_box_dimensions(self):
        """Test official India bounding box dimensions."""
        assert utils.LAT_MIN == 2.5
        assert utils.LAT_MAX == 38.5
        assert utils.LON_MIN == 63.5
        assert utils.LON_MAX == 99.5

        # Should be perfect 36x36 degree square
        assert utils.LAT_SPAN == 36.0
        assert utils.LON_SPAN == 36.0

    def test_digipin_levels(self):
        """Test that DIGIPIN has 10 levels."""
        assert utils.DIGIPIN_LEVELS == 10

    def test_grid_subdivision(self):
        """Test 4x4 grid subdivision."""
        assert utils.GRID_SUBDIVISION == 4


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])
