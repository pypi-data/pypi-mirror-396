"""
Visualization module for DIGIPIN codes.

Provides interactive map visualization using Folium for exploring DIGIPIN codes
and their coverage areas.
"""

from typing import List, Optional, Union, Tuple
import warnings

try:
    import folium
    from folium import plugins

    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False
    # Define placeholders to satisfy type checker
    folium = None  # type: ignore
    plugins = None  # type: ignore
    warnings.warn(
        "Folium not available. Install with: pip install digipinpy[viz]", ImportWarning
    )

from . import decode, get_bounds, is_valid


def plot_pins(
    codes: Union[str, List[str]],
    map_object: Optional["folium.Map"] = None,
    color_by_precision: bool = True,
    show_labels: bool = True,
    show_bounds: bool = True,
    zoom: Optional[int] = None,
    tiles: str = "OpenStreetMap",
    cluster: bool = False,
    max_clusters: int = 1000,
) -> "folium.Map":
    """
    Plot DIGIPIN codes on an interactive Folium map.

    Args:
        codes: Single DIGIPIN code or list of codes to visualize
        map_object: Existing folium.Map to add markers to (creates new if None)
        color_by_precision: Color-code markers by precision level
        show_labels: Show DIGIPIN code as popup label
        show_bounds: Draw bounding box rectangles for each code
        zoom: Map zoom level (auto-calculated if None)
        tiles: Map tile provider ('OpenStreetMap', 'Stamen Terrain', etc.)
        cluster: Use marker clustering for large datasets (recommended for >100 codes)
        max_clusters: Maximum number of markers to render (prevents browser freeze)

    Returns:
        folium.Map object that can be saved with .save('map.html')

    Example:
        >>> from digipin.viz import plot_pins
        >>> # Single code
        >>> m = plot_pins('39J49LL8T4')
        >>> m.save('map.html')
        >>>
        >>> # Multiple codes with clustering
        >>> codes = ['39J49LL8T4', '39J49LL8T5', '39J49LL8T6']
        >>> m = plot_pins(codes, cluster=True, show_bounds=True)
        >>> m.save('coverage.html')
    """
    if not FOLIUM_AVAILABLE:
        raise ImportError(
            "Folium is required for visualization. "
            "Install with: pip install digipinpy[viz]"
        )

    # Normalize input to list
    if isinstance(codes, str):
        codes = [codes]

    # Validate and filter codes
    valid_codes = []
    for code in codes:
        if is_valid(code):
            valid_codes.append(code.upper())
        else:
            warnings.warn(f"Invalid DIGIPIN code skipped: {code}")

    if not valid_codes:
        raise ValueError("No valid DIGIPIN codes provided")

    # Limit number of codes to prevent browser freeze
    if len(valid_codes) > max_clusters:
        warnings.warn(
            f"Too many codes ({len(valid_codes)}). "
            f"Rendering first {max_clusters} only. "
            f"Use cluster=True for large datasets."
        )
        valid_codes = valid_codes[:max_clusters]

    # Calculate center point if creating new map
    if map_object is None:
        lats, lons = [], []
        for code in valid_codes:
            lat, lon = decode(code)
            lats.append(lat)
            lons.append(lon)

        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)

        # Auto-calculate zoom based on spread
        if zoom is None:
            lat_range = max(lats) - min(lats)
            lon_range = max(lons) - min(lons)
            max_range = max(lat_range, lon_range)

            # Heuristic zoom calculation
            if max_range > 5:
                zoom = 6
            elif max_range > 1:
                zoom = 9
            elif max_range > 0.1:
                zoom = 12
            elif max_range > 0.01:
                zoom = 15
            else:
                zoom = 17

        map_object = folium.Map(
            location=[center_lat, center_lon], zoom_start=zoom, tiles=tiles
        )

    # Color palette by precision level
    precision_colors = {
        1: "#8B0000",  # Dark red (country ~1000km)
        2: "#DC143C",  # Crimson (state ~250km)
        3: "#FF6347",  # Tomato (region ~63km)
        4: "#FF8C00",  # Dark orange (district ~16km)
        5: "#FFA500",  # Orange (city ~4km)
        6: "#FFD700",  # Gold (area ~1km)
        7: "#9ACD32",  # Yellow-green (neighborhood ~250m)
        8: "#32CD32",  # Lime green (street ~60m)
        9: "#00FA9A",  # Medium spring green (building ~15m)
        10: "#00CED1",  # Dark turquoise (door ~4m)
    }

    # Create marker cluster if requested
    if cluster:
        marker_cluster = plugins.MarkerCluster()

    # Add markers for each code
    for code in valid_codes:
        lat, lon = decode(code)
        precision = len(code)

        # Determine color
        if color_by_precision:
            color = precision_colors.get(precision, "blue")
        else:
            color = "blue"

        # Create popup label
        if show_labels:
            popup_html = f"""
            <div style="font-family: monospace; font-size: 14px;">
                <b>DIGIPIN:</b> {code}<br>
                <b>Lat:</b> {lat:.6f}<br>
                <b>Lon:</b> {lon:.6f}<br>
                <b>Precision:</b> Level {precision}
            </div>
            """
            popup = folium.Popup(popup_html, max_width=300)
        else:
            popup = None

        # Create marker
        marker = folium.CircleMarker(
            location=[lat, lon],
            radius=8,
            popup=popup,
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.6,
            weight=2,
        )

        # Add to cluster or map
        if cluster:
            marker.add_to(marker_cluster)
        else:
            marker.add_to(map_object)

        # Add bounding box if requested
        if show_bounds:
            min_lat, max_lat, min_lon, max_lon = get_bounds(code)
            bounds = [[min_lat, min_lon], [max_lat, max_lon]]

            folium.Rectangle(
                bounds=bounds,
                color=color,
                fill=False,
                weight=1.5,
                opacity=0.4,
                popup=f"Bounds: {code}" if show_labels else None,
            ).add_to(map_object)

    # Add cluster to map
    if cluster:
        marker_cluster.add_to(map_object)

    # Add legend if color-coding by precision
    if color_by_precision:
        legend_html = """
        <div style="position: fixed; bottom: 50px; right: 50px; z-index: 1000;
                    background-color: white; padding: 10px; border: 2px solid grey;
                    border-radius: 5px; font-family: Arial; font-size: 12px;">
            <p style="margin: 0 0 5px 0; font-weight: bold;">Precision Levels</p>
        """
        for level, color in precision_colors.items():
            legend_html += f'<p style="margin: 2px;"><span style="color: {color};">⬤</span> Level {level}</p>'
        legend_html += "</div>"

        map_object.get_root().html.add_child(folium.Element(legend_html))  # type: ignore[attr-defined]

    return map_object


