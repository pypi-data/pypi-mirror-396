"""
Comprehensive Test Suite for Pandas Integration

Tests cover:
- DataFrame accessor registration
- Encoding coordinate columns to DIGIPIN codes
- Decoding DIGIPIN codes to coordinates
- Validation of codes in DataFrames
- Parent code retrieval (hierarchical operations)
- Neighbor discovery for DataFrame rows
- Edge cases and error handling
- Performance characteristics
"""

import pytest

# Skip all tests if pandas not available (using importorskip)
pd = pytest.importorskip("pandas")
np = pytest.importorskip("numpy")

# Try to import pandas extension
try:
    import digipin.pandas_ext

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

from digipin import encode, decode, is_valid

# Additional skip check for pandas extension
pytestmark = pytest.mark.skipif(
    not PANDAS_AVAILABLE,
    reason="pandas not installed (install with: pip install digipinpy[pandas])",
)


class TestAccessorRegistration:
    """Test that the pandas accessor is properly registered."""

    def test_accessor_is_registered(self):
        """The 'digipin' accessor should be available on DataFrames."""
        df = pd.DataFrame({"lat": [28.6], "lon": [77.2]})

        # Should have 'digipin' accessor
        assert hasattr(df, "digipin")

    def test_accessor_has_expected_methods(self):
        """Verify all expected methods are available."""
        df = pd.DataFrame({"lat": [28.6], "lon": [77.2]})

        expected_methods = ["encode", "decode", "is_valid", "get_parent", "neighbors"]

        for method in expected_methods:
            assert hasattr(df.digipin, method), f"Missing method: {method}"


class TestEncode:
    """Test encoding coordinates to DIGIPIN codes."""

    def test_basic_encoding(self):
        """Basic encoding from lat/lon columns."""
        df = pd.DataFrame({"lat": [28.622788], "lon": [77.213033]})

        df["code"] = df.digipin.encode("lat", "lon")

        # Should match official Dak Bhawan code
        assert df["code"].iloc[0] == "39J49LL8T4"

    def test_multiple_rows_encoding(self):
        """Encode multiple locations."""
        df = pd.DataFrame(
            {
                "city": ["Delhi", "Mumbai", "Bengaluru"],
                "lat": [28.622788, 19.0760, 12.9716],
                "lon": [77.213033, 72.8777, 77.5946],
            }
        )

        df["code"] = df.digipin.encode("lat", "lon")

        # Should have 3 codes
        assert len(df["code"]) == 3

        # All should be 10 characters
        assert all(len(code) == 10 for code in df["code"])

        # All should be valid
        assert all(is_valid(code) for code in df["code"])

        # Delhi should match official test case
        assert df[df["city"] == "Delhi"]["code"].iloc[0] == "39J49LL8T4"

    def test_encoding_with_precision(self):
        """Test encoding with different precision levels."""
        df = pd.DataFrame({"lat": [28.622788, 19.0760], "lon": [77.213033, 72.8777]})

        # Test different precisions
        for precision in [4, 6, 8, 10]:
            df[f"code_{precision}"] = df.digipin.encode(
                "lat", "lon", precision=precision
            )

            # All codes should have correct length
            assert all(len(code) == precision for code in df[f"code_{precision}"])

    def test_encoding_with_series_input(self):
        """Test encoding using Series instead of column names."""
        df = pd.DataFrame({"lat": [28.6, 19.0], "lon": [77.2, 72.8]})

        # Pass Series objects instead of column names
        codes = df.digipin.encode(df["lat"], df["lon"])

        assert len(codes) == 2
        assert all(is_valid(code) for code in codes)

    def test_encoding_preserves_index(self):
        """Encoded series should preserve original DataFrame index."""
        df = pd.DataFrame(
            {"lat": [28.6, 19.0, 12.9], "lon": [77.2, 72.8, 77.6]},
            index=["A", "B", "C"],
        )

        codes = df.digipin.encode("lat", "lon")

        # Index should match
        assert list(codes.index) == ["A", "B", "C"]


