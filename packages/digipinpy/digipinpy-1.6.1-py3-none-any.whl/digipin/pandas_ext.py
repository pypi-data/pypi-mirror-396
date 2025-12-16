"""
Pandas Accessor for DIGIPIN

This module provides pandas integration for DIGIPIN operations.
Import this module to register the 'digipin' accessor on pandas DataFrames.

Usage:
    import pandas as pd
    import digipin.pandas_ext  # Registers the accessor

    df = pd.read_csv('data.csv')
    df['code'] = df.digipin.encode('lat', 'lon')

Requirements:
    - pandas>=1.3.0
    - numpy>=1.21.0

Install with:
    pip install digipinpy[pandas]
"""

import pandas as pd
from typing import Union
from .encoder import encode
from .decoder import decode, get_parent
from .utils import is_valid_digipin as is_valid
from .neighbors import get_neighbors


@pd.api.extensions.register_dataframe_accessor("digipin")
class DigipinAccessor:
    """
    Custom pandas accessor for DIGIPIN operations.

    This accessor adds a 'digipin' namespace to pandas DataFrames,
    enabling efficient vectorized-like operations for geocoding.

    Examples:
        >>> import pandas as pd
        >>> import digipin.pandas_ext
        >>> df = pd.DataFrame({'lat': [28.6, 19.0], 'lon': [77.2, 72.8]})
        >>> df['code'] = df.digipin.encode('lat', 'lon')
    """

    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    def encode(
        self,
        lat_col: Union[str, pd.Series],
        lon_col: Union[str, pd.Series],
        precision: int = 10,
    ) -> pd.Series:
        """
        Encode coordinate columns into DIGIPIN codes.

        Args:
            lat_col: Name of latitude column OR Series/list of latitudes
            lon_col: Name of longitude column OR Series/list of longitudes
            precision: Length of DIGIPIN code (1-10), default=10

        Returns:
            pd.Series: Column of DIGIPIN codes

        Examples:
            >>> df['code'] = df.digipin.encode('latitude', 'longitude')
            >>> df['code'] = df.digipin.encode('lat', 'lon', precision=8)
        """
        # Resolve inputs to iterables
        lats = self._obj[lat_col] if isinstance(lat_col, str) else lat_col
        lons = self._obj[lon_col] if isinstance(lon_col, str) else lon_col

        # Use list comprehension (faster than .apply for string operations)
        results = [
            encode(lat, lon, precision=precision) for lat, lon in zip(lats, lons)
        ]

        return pd.Series(results, index=self._obj.index, name="digipin")

    def decode(self, code_col: Union[str, pd.Series]) -> pd.DataFrame:
        """
        Decode a column of DIGIPIN codes into Latitude/Longitude columns.

        Args:
            code_col: Name of column containing DIGIPIN codes OR Series of codes

        Returns:
            pd.DataFrame: Two columns ['latitude', 'longitude']

        Examples:
            >>> coords = df.digipin.decode('digipin_code')
            >>> df[['lat', 'lon']] = df.digipin.decode('code')
        """
        codes = self._obj[code_col] if isinstance(code_col, str) else code_col

        # Use list comprehension
        results = [decode(code) for code in codes]

        return pd.DataFrame(
            results, columns=["latitude", "longitude"], index=self._obj.index
        )

    def is_valid(self, code_col: Union[str, pd.Series]) -> pd.Series:
        """
        Validate a column of DIGIPIN codes.

        Args:
            code_col: Name of column containing DIGIPIN codes OR Series of codes

        Returns:
            pd.Series: Boolean column (True for valid, False for invalid)

        Examples:
            >>> df['is_valid'] = df.digipin.is_valid('code')
            >>> valid_df = df[df.digipin.is_valid('code')]
        """
        codes = self._obj[code_col] if isinstance(code_col, str) else code_col
        return pd.Series(
            [is_valid(c) for c in codes], index=self._obj.index, dtype=bool
        )

    def get_parent(self, code_col: Union[str, pd.Series], level: int) -> pd.Series:
        """
        Get parent codes for a column (e.g., truncate to Region/City level).

        Args:
            code_col: Name of column containing DIGIPIN codes OR Series of codes
            level: Hierarchy level (1-10) to truncate to

        Returns:
            pd.Series: Parent codes at specified level

        Examples:
            >>> # Get state-level regions (level 2)
            >>> df['state'] = df.digipin.get_parent('code', level=2)
            >>> # Get city-level regions (level 4)
            >>> df['city'] = df.digipin.get_parent('code', level=4)
        """
        codes = self._obj[code_col] if isinstance(code_col, str) else code_col

        # Handle cases where code might be shorter than requested level
        results = [get_parent(c, level) if len(str(c)) > level else c for c in codes]
        return pd.Series(results, index=self._obj.index)

    def neighbors(
        self, code_col: Union[str, pd.Series], direction: str = "all"
    ) -> pd.Series:
        """
        Get adjacent neighbors for every row.

        Args:
            code_col: Name of column containing DIGIPIN codes OR Series of codes
            direction: Which neighbors to fetch
                      - 'all': 8 neighbors (default)
                      - 'cardinal': 4 neighbors (N, S, E, W)
                      - Specific: 'north', 'south', 'east', 'west',
                                 'northeast', 'northwest', 'southeast', 'southwest'

        Returns:
            pd.Series: Each cell contains a LIST of neighbor codes

        Examples:
            >>> # Get all 8 neighbors
            >>> df['neighbors'] = df.digipin.neighbors('code')
            >>> # Get only cardinal neighbors
            >>> df['cardinal'] = df.digipin.neighbors('code', direction='cardinal')
            >>> # Get neighbor count
            >>> df['neighbor_count'] = df.digipin.neighbors('code').apply(len)
        """
        codes = self._obj[code_col] if isinstance(code_col, str) else code_col
        results = [get_neighbors(c, direction=direction) for c in codes]
        return pd.Series(results, index=self._obj.index)
