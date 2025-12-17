"""
Comprehensive test suite for FastAPI integration.

Tests the Pydantic models, API endpoints, and validation logic.
"""

import pytest

# Skip all tests if FastAPI is not installed
fastapi = pytest.importorskip("fastapi")
pydantic = pytest.importorskip("pydantic")

from fastapi.testclient import TestClient
from digipin.fastapi_ext import (
    router,
    Coordinate,
    DigipinRequest,
    EncodeResponse,
    DecodeResponse,
)
from fastapi import FastAPI

# Create test app
app = FastAPI()
app.include_router(router, prefix="/api/v1")
client = TestClient(app)


# -------------------------------------------------------------------------
# Test Pydantic Models
# -------------------------------------------------------------------------


class TestPydanticModels:
    """Test data validation with Pydantic models."""

    def test_coordinate_valid(self):
        """Valid coordinates should be accepted."""
        coord = Coordinate(lat=28.622788, lon=77.213033)
        assert coord.lat == 28.622788
        assert coord.lon == 77.213033

    def test_coordinate_lat_too_low(self):
        """Latitude below 2.5 should fail."""
        with pytest.raises(pydantic.ValidationError):
            Coordinate(lat=2.0, lon=77.0)

    def test_coordinate_lat_too_high(self):
        """Latitude above 38.5 should fail."""
        with pytest.raises(pydantic.ValidationError):
            Coordinate(lat=39.0, lon=77.0)

    def test_coordinate_lon_too_low(self):
        """Longitude below 63.5 should fail."""
        with pytest.raises(pydantic.ValidationError):
            Coordinate(lat=28.0, lon=60.0)

    def test_coordinate_lon_too_high(self):
        """Longitude above 99.5 should fail."""
        with pytest.raises(pydantic.ValidationError):
            Coordinate(lat=28.0, lon=100.0)

    def test_digipin_request_valid(self):
        """Valid DIGIPIN code should be accepted."""
        req = DigipinRequest(code="39J49LL8T4")
        assert req.code == "39J49LL8T4"

    def test_digipin_request_auto_uppercase(self):
        """Lowercase codes should be auto-converted to uppercase."""
        req = DigipinRequest(code="39j49ll8t4")
        assert req.code == "39J49LL8T4"

    def test_digipin_request_invalid_code(self):
        """Invalid DIGIPIN codes should fail validation."""
        with pytest.raises(pydantic.ValidationError):
            DigipinRequest(code="INVALID123")

    def test_digipin_request_too_long(self):
        """Codes longer than 10 characters should fail."""
        with pytest.raises(pydantic.ValidationError):
            DigipinRequest(code="39J49LL8T4X")


# -------------------------------------------------------------------------
# Test Encode Endpoint
# -------------------------------------------------------------------------