class TestDecode:
    """Test decoding DIGIPIN codes to coordinates."""

    def test_basic_decoding(self):
        """Basic decoding of DIGIPIN codes."""
        df = pd.DataFrame({"code": ["39J49LL8T4"]})

        coords = df.digipin.decode("code")

        # Should return DataFrame with 2 columns
        assert isinstance(coords, pd.DataFrame)
        assert list(coords.columns) == ["latitude", "longitude"]

        # Should be close to original Dak Bhawan coordinates
        assert abs(coords["latitude"].iloc[0] - 28.622788) < 0.001
        assert abs(coords["longitude"].iloc[0] - 77.213033) < 0.001

    def test_multiple_codes_decoding(self):
        """Decode multiple codes."""
        df = pd.DataFrame({"code": ["39J49LL8T4", "58C4K9FF72", "39J49LL8T5"]})

        coords = df.digipin.decode("code")

        # Should have 3 rows
        assert len(coords) == 3

        # All coordinates should be valid
        assert all(2.5 <= lat <= 38.5 for lat in coords["latitude"])
        assert all(63.5 <= lon <= 99.5 for lon in coords["longitude"])

    def test_decode_preserves_index(self):
        """Decoded DataFrame should preserve original index."""
        df = pd.DataFrame(
            {"code": ["39J49LL8T4", "58C4K9FF72"]}, index=["first", "second"]
        )

        coords = df.digipin.decode("code")

        # Index should match
        assert list(coords.index) == ["first", "second"]

    def test_encode_decode_round_trip(self):
        """Test round-trip: encode then decode."""
        original_df = pd.DataFrame(
            {"lat": [28.622788, 19.0760, 12.9716], "lon": [77.213033, 72.8777, 77.5946]}
        )

        # Encode
        original_df["code"] = original_df.digipin.encode("lat", "lon")

        # Decode
        decoded_coords = original_df.digipin.decode("code")

        # Should be very close to original (within ~5m)
        for i in range(len(original_df)):
            lat_error = (
                abs(decoded_coords["latitude"].iloc[i] - original_df["lat"].iloc[i])
                * 111000
            )
            lon_error = (
                abs(decoded_coords["longitude"].iloc[i] - original_df["lon"].iloc[i])
                * 111000
            )
            total_error = (lat_error**2 + lon_error**2) ** 0.5

            assert total_error < 5.0, f"Round-trip error too large: {total_error:.2f}m"

    def test_decode_with_series_input(self):
        """Test decoding using Series instead of column name."""
        df = pd.DataFrame({"code": ["39J49LL8T4", "58C4K9FF72"]})

        # Pass Series object
        coords = df.digipin.decode(df["code"])

        assert len(coords) == 2
        assert "latitude" in coords.columns
        assert "longitude" in coords.columns


class TestValidation:
    """Test validation of DIGIPIN codes."""

    def test_is_valid_all_valid(self):
        """Test validation with all valid codes."""
        df = pd.DataFrame({"code": ["39J49LL8T4", "58C4K9FF72", "39J49LL8T5"]})

        valid_mask = df.digipin.is_valid("code")

        # Should be a boolean Series
        assert valid_mask.dtype == bool

        # All should be valid
        assert all(valid_mask)

    def test_is_valid_mixed(self):
        """Test validation with mixed valid/invalid codes."""
        df = pd.DataFrame(
            {
                "code": [
                    "39J49LL8T4",  # valid
                    "INVALID123",  # invalid
                    "58C4K9FF72",  # valid
                    "123",  # invalid (too short)
                    "39J49LL8T4X",  # invalid (too long)
                ]
            }
        )

        valid_mask = df.digipin.is_valid("code")

        # Only first and third should be valid
        assert valid_mask.iloc[0] == True
        assert valid_mask.iloc[1] == False
        assert valid_mask.iloc[2] == True
        assert valid_mask.iloc[3] == False
        assert valid_mask.iloc[4] == False

    def test_is_valid_filtering(self):
        """Test filtering DataFrame based on validity."""
        df = pd.DataFrame(
            {
                "code": ["39J49LL8T4", "INVALID", "58C4K9FF72", "123"],
                "value": [100, 200, 300, 400],
            }
        )

        # Filter to only valid codes
        valid_df = df[df.digipin.is_valid("code")]

        # Should have 2 rows
        assert len(valid_df) == 2

        # Should be rows 0 and 2
        assert list(valid_df["value"]) == [100, 300]

    def test_is_valid_with_lowercase(self):
        """Test validation accepts lowercase codes."""
        df = pd.DataFrame({"code": ["39j49ll8t4", "39J49LL8T4"]})

        valid_mask = df.digipin.is_valid("code")

        # Both should be valid
        assert all(valid_mask)


