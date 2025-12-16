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
from .decoder import decode, batch_decode, get_bounds
from .neighbors import get_neighbors
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
