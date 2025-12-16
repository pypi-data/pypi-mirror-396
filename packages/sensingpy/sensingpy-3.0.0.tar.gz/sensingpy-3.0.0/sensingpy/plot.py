from typing import Any, List, Tuple

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
import pyproj
from matplotlib.axes import Axes
from matplotlib.pyplot import Figure

from sensingpy.image import Image


def get_projection(crs: pyproj.CRS) -> ccrs.Projection:
    """
    Obtain cartopy projection from a CRS object for plotting.

    Parameters
    ----------
    crs : pyproj.CRS
        Custom object containing coordinate reference system data

    Returns
    -------
    ccrs.Projection
        Cartopy projection object suitable for plotting

    Raises
    ------
    ValueError
        If the CRS object is not valid or not supported

    Notes
    -----
    Currently supports UTM projections explicitly. Defaults to Mercator
    for other projection types.
    """
    if not isinstance(crs, pyproj.CRS):
        raise ValueError("Invalid CRS object. Expected a pyproj CRS object.")

    # Check if it's a UTM projection using safer methods
    try:
        # Use the coordinate_operation property to check for UTM
        if crs.coordinate_operation and "UTM" in str(crs.coordinate_operation):
            # Extract UTM zone from the CRS name or authority code
            if crs.to_authority():
                auth_name, auth_code = crs.to_authority()
                if auth_name == "EPSG":
                    # EPSG codes for UTM zones follow a pattern
                    code = int(auth_code)
                    if 32601 <= code <= 32660:  # UTM North zones
                        zone = code - 32600
                        return ccrs.UTM(zone, southern_hemisphere=False)
                    elif 32701 <= code <= 32760:  # UTM South zones
                        zone = code - 32700
                        return ccrs.UTM(zone, southern_hemisphere=True)

            # Fallback: try to extract zone from CRS name
            crs_name = str(crs)
            if "zone" in crs_name.lower():
                import re

                zone_match = re.search(r"zone (\d+)", crs_name.lower())
                if zone_match:
                    zone = int(zone_match.group(1))
                    southern = "south" in crs_name.lower()
                    return ccrs.UTM(zone, southern_hemisphere=southern)

        # Check for other common projections
        crs_name = str(crs).lower()
        if "plate carree" in crs_name or "epsg:4326" in crs_name:
            return ccrs.PlateCarree()

    except Exception:
        pass

    # Default to Mercator for unsupported projections
    return ccrs.PlateCarree()


def get_geofigure(
    crs: pyproj.CRS, nrows: int, ncols: int, figsize: tuple = (12, 6), **kwargs
) -> Tuple[Figure, Axes | List[Axes]]:
    """
    Generate matplotlib figure and axes with georeferenced projections.

    Parameters
    ----------
    crs : pyproj.CRS
        Coordinate reference system for the plot
    nrows : int
        Number of rows for the subplots
    ncols : int
        Number of columns for the subplots
    figsize : tuple, optional
        Dimensions in inches of the figure, by default (12, 6)
    **kwargs
        Additional keyword arguments passed to plt.subplots()

    Returns
    -------
    Tuple[Figure, Axes | List[Axes]]
        Figure object and either a single Axes object (if nrows=ncols=1)
        or a list of Axes objects

    Notes
    -----
    Creates a figure with axes that use the appropriate cartopy projection
    based on the provided CRS.
    """
    return plt.subplots(
        ncols=ncols,
        nrows=nrows,
        figsize=figsize,
        subplot_kw={"projection": get_projection(crs)},
        **kwargs,
    )


def plot_band(
    image: Image, band: str, ax: Axes, cmap: str = "viridis", **kwargs
) -> Tuple[Axes, Any]:
    """
    Plot a single band of an Image object.

    Parameters
    ----------
    image : Image
        Image object containing bands data and coordinate reference system
    band : str
        Band name to be plotted
    ax : Axes
        Matplotlib axes on which to plot the data
    cmap : str, optional
        Colormap to use for visualization, by default 'viridis'
    **kwargs
        Additional keyword arguments passed to ax.pcolormesh()

    Returns
    -------
    Tuple[Axes, Any]
        Axes with the plotted data and the mappable object for creating a colorbar

    Examples
    --------
    >>> fig, ax = get_geofigure(image.crs, 1, 1)
    >>> ax, mappable = plot_band(image, 'nir', ax, cmap='inferno')
    >>> plt.colorbar(mappable, ax=ax, label='NIR Reflectance')
    """
    data = image.select(band)
    transform = get_projection(image.crs)
    mappable = ax.pcolormesh(
        *image.xs_ys, data, cmap=cmap, transform=transform, **kwargs
    )
    return ax, mappable


def plot_rgb(
    image: Image,
    red: str,
    green: str,
    blue: str,
    ax: Axes,
    brightness: float = 1,
    **kwargs,
) -> Axes:
    """
    Create an RGB visualization from three bands of an Image object.

    Parameters
    ----------
    image : Image
        Image object containing bands data and coordinate reference system
    red : str
        Band name to use for the red channel
    green : str
        Band name to use for the green channel
    blue : str
        Band name to use for the blue channel
    ax : Axes
        Matplotlib axes on which to plot the RGB image
    brightness : float, optional
        Value to multiply the RGB values to adjust brightness, by default 1
    **kwargs
        Additional keyword arguments passed to ax.pcolormesh()

    Returns
    -------
    Axes
        Axes with the RGB image plotted

    Notes
    -----
    This function handles both float (0-1) and uint8 (0-255) data types.
    Values are clipped to valid range after brightness adjustment.

    Examples
    --------
    >>> fig, ax = get_geofigure(image.crs, 1, 1)
    >>> ax = plot_rgb(image, 'red', 'green', 'blue', ax, brightness=1.5)
    >>> plt.title('True Color Composite')
    """
    rgb = np.dstack(image.select([red, green, blue]))
    limit = 1 if rgb.dtype != np.uint8 else 255

    rgb = np.clip(rgb * brightness, 0, limit)
    transform = get_projection(image.crs)
    ax.pcolormesh(*image.xs_ys, rgb, transform=transform, **kwargs)
    return ax


def add_gridlines(ax: Axes, **kwargs) -> Tuple[Axes, Any]:
    """
    Add geographic gridlines to a cartopy axes.

    Parameters
    ----------
    ax : Axes
        Cartopy axes to which gridlines will be added
    **kwargs
        Additional keyword arguments passed to ax.gridlines()

    Returns
    -------
    Tuple[Axes, Any]
        Axes with added gridlines and the gridlines object for further customization

    Notes
    -----
    Labels on top and right edges are disabled by default.
    The returned gridlines object can be used for additional customization.

    Examples
    --------
    >>> fig, ax = get_geofigure(image.crs, 1, 1)
    >>> ax, gl = add_gridlines(ax, linestyle='--')
    >>> # Customize gridlines further if needed
    >>> gl.xlabel_style = {'size': 15}
    >>> gl.ylabel_style = {'color': 'gray'}
    """
    gl = ax.gridlines(draw_labels=True, **kwargs)
    gl.top_labels = gl.right_labels = False

    return ax, gl