class TestGetParent:
    """Test hierarchical parent code retrieval."""

    def test_get_parent_basic(self):
        """Basic parent code retrieval."""
        df = pd.DataFrame({"code": ["39J49LL8T4"]})

        # Get parent at level 2 (state/region level)
        df["region"] = df.digipin.get_parent("code", level=2)

        assert df["region"].iloc[0] == "39"

    def test_get_parent_multiple_levels(self):
        """Test getting parents at different levels."""
        df = pd.DataFrame({"code": ["39J49LL8T4", "58C4K9FF72"]})

        for level in [1, 2, 4, 6, 8]:
            df[f"parent_{level}"] = df.digipin.get_parent("code", level=level)

            # All parents should have correct length
            assert all(len(p) == level for p in df[f"parent_{level}"])

    def test_get_parent_grouping(self):
        """Test grouping by parent code."""
        df = pd.DataFrame(
            {
                "code": [
                    "39J49LL8T4",
                    "39J49LL8T5",
                    "39J49LL8T6",
                    "58C4K9FF72",
                    "58C4K9FF73",
                ],
                "value": [1, 2, 3, 4, 5],
            }
        )

        # Get parent at level 6
        df["parent"] = df.digipin.get_parent("code", level=6)

        # Group by parent and sum
        grouped = df.groupby("parent")["value"].sum()

        # Should have 2 groups
        assert len(grouped) == 2

        # Group '39J49L' should have sum of 1+2+3=6
        assert grouped["39J49L"] == 6


class TestNeighbors:
    """Test neighbor discovery for DataFrame rows."""

    def test_neighbors_all_directions(self):
        """Test getting all 8 neighbors."""
        df = pd.DataFrame({"code": ["39J49LL8T4", "58C4K9FF72"]})

        df["neighbors"] = df.digipin.neighbors("code", direction="all")

        # Each row should have a list of neighbors
        assert isinstance(df["neighbors"].iloc[0], list)

        # Should have up to 8 neighbors (might be fewer at boundaries)
        assert len(df["neighbors"].iloc[0]) <= 8
        assert len(df["neighbors"].iloc[1]) <= 8

        # All neighbors should be valid
        for neighbors_list in df["neighbors"]:
            for neighbor in neighbors_list:
                assert is_valid(neighbor)

    def test_neighbors_cardinal_only(self):
        """Test getting only cardinal neighbors (N, S, E, W)."""
        df = pd.DataFrame({"code": ["39J49LL8T4"]})

        df["cardinal"] = df.digipin.neighbors("code", direction="cardinal")

        # Should have up to 4 neighbors
        assert len(df["cardinal"].iloc[0]) <= 4

    def test_neighbors_count(self):
        """Test counting neighbors per row."""
        df = pd.DataFrame({"code": ["39J49LL8T4", "58C4K9FF72", "39J49LL8T5"]})

        df["neighbors"] = df.digipin.neighbors("code")
        df["neighbor_count"] = df["neighbors"].apply(len)

        # All should have some neighbors
        assert all(count > 0 for count in df["neighbor_count"])

    def test_neighbors_expansion(self):
        """Test using neighbors for search area expansion."""
        df = pd.DataFrame(
            {"warehouse": ["W1", "W2"], "code": ["39J49LL8T4", "58C4K9FF72"]}
        )

        # Get neighbors for delivery zone
        df["delivery_zone"] = df.digipin.neighbors("code")

        # Explode to create one row per neighbor
        expanded = df.explode("delivery_zone")

        # Should have more rows than original
        assert len(expanded) > len(df)


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_dataframe(self):
        """Test operations on empty DataFrame."""
        df = pd.DataFrame({"lat": [], "lon": []})

        codes = df.digipin.encode("lat", "lon")

        # Should return empty Series
        assert len(codes) == 0

    def test_nan_values_encoding(self):
        """Test encoding with NaN values."""
        df = pd.DataFrame({"lat": [28.6, np.nan, 19.0], "lon": [77.2, 72.8, 72.8]})

        # Should raise error on NaN
        with pytest.raises((ValueError, TypeError)):
            df.digipin.encode("lat", "lon")

    def test_invalid_column_name(self):
        """Test with non-existent column name."""
        df = pd.DataFrame({"lat": [28.6], "lon": [77.2]})

        # Should raise KeyError
        with pytest.raises(KeyError):
            df.digipin.encode("latitude", "longitude")  # Wrong names

    def test_mismatched_column_lengths(self):
        """Test error when using Series of different lengths."""
        # pandas will raise ValueError when creating DataFrame with mismatched lengths
        with pytest.raises(ValueError):
            df = pd.DataFrame({"lat": [28.6, 19.0], "lon": [77.2]})


