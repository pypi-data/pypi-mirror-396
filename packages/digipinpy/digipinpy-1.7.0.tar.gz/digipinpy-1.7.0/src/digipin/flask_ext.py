"""
Flask Integration for DIGIPIN

This module provides Flask-SQLAlchemy custom types and utilities for DIGIPIN codes.
It also includes request/response validation decorators.

Usage:
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    from digipin.flask_ext import DigipinType, validate_digipin_request

    app = Flask(__name__)
    db = SQLAlchemy(app)

    class Warehouse(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        location_code = db.Column(DigipinType)

    # API endpoint with validation
    @app.route('/api/encode', methods=['POST'])
    @validate_digipin_request('lat', 'lon')
    def encode_endpoint():
        data = request.get_json()
        code = encode(data['lat'], data['lon'])
        return {'code': code}
"""

try:
    from flask import request, jsonify
    from sqlalchemy import TypeDecorator, String
    from sqlalchemy.types import UserDefinedType
except ImportError:
    raise ImportError(
        "Flask and SQLAlchemy are required. "
        "Install with: pip install digipinpy[flask]"
    )

from functools import wraps
from typing import Callable, Any, Optional
from .utils import is_valid_digipin, is_valid_coordinate
from .decoder import decode
from .encoder import encode


# -------------------------------------------------------------------------
# SQLAlchemy Custom Type
# -------------------------------------------------------------------------


class DigipinType(TypeDecorator):
    """
    SQLAlchemy custom type for DIGIPIN codes.

    Features:
    - Auto-validates DIGIPIN format on insert/update
    - Normalizes to uppercase
    - Stores as VARCHAR(10) in database
    - Compatible with Flask-SQLAlchemy

    Example:
        >>> from flask_sqlalchemy import SQLAlchemy
        >>> from digipin.flask_ext import DigipinType
        >>>
        >>> db = SQLAlchemy(app)
        >>>
        >>> class Location(db.Model):
        ...     id = db.Column(db.Integer, primary_key=True)
        ...     code = db.Column(DigipinType, nullable=False)
        ...     name = db.Column(db.String(100))
        >>>
        >>> # Usage
        >>> loc = Location(code='39J49LL8T4', name='Dak Bhawan')
        >>> db.session.add(loc)
        >>> db.session.commit()
        >>>
        >>> # Query with prefix matching
        >>> delhi_locations = Location.query.filter(
        ...     Location.code.like('39%')
        ... ).all()
    """

    impl = String
    cache_ok = True

    def __init__(self, *args, **kwargs):
        # Force length to 10 for DIGIPIN codes
        kwargs["length"] = 10
        super().__init__(*args, **kwargs)

    def process_bind_param(self, value: Optional[str], dialect) -> Optional[str]:
        """
        Process value before storing in database.
        Normalizes to uppercase and validates format.
        """
        if value is None:
            return value

        value = str(value).upper()

        # Validate DIGIPIN format
        if not is_valid_digipin(value):
            raise ValueError(
                f"Invalid DIGIPIN code: '{value}'. "
                f"Must be 1-10 characters using alphabet: 23456789CFJKLMPT"
            )

        return value

    def process_result_value(self, value: Optional[str], dialect) -> Optional[str]:
        """
        Process value when reading from database.
        Ensures uppercase normalization.
        """
        if value is None:
            return value
        return str(value).upper()


# -------------------------------------------------------------------------
# Request Validation Decorators
# -------------------------------------------------------------------------


def validate_digipin_request(*code_fields: str):
    """
    Decorator to validate DIGIPIN codes in Flask request data.

    Args:
        *code_fields: Names of fields in request JSON that should contain DIGIPIN codes

    Raises:
        400 Bad Request if validation fails

    Example:
        >>> from flask import Flask, request
        >>> from digipin.flask_ext import validate_digipin_request
        >>>
        >>> app = Flask(__name__)
        >>>
        >>> @app.route('/api/decode', methods=['POST'])
        >>> @validate_digipin_request('code')
        >>> def decode_endpoint():
        ...     data = request.get_json()
        ...     lat, lon = decode(data['code'])
        ...     return {'lat': lat, 'lon': lon}
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            data = request.get_json()

            if not data:
                return jsonify({"error": "Request body must be JSON"}), 400

            # Validate each specified field
            for field in code_fields:
                if field not in data:
                    return (
                        jsonify({"error": f"Missing required field: '{field}'"}),
                        400,
                    )

                code = data[field]
                if not is_valid_digipin(code):
                    return (
                        jsonify(
                            {
                                "error": f"Invalid DIGIPIN code in field '{field}': {code}",
                                "valid_alphabet": "23456789CFJKLMPT",
                                "valid_length": "1-10 characters",
                            }
                        ),
                        400,
                    )

                # Normalize to uppercase
                data[field] = code.upper()

            return f(*args, **kwargs)

        return wrapper

    return decorator


def validate_coordinates_request(
    lat_field: str = "lat", lon_field: str = "lon"
) -> Callable:
    """
    Decorator to validate latitude/longitude in Flask request data.

    Args:
        lat_field: Name of latitude field (default: 'lat')
        lon_field: Name of longitude field (default: 'lon')

    Raises:
        400 Bad Request if validation fails

    Example:
        >>> @app.route('/api/encode', methods=['POST'])
        >>> @validate_coordinates_request('latitude', 'longitude')
        >>> def encode_endpoint():
        ...     data = request.get_json()
        ...     code = encode(data['latitude'], data['longitude'])
        ...     return {'code': code}
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            data = request.get_json()

            if not data:
                return jsonify({"error": "Request body must be JSON"}), 400

            # Check required fields
            if lat_field not in data:
                return jsonify({"error": f"Missing required field: '{lat_field}'"}), 400
            if lon_field not in data:
                return jsonify({"error": f"Missing required field: '{lon_field}'"}), 400

            try:
                lat = float(data[lat_field])
                lon = float(data[lon_field])
            except (ValueError, TypeError):
                return (
                    jsonify({"error": "Latitude and longitude must be numeric values"}),
                    400,
                )

            # Validate coordinate range
            if not is_valid_coordinate(lat, lon):
                return (
                    jsonify(
                        {
                            "error": "Coordinates outside India's bounding box",
                            "valid_range": {
                                "latitude": "2.5 to 38.5",
                                "longitude": "63.5 to 99.5",
                            },
                            "received": {"lat": lat, "lon": lon},
                        }
                    ),
                    400,
                )

            # Store validated values back
            data[lat_field] = lat
            data[lon_field] = lon

            return f(*args, **kwargs)

        return wrapper

    return decorator