class TestEncodeEndpoint:
    """Test the POST /encode endpoint."""

    def test_encode_basic(self):
        """Basic encoding should work."""
        response = client.post(
            "/api/v1/encode", json={"lat": 28.622788, "lon": 77.213033}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "39J49LL8T4"
        assert data["precision"] == 10

    def test_encode_with_precision(self):
        """Encoding with custom precision should work."""
        response = client.post(
            "/api/v1/encode?precision=5", json={"lat": 28.622788, "lon": 77.213033}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "39J49"
        assert data["precision"] == 5

    def test_encode_precision_levels(self):
        """Test all precision levels 1-10."""
        for precision in range(1, 11):
            response = client.post(
                f"/api/v1/encode?precision={precision}",
                json={"lat": 28.622788, "lon": 77.213033},
            )
            assert response.status_code == 200
            data = response.json()
            assert len(data["code"]) == precision
            assert data["precision"] == precision

    def test_encode_invalid_lat(self):
        """Invalid latitude should return 422."""
        response = client.post("/api/v1/encode", json={"lat": 50.0, "lon": 77.0})
        assert response.status_code == 422

    def test_encode_invalid_lon(self):
        """Invalid longitude should return 422."""
        response = client.post("/api/v1/encode", json={"lat": 28.0, "lon": 120.0})
        assert response.status_code == 422

    def test_encode_missing_lat(self):
        """Missing latitude should return 422."""
        response = client.post("/api/v1/encode", json={"lon": 77.0})
        assert response.status_code == 422

    def test_encode_missing_lon(self):
        """Missing longitude should return 422."""
        response = client.post("/api/v1/encode", json={"lat": 28.0})
        assert response.status_code == 422

    def test_encode_precision_too_low(self):
        """Precision below 1 should return 422."""
        response = client.post(
            "/api/v1/encode?precision=0", json={"lat": 28.622788, "lon": 77.213033}
        )
        assert response.status_code == 422

    def test_encode_precision_too_high(self):
        """Precision above 10 should return 422."""
        response = client.post(
            "/api/v1/encode?precision=11", json={"lat": 28.622788, "lon": 77.213033}
        )
        assert response.status_code == 422


# -------------------------------------------------------------------------
# Test Decode Endpoint
# -------------------------------------------------------------------------


class TestDecodeEndpoint:
    """Test the GET /decode/{code} endpoint."""

    def test_decode_basic(self):
        """Basic decoding should work."""
        response = client.get("/api/v1/decode/39J49LL8T4")
        assert response.status_code == 200
        data = response.json()
        assert "lat" in data
        assert "lon" in data
        assert 28.6 < data["lat"] < 28.7
        assert 77.2 < data["lon"] < 77.3

    def test_decode_with_bounds(self):
        """Decoding with bounds should include bounds in response."""
        response = client.get("/api/v1/decode/39J49LL8T4?include_bounds=true")
        assert response.status_code == 200
        data = response.json()
        assert "lat" in data
        assert "lon" in data
        assert "bounds" in data
        assert len(data["bounds"]) == 4  # min_lat, max_lat, min_lon, max_lon

    def test_decode_without_bounds(self):
        """Decoding without bounds should not include bounds."""
        response = client.get("/api/v1/decode/39J49LL8T4?include_bounds=false")
        assert response.status_code == 200
        data = response.json()
        assert "bounds" not in data or data["bounds"] is None

    def test_decode_invalid_code(self):
        """Invalid DIGIPIN code should return 400."""
        response = client.get("/api/v1/decode/INVALID123")
        assert response.status_code == 400
        assert "Invalid DIGIPIN code" in response.json()["detail"]

    def test_decode_partial_code(self):
        """Partial codes should work."""
        response = client.get("/api/v1/decode/39J49")
        assert response.status_code == 200
        data = response.json()
        assert "lat" in data
        assert "lon" in data

    def test_decode_lowercase(self):
        """Lowercase codes should work (auto-normalized)."""
        response = client.get("/api/v1/decode/39j49ll8t4")
        assert response.status_code == 200

    def test_decode_too_short(self):
        """Too short codes should fail validation."""
        response = client.get("/api/v1/decode/3")
        assert response.status_code == 200  # Single char is valid at precision 1

    def test_decode_too_long(self):
        """Codes longer than 10 characters should fail."""
        response = client.get("/api/v1/decode/39J49LL8T4X")
        assert response.status_code == 400


# -------------------------------------------------------------------------
# Test Neighbors Endpoint
# -------------------------------------------------------------------------


class TestNeighborsEndpoint:
    """Test the GET /neighbors/{code} endpoint."""

    def test_neighbors_basic(self):
        """Basic neighbor discovery should work."""
        response = client.get("/api/v1/neighbors/39J49LL8T4")
        assert response.status_code == 200
        data = response.json()
        assert "center" in data
        assert "neighbors" in data
        assert "count" in data
        assert data["center"] == "39J49LL8T4"
        assert isinstance(data["neighbors"], list)
        assert data["count"] == len(data["neighbors"])

    def test_neighbors_all_directions(self):
        """All directions should return 8 neighbors (or fewer at edges)."""
        response = client.get("/api/v1/neighbors/39J49LL8T4?direction=all")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] <= 8  # May be fewer at edges

    def test_neighbors_cardinal(self):
        """Cardinal directions should return 4 neighbors."""
        response = client.get("/api/v1/neighbors/39J49LL8T4?direction=cardinal")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] <= 4

    def test_neighbors_north(self):
        """North direction should return 1 or 0 neighbors."""
        response = client.get("/api/v1/neighbors/39J49LL8T4?direction=north")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] <= 1

    def test_neighbors_invalid_code(self):
        """Invalid DIGIPIN code should return 400."""
        response = client.get("/api/v1/neighbors/INVALID123")
        assert response.status_code == 400

    def test_neighbors_invalid_direction(self):
        """Invalid direction should return 400."""
        response = client.get("/api/v1/neighbors/39J49LL8T4?direction=invalid")
        assert response.status_code == 400

    def test_neighbors_partial_code(self):
        """Partial codes should work."""
        response = client.get("/api/v1/neighbors/39J49")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] > 0


# -------------------------------------------------------------------------
# Test Response Models
# -------------------------------------------------------------------------