class TestRealWorldWorkflows:
    """Test realistic data analysis workflows."""

    def test_delivery_route_analysis(self):
        """Simulate delivery route analysis."""
        # Create sample delivery data
        df = pd.DataFrame(
            {
                "delivery_id": ["D1", "D2", "D3", "D4"],
                "lat": [28.6, 28.61, 28.62, 19.0],
                "lon": [77.2, 77.21, 77.22, 72.8],
                "time_minutes": [15, 18, 20, 25],
            }
        )

        # Encode locations
        df["code"] = df.digipin.encode("lat", "lon", precision=8)

        # Get region codes
        df["region"] = df.digipin.get_parent("code", level=4)

        # Analyze by region
        region_stats = df.groupby("region").agg(
            {"time_minutes": "mean", "delivery_id": "count"}
        )

        assert len(region_stats) > 0

    def test_location_clustering(self):
        """Simulate clustering locations by DIGIPIN region."""
        # Generate sample data
        np.random.seed(42)
        n_points = 50

        df = pd.DataFrame(
            {
                "lat": np.random.uniform(28.5, 28.7, n_points),
                "lon": np.random.uniform(77.1, 77.3, n_points),
            }
        )

        # Encode at city level (precision 6)
        df["cluster"] = df.digipin.encode("lat", "lon", precision=6)

        # Count points per cluster
        cluster_counts = df["cluster"].value_counts()

        # Should have multiple clusters
        assert len(cluster_counts) > 1

    def test_spatial_join_simulation(self):
        """Simulate spatial join using DIGIPIN codes."""
        # Points of interest
        poi_df = pd.DataFrame(
            {
                "name": ["Restaurant", "Hospital", "School"],
                "lat": [28.6, 28.61, 19.0],
                "lon": [77.2, 77.21, 72.8],
            }
        )
        poi_df["code"] = poi_df.digipin.encode("lat", "lon", precision=8)

        # User locations
        user_df = pd.DataFrame(
            {"user_id": ["U1", "U2"], "lat": [28.605, 19.005], "lon": [77.205, 72.805]}
        )
        user_df["code"] = user_df.digipin.encode("lat", "lon", precision=8)

        # Get neighbors for users
        user_df["search_area"] = user_df.digipin.neighbors("code")

        # Explode to search each neighboring cell
        search_df = user_df.explode("search_area")

        # "Join" by matching codes (simplified spatial join)
        # In real app, would use: poi_df[poi_df['code'].isin(search_df['search_area'])]
        matches = poi_df[poi_df["code"].isin(search_df["search_area"])]

        # Verify we can perform the operation
        assert isinstance(matches, pd.DataFrame)


class TestPerformance:
    """Test performance characteristics."""

    def test_encoding_large_dataset(self):
        """Test encoding performance on larger dataset."""
        import time

        # Generate 1000 random coordinates
        np.random.seed(42)
        n = 1000

        df = pd.DataFrame(
            {
                "lat": np.random.uniform(28.0, 29.0, n),
                "lon": np.random.uniform(77.0, 78.0, n),
            }
        )

        start = time.time()
        df["code"] = df.digipin.encode("lat", "lon")
        elapsed = time.time() - start

        # Should complete in reasonable time (< 5 seconds)
        assert elapsed < 5.0, f"Encoding 1000 rows took {elapsed:.2f}s"

        # Verify all codes are valid
        assert len(df["code"]) == n
        assert all(is_valid(code) for code in df["code"])

    def test_decoding_large_dataset(self):
        """Test decoding performance."""
        import time

        # Create 500 codes
        np.random.seed(42)
        n = 500

        df = pd.DataFrame(
            {
                "lat": np.random.uniform(28.0, 29.0, n),
                "lon": np.random.uniform(77.0, 78.0, n),
            }
        )
        df["code"] = df.digipin.encode("lat", "lon")

        start = time.time()
        coords = df.digipin.decode("code")
        elapsed = time.time() - start

        # Should complete in reasonable time
        assert elapsed < 3.0, f"Decoding 500 rows took {elapsed:.2f}s"

        # Verify output
        assert len(coords) == n


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
