"""
FastAPI Integration for DIGIPIN

This module provides Pydantic models and an APIRouter for quick API integration.

Usage:
    from fastapi import FastAPI
    from digipin.fastapi_ext import router as digipin_router

    app = FastAPI()
    app.include_router(digipin_router, prefix="/digipin")
"""

try:
    from fastapi import APIRouter, HTTPException, Query
    from pydantic import BaseModel, Field, field_validator
except ImportError:
    raise ImportError(
        "FastAPI and Pydantic are required. "
        "Install with: pip install digipinpy[fastapi]"
    )

from typing import List, Optional, Dict, Any
from .encoder import encode, batch_encode
from .decoder import decode, batch_decode, get_bounds, get_parent
from .neighbors import get_neighbors, get_disk, get_ring
from .utils import is_valid_coordinate, is_valid_digipin

# -------------------------------------------------------------------------
# Pydantic Models (Data Contracts)
# -------------------------------------------------------------------------


class Coordinate(BaseModel):
    lat: float = Field(..., ge=2.5, le=38.5, description="Latitude (North)")
    lon: float = Field(..., ge=63.5, le=99.5, description="Longitude (East)")


class DigipinRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=10, description="DIGIPIN Code")

    @field_validator("code")
    @classmethod
    def validate_code(cls, v):
        if not is_valid_digipin(v):
            raise ValueError("Invalid DIGIPIN code format")
        return v.upper()


class EncodeResponse(BaseModel):
    code: str
    precision: int


class DecodeResponse(BaseModel):
    lat: float
    lon: float
    bounds: Optional[List[float]] = None


class BatchEncodeRequest(BaseModel):
    coordinates: List[Coordinate] = Field(
        ..., description="List of coordinates to encode"
    )
    precision: int = Field(10, ge=1, le=10, description="Precision level (1-10)")


class BatchDecodeRequest(BaseModel):
    codes: List[str] = Field(..., description="List of DIGIPIN codes to decode")


class ValidateResponse(BaseModel):
    code: str
    valid: bool
    precision: Optional[int] = None
    error: Optional[str] = None


# -------------------------------------------------------------------------
# API Router
# -------------------------------------------------------------------------

router = APIRouter(tags=["DIGIPIN"])


@router.post("/encode", response_model=EncodeResponse)
async def encode_coordinate(coord: Coordinate, precision: int = Query(10, ge=1, le=10)):
    """Encode a latitude/longitude pair into a DIGIPIN code."""
    code = encode(coord.lat, coord.lon, precision=precision)
    return {"code": code, "precision": precision}


@router.get("/decode/{code}", response_model=DecodeResponse)
async def decode_code(code: str, include_bounds: bool = False):
    """Decode a DIGIPIN code back to coordinates."""
    if not is_valid_digipin(code):
        raise HTTPException(status_code=400, detail="Invalid DIGIPIN code")

    lat, lon = decode(code)
    response: Dict[str, Any] = {"lat": lat, "lon": lon}

    if include_bounds:
        response["bounds"] = list(get_bounds(code))

    return response


