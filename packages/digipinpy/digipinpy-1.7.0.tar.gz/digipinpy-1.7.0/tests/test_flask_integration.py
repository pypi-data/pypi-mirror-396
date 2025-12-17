"""
Tests for Flask Integration

Tests the Flask-SQLAlchemy DigipinType and request validation decorators.
"""

import pytest

try:
    from flask import Flask, request
    from flask_sqlalchemy import SQLAlchemy
    from digipin.flask_ext import (
        DigipinType,
        validate_digipin_request,
        validate_coordinates_request,
        create_digipin_blueprint,
    )

    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    pytestmark = pytest.mark.skip(reason="Flask not installed")

from digipin import encode

if FLASK_AVAILABLE:

    @pytest.fixture
    def app():
        """Create a Flask app for testing."""
        app = Flask(__name__)
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        return app

    @pytest.fixture
    def db(app):
        """Create SQLAlchemy database."""
        db = SQLAlchemy(app)

        class Location(db.Model):  # type: ignore[name-defined]
            __tablename__ = "locations"
            id = db.Column(db.Integer, primary_key=True)
            code = db.Column(DigipinType, nullable=False)
            name = db.Column(db.String(100))

        with app.app_context():
            db.create_all()

        return db

    @pytest.fixture
    def client(app):
        """Create test client."""
        return app.test_client()

    # -------------------------------------------------------------------------
    # DigipinType Tests
    # -------------------------------------------------------------------------

    def test_digipin_type_valid_insert(app, db):
        """Test inserting valid DIGIPIN code."""
        Location = db.Model._decl_class_registry.get("Location")

        with app.app_context():
            loc = Location(code="39J49LL8T4", name="Test Location")
            db.session.add(loc)
            db.session.commit()

            # Verify it was stored uppercase
            result = Location.query.filter_by(name="Test Location").first()
            assert result is not None
            assert result.code == "39J49LL8T4"

    def test_digipin_type_lowercase_normalization(app, db):
        """Test that lowercase codes are normalized to uppercase."""
        Location = db.Model._decl_class_registry.get("Location")

        with app.app_context():
            loc = Location(code="39j49ll8t4", name="Lowercase Test")
            db.session.add(loc)
            db.session.commit()

            result = Location.query.filter_by(name="Lowercase Test").first()
            assert result.code == "39J49LL8T4"

    def test_digipin_type_invalid_code(app, db):
        """Test that invalid codes raise ValueError."""
        Location = db.Model._decl_class_registry.get("Location")

        with app.app_context():
            with pytest.raises(ValueError, match="Invalid DIGIPIN code"):
                loc = Location(code="INVALID123", name="Bad Code")
                db.session.add(loc)
                db.session.commit()

    def test_digipin_type_query_prefix(app, db):
        """Test querying by prefix (e.g., all codes in region)."""
        Location = db.Model._decl_class_registry.get("Location")

        with app.app_context():
            # Insert test data
            db.session.add(Location(code="39J49LL8T4", name="Delhi 1"))
            db.session.add(Location(code="39J49LL8T5", name="Delhi 2"))
            db.session.add(Location(code="2XXXXXXXXX", name="South India"))
            db.session.commit()

            # Query all codes starting with '39' (Delhi region)
            delhi_locations = Location.query.filter(Location.code.like("39%")).all()
            assert len(delhi_locations) == 2
            assert all(loc.code.startswith("39") for loc in delhi_locations)

    # -------------------------------------------------------------------------
    # Decorator Tests
    # -------------------------------------------------------------------------

    def test_validate_digipin_request_valid(app, client):
        """Test validation decorator with valid DIGIPIN code."""

        @app.route("/test", methods=["POST"])
        @validate_digipin_request("code")
        def test_endpoint():
            data = request.get_json()
            return {"received": data["code"]}

        response = client.post("/test", json={"code": "39J49LL8T4"})
        assert response.status_code == 200
        assert response.json["received"] == "39J49LL8T4"

    def test_validate_digipin_request_invalid(app, client):
        """Test validation decorator with invalid DIGIPIN code."""

        @app.route("/test", methods=["POST"])
        @validate_digipin_request("code")
        def test_endpoint():
            return {"ok": True}

        response = client.post("/test", json={"code": "INVALID"})
        assert response.status_code == 400
        assert "error" in response.json
        assert "Invalid DIGIPIN code" in response.json["error"]

    def test_validate_digipin_request_missing_field(app, client):
        """Test validation decorator with missing field."""

        @app.route("/test", methods=["POST"])
        @validate_digipin_request("code")
        def test_endpoint():
            return {"ok": True}

        response = client.post("/test", json={"other_field": "value"})
        assert response.status_code == 400
        assert "Missing required field" in response.json["error"]

    def test_validate_coordinates_request_valid(app, client):
        """Test coordinate validation decorator with valid coordinates."""

        @app.route("/test", methods=["POST"])
        @validate_coordinates_request("lat", "lon")
        def test_endpoint():
            data = request.get_json()
            return {"lat": data["lat"], "lon": data["lon"]}

        response = client.post("/test", json={"lat": 28.6, "lon": 77.2})
        assert response.status_code == 200
        assert response.json["lat"] == 28.6
        assert response.json["lon"] == 77.2

    def test_validate_coordinates_request_invalid_range(app, client):
        """Test coordinate validation with out-of-range values."""

        @app.route("/test", methods=["POST"])
        @validate_coordinates_request("lat", "lon")
        def test_endpoint():
            return {"ok": True}

        # Coordinates outside India
        response = client.post("/test", json={"lat": 50.0, "lon": 77.2})
        assert response.status_code == 400
        assert "Coordinates outside India" in response.json["error"]

    def test_validate_coordinates_request_non_numeric(app, client):
        """Test coordinate validation with non-numeric values."""

        @app.route("/test", methods=["POST"])
        @validate_coordinates_request("lat", "lon")
        def test_endpoint():
            return {"ok": True}

        response = client.post("/test", json={"lat": "not_a_number", "lon": 77.2})
        assert response.status_code == 400
        assert "must be numeric" in response.json["error"]

    # -------------------------------------------------------------------------
    # Blueprint Tests
    # -------------------------------------------------------------------------

    def test_blueprint_encode_endpoint(app, client):
        """Test pre-built /encode endpoint."""
        bp = create_digipin_blueprint()
        app.register_blueprint(bp)

        response = client.post(
            "/api/digipin/encode", json={"lat": 28.622788, "lon": 77.213033}
        )
        assert response.status_code == 200
        assert "code" in response.json
        assert response.json["precision"] == 10

    def test_blueprint_encode_custom_precision(app, client):
        """Test encode endpoint with custom precision."""
        bp = create_digipin_blueprint()
        app.register_blueprint(bp)

        response = client.post(
            "/api/digipin/encode",
            json={"lat": 28.622788, "lon": 77.213033, "precision": 5},
        )
        assert response.status_code == 200
        assert len(response.json["code"]) == 5
        assert response.json["precision"] == 5

    def test_blueprint_decode_endpoint(app, client):
        """Test pre-built /decode endpoint."""
        bp = create_digipin_blueprint()
        app.register_blueprint(bp)

        response = client.get("/api/digipin/decode/39J49LL8T4")
        assert response.status_code == 200
        assert "lat" in response.json
        assert "lon" in response.json
        assert response.json["code"] == "39J49LL8T4"

    def test_blueprint_decode_with_bounds(app, client):
        """Test decode endpoint with bounds."""
        bp = create_digipin_blueprint()
        app.register_blueprint(bp)

        response = client.get("/api/digipin/decode/39J49LL8T4?include_bounds=true")
        assert response.status_code == 200
        assert "bounds" in response.json
        assert "min_lat" in response.json["bounds"]

    def test_blueprint_neighbors_endpoint(app, client):
        """Test pre-built /neighbors endpoint."""
        bp = create_digipin_blueprint()
        app.register_blueprint(bp)

        response = client.get("/api/digipin/neighbors/39J49LL8T4")
        assert response.status_code == 200
        assert "neighbors" in response.json
        assert "count" in response.json
        assert isinstance(response.json["neighbors"], list)

    def test_blueprint_neighbors_direction(app, client):
        """Test neighbors endpoint with direction filter."""
        bp = create_digipin_blueprint()
        app.register_blueprint(bp)

        response = client.get("/api/digipin/neighbors/39J49LL8T4?direction=cardinal")
        assert response.status_code == 200
        # Cardinal directions should return 4 neighbors
        assert response.json["count"] <= 4

    def test_blueprint_disk_endpoint(app, client):
        """Test pre-built /disk endpoint."""
        bp = create_digipin_blueprint()
        app.register_blueprint(bp)

        response = client.get("/api/digipin/disk/39J49LL8T4?radius=2")
        assert response.status_code == 200
        assert "cells" in response.json
        assert response.json["radius"] == 2
        assert isinstance(response.json["cells"], list)

    def test_blueprint_validate_endpoint(app, client):
        """Test pre-built /validate endpoint."""
        bp = create_digipin_blueprint()
        app.register_blueprint(bp)

        # Valid code
        response = client.post("/api/digipin/validate", json={"code": "39J49LL8T4"})
        assert response.status_code == 200
        assert response.json["valid"] is True

        # Invalid code
        response = client.post("/api/digipin/validate", json={"code": "INVALID"})
        assert response.status_code == 200
        assert response.json["valid"] is False

    def test_blueprint_health_endpoint(app, client):
        """Test health check endpoint."""
        bp = create_digipin_blueprint()
        app.register_blueprint(bp)

        response = client.get("/api/digipin/health")
        assert response.status_code == 200
        assert response.json["status"] == "ok"

    def test_blueprint_custom_prefix(app, client):
        """Test blueprint with custom URL prefix."""
        bp = create_digipin_blueprint(url_prefix="/custom/path")
        app.register_blueprint(bp)

        response = client.get("/custom/path/health")
        assert response.status_code == 200