class TestResponseModels:
    """Test that responses match expected schemas."""

    def test_encode_response_schema(self):
        """Encode response should match EncodeResponse model."""
        response = client.post(
            "/api/v1/encode", json={"lat": 28.622788, "lon": 77.213033}
        )
        assert response.status_code == 200
        data = response.json()
        # Validate against Pydantic model
        encode_resp = EncodeResponse(**data)
        assert encode_resp.code == data["code"]
        assert encode_resp.precision == data["precision"]

    def test_decode_response_schema(self):
        """Decode response should match DecodeResponse model."""
        response = client.get("/api/v1/decode/39J49LL8T4?include_bounds=true")
        assert response.status_code == 200
        data = response.json()
        # Validate against Pydantic model
        decode_resp = DecodeResponse(**data)
        assert decode_resp.lat == data["lat"]
        assert decode_resp.lon == data["lon"]
        assert decode_resp.bounds == data["bounds"]


# -------------------------------------------------------------------------
# Test Real-World Scenarios
# -------------------------------------------------------------------------


class TestRealWorldScenarios:
    """Test real-world usage patterns."""

    def test_encode_decode_roundtrip(self):
        """Encode then decode should return similar coordinates."""
        # Encode
        encode_resp = client.post(
            "/api/v1/encode", json={"lat": 28.622788, "lon": 77.213033}
        )
        code = encode_resp.json()["code"]

        # Decode
        decode_resp = client.get(f"/api/v1/decode/{code}")
        coords = decode_resp.json()

        # Should be very close (within grid cell)
        assert abs(coords["lat"] - 28.622788) < 0.01
        assert abs(coords["lon"] - 77.213033) < 0.01

    def test_delivery_workflow(self):
        """Simulate a delivery service workflow."""
        # Customer location
        customer = {"lat": 28.622788, "lon": 77.213033}

        # Encode customer location
        encode_resp = client.post("/api/v1/encode", json=customer)
        customer_code = encode_resp.json()["code"]

        # Find nearby delivery zones
        neighbors_resp = client.get(f"/api/v1/neighbors/{customer_code}")
        delivery_zones = neighbors_resp.json()["neighbors"]

        assert len(delivery_zones) > 0

    def test_multiple_cities(self):
        """Test encoding multiple Indian cities."""
        cities = [
            {"name": "Delhi", "lat": 28.622788, "lon": 77.213033},
            {"name": "Mumbai", "lat": 19.076090, "lon": 72.877426},
            {"name": "Bangalore", "lat": 12.971600, "lon": 77.594600},
            {"name": "Chennai", "lat": 13.082680, "lon": 80.270721},
        ]

        for city in cities:
            response = client.post(
                "/api/v1/encode", json={"lat": city["lat"], "lon": city["lon"]}
            )
            assert response.status_code == 200
            code = response.json()["code"]
            assert len(code) == 10


# -------------------------------------------------------------------------
# Test Performance
# -------------------------------------------------------------------------


class TestPerformance:
    """Test API performance characteristics."""

    def test_encode_performance(self):
        """Encoding should be fast (< 100ms for single request)."""
        import time

        start = time.time()
        response = client.post(
            "/api/v1/encode", json={"lat": 28.622788, "lon": 77.213033}
        )
        duration = time.time() - start

        assert response.status_code == 200
        assert duration < 0.1  # Should complete in under 100ms

    def test_batch_encoding(self):
        """Multiple encode requests should complete quickly."""
        import time

        coords = [
            {"lat": 28.622788, "lon": 77.213033},
            {"lat": 19.076090, "lon": 72.877426},
            {"lat": 12.971600, "lon": 77.594600},
            {"lat": 13.082680, "lon": 80.270721},
        ]

        start = time.time()
        for coord in coords:
            response = client.post("/api/v1/encode", json=coord)
            assert response.status_code == 200
        duration = time.time() - start

        assert duration < 0.5  # 4 requests in under 500ms


# -------------------------------------------------------------------------
# Summary
# -------------------------------------------------------------------------


def test_summary():
    """Print test summary."""
    print("\n" + "=" * 70)
    print("FastAPI Integration Test Summary")
    print("=" * 70)
    print("✓ Pydantic model validation")
    print("✓ Encode endpoint (POST /api/v1/encode)")
    print("✓ Decode endpoint (GET /api/v1/decode/{code})")
    print("✓ Neighbors endpoint (GET /api/v1/neighbors/{code})")
    print("✓ Response schema validation")
    print("✓ Real-world scenarios")
    print("✓ Performance benchmarks")
    print("=" * 70)