# -------------------------------------------------------------------------
# Blueprint (Pre-built REST API)
# -------------------------------------------------------------------------


def create_digipin_blueprint(url_prefix: str = "/api/digipin"):
    """
    Create a Flask Blueprint with pre-built DIGIPIN API endpoints.

    Args:
        url_prefix: URL prefix for all endpoints (default: '/api/digipin')

    Returns:
        Flask Blueprint ready to register with app.register_blueprint()

    Example:
        >>> from flask import Flask
        >>> from digipin.flask_ext import create_digipin_blueprint
        >>>
        >>> app = Flask(__name__)
        >>> digipin_bp = create_digipin_blueprint()
        >>> app.register_blueprint(digipin_bp)
        >>>
        >>> # Now these endpoints are available:
        >>> # POST /api/digipin/encode - Encode coordinates
        >>> # GET  /api/digipin/decode/<code> - Decode DIGIPIN
        >>> # GET  /api/digipin/neighbors/<code> - Get neighbors
        >>> # POST /api/digipin/validate - Validate code
    """
    from flask import Blueprint, current_app

    from .neighbors import get_neighbors, get_disk
    from .decoder import get_bounds

    bp = Blueprint("digipin", __name__, url_prefix=url_prefix)

    @bp.route("/encode", methods=["POST"])
    @validate_coordinates_request("lat", "lon")
    def encode_endpoint():
        """Encode coordinates to DIGIPIN code."""
        data = request.get_json()
        precision = int(data.get("precision", 10))

        if not (1 <= precision <= 10):
            return jsonify({"error": "Precision must be between 1 and 10"}), 400

        code = encode(data["lat"], data["lon"], precision=precision)
        return jsonify({"code": code, "precision": precision})

    @bp.route("/decode/<code>", methods=["GET"])
    def decode_endpoint(code: str):
        """Decode DIGIPIN code to coordinates."""
        if not is_valid_digipin(code):
            return (
                jsonify(
                    {
                        "error": "Invalid DIGIPIN code",
                        "valid_alphabet": "23456789CFJKLMPT",
                    }
                ),
                400,
            )

        lat, lon = decode(code)
        response = {"code": code.upper(), "lat": lat, "lon": lon}

        # Optional: Include bounds
        if request.args.get("include_bounds", "false").lower() == "true":
            bounds = get_bounds(code)
            response["bounds"] = {
                "min_lat": bounds[0],
                "max_lat": bounds[1],
                "min_lon": bounds[2],
                "max_lon": bounds[3],
            }

        return jsonify(response)

    @bp.route("/neighbors/<code>", methods=["GET"])
    def neighbors_endpoint(code: str):
        """Get neighboring cells."""
        if not is_valid_digipin(code):
            return jsonify({"error": "Invalid DIGIPIN code"}), 400

        direction = request.args.get("direction", "all")

        try:
            neighbors = get_neighbors(code, direction=direction)
            return jsonify(
                {
                    "center": code.upper(),
                    "neighbors": neighbors,
                    "count": len(neighbors),
                }
            )
        except ValueError as e:
            # Security: Log the actual error internally, return sanitized message
            current_app.logger.error(f"Neighbors endpoint error: {e}")
            return jsonify({"error": "Invalid request parameters"}), 400

    @bp.route("/disk/<code>", methods=["GET"])
    def disk_endpoint(code: str):
        """Get all cells within radius."""
        if not is_valid_digipin(code):
            return jsonify({"error": "Invalid DIGIPIN code"}), 400

        radius = int(request.args.get("radius", 1))

        if radius < 0 or radius > 100:
            return jsonify({"error": "Radius must be between 0 and 100"}), 400

        try:
            cells = get_disk(code, radius=radius)
            return jsonify(
                {
                    "center": code.upper(),
                    "radius": radius,
                    "cells": cells,
                    "count": len(cells),
                }
            )
        except ValueError as e:
            # Security: Log the actual error internally, return sanitized message
            current_app.logger.error(f"Disk endpoint error: {e}")
            return jsonify({"error": "Invalid request parameters"}), 400

    @bp.route("/validate", methods=["POST"])
    def validate_endpoint():
        """Validate DIGIPIN code format."""
        data = request.get_json()

        if not data or "code" not in data:
            return jsonify({"error": "Missing 'code' field"}), 400

        code = data["code"]
        valid = is_valid_digipin(code)

        return jsonify({"code": code, "valid": valid})

    @bp.route("/health", methods=["GET"])
    def health_endpoint():
        """Health check endpoint."""
        return jsonify({"status": "ok", "service": "digipin-api"})

    return bp


__all__ = [
    "DigipinType",
    "validate_digipin_request",
    "validate_coordinates_request",
    "create_digipin_blueprint",
]