@router.get("/neighbors/{code}")
async def get_adjacent_cells(code: str, direction: str = "all"):
    """Get neighboring grid cells."""
    if not is_valid_digipin(code):
        raise HTTPException(status_code=400, detail="Invalid DIGIPIN code")

    try:
        neighbors = get_neighbors(code, direction=direction)
        return {"center": code, "neighbors": neighbors, "count": len(neighbors)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/disk/{code}")
async def get_search_area(
    code: str,
    radius: int = Query(1, ge=0, le=100, description="Search radius in cells"),
):
    """
    Get all cells within a specified radius (filled disk).

    Radius examples:
    - 0: Just the center cell
    - 1: 3x3 grid (9 cells)
    - 2: 5x5 grid (25 cells)
    """
    if not is_valid_digipin(code):
        raise HTTPException(status_code=400, detail="Invalid DIGIPIN code")

    try:
        cells = get_disk(code, radius=radius)
        return {
            "center": code,
            "radius": radius,
            "grid_size": f"{2*radius+1}x{2*radius+1}",
            "cells": cells,
            "count": len(cells),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/ring/{code}")
async def get_ring_cells(
    code: str, radius: int = Query(1, ge=1, le=100, description="Ring radius in cells")
):
    """
    Get all cells at exactly the specified radius (hollow ring).
    """
    if not is_valid_digipin(code):
        raise HTTPException(status_code=400, detail="Invalid DIGIPIN code")

    try:
        cells = get_ring(code, radius=radius)
        return {"center": code, "radius": radius, "cells": cells, "count": len(cells)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/parent/{code}")
async def get_parent_code(
    code: str,
    level: int = Query(..., ge=1, le=10, description="Target precision level"),
):
    """Get parent code at specified hierarchical level."""
    if not is_valid_digipin(code):
        raise HTTPException(status_code=400, detail="Invalid DIGIPIN code")

    try:
        parent = get_parent(code, level)
        return {
            "original": code,
            "parent": parent,
            "original_level": len(code),
            "parent_level": len(parent),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/batch/encode")
async def batch_encode_coordinates(request: BatchEncodeRequest):
    """Batch encode multiple coordinates to DIGIPIN codes."""
    try:
        coords = [(c.lat, c.lon) for c in request.coordinates]
        codes = batch_encode(coords, precision=request.precision)
        return {"precision": request.precision, "count": len(codes), "codes": codes}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/batch/decode")
async def batch_decode_codes(request: BatchDecodeRequest):
    """Batch decode multiple DIGIPIN codes to coordinates."""
    # Validate all codes first
    invalid_codes = [c for c in request.codes if not is_valid_digipin(c)]
    if invalid_codes:
        raise HTTPException(
            status_code=400, detail=f"Invalid DIGIPIN codes: {', '.join(invalid_codes)}"
        )

    try:
        coords = batch_decode(request.codes)
        return {
            "count": len(coords),
            "coordinates": [{"lat": lat, "lon": lon} for lat, lon in coords],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/validate/{code}", response_model=ValidateResponse)
async def validate_code(code: str, strict: bool = False):
    """
    Validate a DIGIPIN code.

    - strict=False: Accepts codes of any length (1-10)
    - strict=True: Requires exactly 10 characters
    """
    valid = is_valid_digipin(code, strict=strict)

    response = {"code": code.upper() if valid else code, "valid": valid}

    if valid:
        response["precision"] = len(code)
    else:
        errors = []
        if not code:
            errors.append("Code is empty")
        elif len(code) > 10:
            errors.append(f"Code too long ({len(code)} chars, max 10)")
        elif strict and len(code) != 10:
            errors.append(f"Strict mode requires 10 characters, got {len(code)}")
        else:
            invalid_chars = [c for c in code.upper() if c not in "23456789CFJKLMPT"]
            if invalid_chars:
                errors.append(f"Invalid characters: {', '.join(set(invalid_chars))}")

        response["error"] = "; ".join(errors)

    return response


@router.get("/bounds/{code}")
async def get_cell_bounds(code: str):
    """Get the geographic bounding box for a DIGIPIN code."""
    if not is_valid_digipin(code):
        raise HTTPException(status_code=400, detail="Invalid DIGIPIN code")

    try:
        min_lat, max_lat, min_lon, max_lon = get_bounds(code)
        return {
            "code": code.upper(),
            "bounds": {
                "min_lat": min_lat,
                "max_lat": max_lat,
                "min_lon": min_lon,
                "max_lon": max_lon,
            },
            "center": {"lat": (min_lat + max_lat) / 2, "lon": (min_lon + max_lon) / 2},
            "dimensions": {
                "lat_span": max_lat - min_lat,
                "lon_span": max_lon - min_lon,
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "digipin-api", "version": "1.0.0"}