def plot_coverage(
    codes: List[str],
    title: str = "DIGIPIN Coverage Map",
    output_file: Optional[str] = None,
    **kwargs,
) -> "folium.Map":
    """
    Create a coverage map for a list of DIGIPIN codes (e.g., delivery zones).

    This is a convenience function that sets sensible defaults for visualizing
    coverage areas like delivery zones, service areas, or administrative regions.

    Args:
        codes: List of DIGIPIN codes representing the coverage area
        title: Title to display on the map
        output_file: If provided, saves map to this HTML file
        **kwargs: Additional arguments passed to plot_pins()

    Returns:
        folium.Map object

    Example:
        >>> from digipin import polyfill
        >>> from digipin.viz import plot_coverage
        >>>
        >>> # Define delivery zone
        >>> zone_polygon = [(28.63, 77.22), (28.62, 77.21), (28.62, 77.23)]
        >>> zone_codes = polyfill(zone_polygon, precision=8)
        >>>
        >>> # Visualize coverage
        >>> m = plot_coverage(zone_codes, title="Delivery Zone", output_file="zone.html")
    """
    if not FOLIUM_AVAILABLE:
        raise ImportError(
            "Folium is required for visualization. "
            "Install with: pip install digipinpy[viz]"
        )

    # Set defaults for coverage visualization
    defaults = {
        "show_bounds": True,
        "cluster": len(codes) > 100,
        "color_by_precision": False,
    }
    defaults.update(kwargs)

    # Create map
    m = plot_pins(codes, **defaults)  # type: ignore[arg-type]

    # Add title
    title_html = f"""
    <div style="position: fixed; top: 10px; left: 50px; z-index: 1000;
                background-color: white; padding: 10px; border: 2px solid grey;
                border-radius: 5px; font-size: 16px; font-weight: bold;">
        {title}<br>
        <span style="font-size: 12px; font-weight: normal;">
            {len(codes)} DIGIPIN codes
        </span>
    </div>
    """
    m.get_root().html.add_child(folium.Element(title_html))  # type: ignore[attr-defined]

    # Save if requested
    if output_file:
        m.save(output_file)
        print(f"Map saved to: {output_file}")

    return m


def plot_neighbors(
    center_code: str,
    include_neighbors: bool = True,
    radius: int = 1,
    output_file: Optional[str] = None,
) -> "folium.Map":
    """
    Visualize a DIGIPIN code and its neighboring cells.

    Args:
        center_code: The central DIGIPIN code
        include_neighbors: Whether to show neighboring cells
        radius: Radius of neighbors to include (1 = immediate 8 neighbors)
        output_file: If provided, saves map to this HTML file

    Returns:
        folium.Map object

    Example:
        >>> from digipin.viz import plot_neighbors
        >>> m = plot_neighbors('39J49LL8T4', radius=2)
        >>> m.save('neighbors.html')
    """
    if not FOLIUM_AVAILABLE:
        raise ImportError(
            "Folium is required for visualization. "
            "Install with: pip install digipinpy[viz]"
        )

    from . import get_disk

    codes = [center_code]

    if include_neighbors:
        codes.extend(get_disk(center_code, radius=radius))

    # Create map with center highlighted
    lat, lon = decode(center_code)
    m = folium.Map(location=[lat, lon], zoom_start=16)

    # Plot center code with different style
    folium.Marker(
        location=[lat, lon],
        popup=f"<b>Center:</b> {center_code}",
        icon=folium.Icon(color="red", icon="info-sign"),
    ).add_to(m)

    # Plot neighbors
    if include_neighbors:
        neighbor_codes = [c for c in codes if c != center_code]
        plot_pins(
            neighbor_codes,
            map_object=m,
            color_by_precision=False,
            show_bounds=True,
            show_labels=True,
        )

    # Add center bounds
    min_lat, max_lat, min_lon, max_lon = get_bounds(center_code)
    folium.Rectangle(
        bounds=[[min_lat, min_lon], [max_lat, max_lon]],
        color="red",
        fill=True,
        fillColor="red",
        fillOpacity=0.2,
        weight=3,
    ).add_to(m)

    # Save if requested
    if output_file:
        m.save(output_file)
        print(f"Map saved to: {output_file}")

    return m


__all__ = ["plot_pins", "plot_coverage", "plot_neighbors"]
