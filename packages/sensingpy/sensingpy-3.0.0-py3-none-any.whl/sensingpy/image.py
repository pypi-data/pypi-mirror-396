from __future__ import annotations

from copy import deepcopy
from typing import Callable, Iterable, List, Self, Tuple

import numpy as np
import pyproj
import rasterio
import rasterio.features
import xarray as xr
from affine import Affine
from rasterio.transform import from_origin, rowcol, xy
from rasterio.warp import Resampling, calculate_default_transform, reproject
from shapely.geometry import Polygon, box
from shapely.geometry.base import BaseGeometry

import sensingpy.enums as enums
import sensingpy.selector as selector


class Image(object):
    """
    A geospatial image processing class for remote sensing operations.

    This class provides tools for working with geospatial image data in Python.
    It wraps xarray Datasets with geospatial metadata and provides methods for
    common remote sensing operations including reprojection, band manipulation,
    spatial analysis, and more.

    Parameters
    ----------
    data : xr.Dataset
        xarray Dataset containing image bands and coordinates
    crs : pyproj.CRS
        Coordinate reference system of the image

    Attributes
    ----------
    data : xr.Dataset
        xarray Dataset containing image bands and coordinates
    crs : pyproj.CRS
        Coordinate reference system of the image
    name : str
        Optional name identifier for the image
    grid_mapping : str
        Name of the grid mapping variable in the Dataset

    Notes
    -----
    The Image class is designed to maintain spatial reference information throughout
    operations. Most methods support an `inplace` parameter (default True) that controls
    whether operations modify the image in-place or return a modified copy. All methods
    return self (or a copy) to enable method chaining.
    
    Examples
    --------
    >>> # In-place operations (default behavior)
    >>> image.mask(water_mask).reproject(new_crs).dropna()
    >>> 
    >>> # Non-mutating operations (create copies)
    >>> masked = image.mask(water_mask, inplace=False)
    >>> reprojected = image.reproject(new_crs, inplace=False)
    """

    grid_mapping: str = "projection"

    def __init__(self, data: xr.Dataset, crs: pyproj.CRS) -> None:
        """
        Initialize an Image object with geospatial data and coordinate reference system.

        Parameters
        ----------
        data : xr.Dataset
            The xarray Dataset containing the image data with dimensions
            and variables representing different bands/channels
        crs : pyproj.CRS
            The coordinate reference system defining the spatial reference
            of the image data
        """

        self.crs: pyproj.CRS = crs
        self.data: xr.Dataset = data
        self.name: str = ""

    def _prepare_target(self, inplace: bool) -> Image:
        """
        Helper method to handle inplace parameter.

        Parameters
        ----------
        inplace : bool
            If True, returns self for in-place modification.
            If False, returns a deep copy.

        Returns
        -------
        Image
            Self if inplace=True, otherwise a deep copy
        """
        return self if inplace else self.copy()

    def __getitem__(self, bands: str | List[str]) -> np.ndarray:
        """
        Access band(s) by name using bracket notation and return as numpy array (copy).

        Returns a numpy array copy of the specified band(s). The returned array
        is independent from the original data, so modifications will not affect
        the Image object.

        Parameters
        ----------
        bands : str or List[str]
            Band name(s) to access. Single string for one band,
            list of strings for multiple bands.

        Returns
        -------
        np.ndarray
            Copy of the band data as numpy array. For single band returns 2D array (H, W),
            for multiple bands returns 3D array (N, H, W). Modifications to this array
            will NOT affect the original Image.

        Examples
        --------
        >>> # Access single band as numpy array
        >>> blue_band = image['blue']
        >>> blue_band[mask] = 0  # Does NOT modify original image
        >>> 
        >>> # Access multiple bands
        >>> rgb = image[['red', 'green', 'blue']]
        >>> print(rgb.shape)  # (3, height, width)
        >>> 
        >>> # To modify the original image, use __setitem__ or add_band
        >>> modified_blue = image['blue'].copy()
        >>> modified_blue[mask] = 0
        >>> image['blue'] = modified_blue  # Update original
        >>> 
        >>> # Or use the data attribute directly for in-place modifications
        >>> image.data['blue'].values[mask] = 0

        See Also
        --------
        select : Equivalent method, explicitly returns numpy array copy
        __setitem__ : Set band data using bracket notation
        add_band : Add or update a band

        Notes
        -----
        This method now returns a numpy array copy (via select()) instead of an
        xarray DataArray reference. To modify the image in-place, access the
        data attribute directly: `image.data['band'].values[mask] = value`
        """
        return self.select(bands)

    def __setitem__(self, key: str, value: np.ndarray | xr.DataArray) -> None:
        """
        Set band data using bracket notation (similar to xarray/numpy).

        This method allows setting band data directly using bracket notation,
        making the API more intuitive for adding or updating bands. This operation
        always modifies the image in-place.

        Parameters
        ----------
        key : str
            Name of the band to set or update
        value : np.ndarray or xr.DataArray
            Band data. Must match the spatial dimensions (height, width) of the image.

        Examples
        --------
        >>> # Add or update a band (always in-place)
        >>> image['ndvi'] = ndvi_array
        >>> # Update existing band
        >>> image['blue'] = modified_blue_band
        >>> 
        >>> # For non-mutating operation, use add_band with inplace=False
        >>> modified = image.add_band('ndvi', ndvi_array, inplace=False)

        See Also
        --------
        add_band : Method for adding bands with inplace control
        __getitem__ : Get band data using bracket notation

        Notes
        -----
        If the band name already exists, it will be updated. Otherwise, a new band
        will be created. This method always modifies the image in-place.
        """
        self.add_band(key, value, inplace=True)

    def replace(self, old: str, new: str, inplace: bool = True) -> Image:
        """
        Replace occurrences of a substring in all band names with a new substring.

        Parameters
        ----------
        old : str
            The substring to be replaced in band names
        new : str
            The substring to replace with
        inplace : bool, optional
            If True (default), modifies the image in-place and returns self.
            If False, returns a modified copy without changing the original.

        Returns
        -------
        Self
            The modified Image object. Returns self if inplace=True,
            otherwise returns a new Image instance.

        Examples
        --------
        >>> # In-place modification (default)
        >>> image.replace('B01', 'blue')
        >>> 
        >>> # Create modified copy
        >>> renamed = image.replace('B01', 'blue', inplace=False)
        >>> # Original image unchanged
        """
        target = self._prepare_target(inplace)
        
        new_names = {
            var: var.replace(old, new) for var in target.data.data_vars if old in var
        }

        target.data = target.data.rename(new_names)
        return target

    def rename(self, new_names, inplace: bool = True) -> Image:
        """
        Rename band names using a dictionary mapping.

        Parameters
        ----------
        new_names : dict
            Dictionary mapping old band names to new band names
        inplace : bool, optional
            If True (default), modifies the image in-place and returns self.
            If False, returns a modified copy without changing the original.

        Returns
        -------
        Self
            The modified Image object. Returns self if inplace=True,
            otherwise returns a new Image instance.

        Examples
        --------
        >>> # In-place modification (default)
        >>> image.rename({'B1': 'blue', 'B2': 'green'})
        >>> 
        >>> # Create modified copy
        >>> renamed = image.rename({'B1': 'blue'}, inplace=False)
        >>> # Original image unchanged
        """
        target = self._prepare_target(inplace)
        target.data = target.data.rename(new_names)
        return target

    def rename_by_enum(self, enum: enums.Enum, inplace: bool = True) -> Image:
        """
        Rename bands using an enumeration mapping.

        Renames image bands using a mapping defined in an enumeration class.

        Parameters
        ----------
        enum : enums.Enum
            Enumeration class containing band name mappings. Each enum value
            should be a List[str] of wavelength strings that map to the enum name.
        inplace : bool, optional
            If True (default), modifies the image in-place and returns self.
            If False, returns a modified copy without changing the original.

        Returns
        -------
        Self
            The modified Image object. Returns self if inplace=True,
            otherwise returns a new Image instance.

        Examples
        --------
        >>> # In-place modification (default)
        >>> image.rename_by_enum(SENTINEL2_BANDS)
        >>> # Renames bands like '443' to 'B1', '493' to 'B2', etc.
        >>> 
        >>> # Create modified copy
        >>> renamed = image.rename_by_enum(SENTINEL2_BANDS, inplace=False)
        >>> # Original image unchanged

        See Also
        --------
        enums.SENTINEL2_BANDS : Enum for Sentinel-2 band mappings
        enums.MICASENSE_BANDS : Enum for MicaSense RedEdge band mappings
        """
        target = self._prepare_target(inplace)
        
        for band in enum:
            for wavelenght in band.value:
                target.replace(wavelenght, band.name, inplace=True)

        return target

    @property
    def band_names(self) -> List[str]:
        """
        Get list of band names in the image.

        Returns
        -------
        List[str]
            List of band names
        """

        return list(self.data.data_vars.keys())

    @property
    def width(self) -> int:
        """
        Get width of the image in pixels.

        Returns
        -------
        int
            Image width
        """

        return len(self.data.x)

    @property
    def height(self) -> int:
        """
        Get height of the image in pixels.

        Returns
        -------
        int
            Image height
        """

        return len(self.data.y)

    @property
    def count(self) -> int:
        """
        Get number of bands in the image.

        Returns
        -------
        int
            Number of bands
        """

        return len(self.data.data_vars)

    @property
    def x_res(self) -> float:
        """
        Get pixel resolution in x direction.

        Returns
        -------
        float or int
            X resolution
        """

        return float(abs(self.data.x[0] - self.data.x[1]))

    @property
    def y_res(self) -> float:
        """
        Get pixel resolution in y direction.

        Returns
        -------
        float or int
            Y resolution
        """

        return float(abs(self.data.y[0] - self.data.y[1]))

    @property
    def res(self) -> Tuple[float, float]:
        """
        Get pixel resolution in x and y directions as a tuple.

        Returns
        -------
        Tuple[float, float]
            Tuple containing (x_resolution, y_resolution) in the units
            of the image's coordinate reference system

        Examples
        --------
        >>> x_res, y_res = image.res
        >>> print(f"Resolution: {x_res} x {y_res}")
        """
        return self.x_res, self.y_res

    @property
    def transform(self) -> Affine:
        """
        Get affine transform for the image.

        Returns
        -------
        Affine
            Affine transform object representing the spatial relationship
            between pixel coordinates and CRS coordinates
        """

        return from_origin(self.left, self.top, self.x_res, self.y_res)

    @property
    def xs_ys(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get meshgrid of x and y coordinates.

        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            X and Y coordinate arrays
        """

        return np.meshgrid(self.data.x, self.data.y)

    @property
    def left(self) -> float:
        """
        Get min longitude coordinate of the image.

        Returns
        -------
        float
            Left coordinate
        """

        return float(self.data.x.min()) - abs(self.x_res / 2)

    @property
    def right(self) -> float:
        """
        Get max longitude coordinate of the image.

        Returns
        -------
        float
            Right coordinate
        """

        return float(self.data.x.max()) + abs(self.x_res / 2)

    @property
    def top(self) -> float:
        """
        Get max latitude coordinate of the image.

        Returns
        -------
        float
            Top coordinate
        """

        return float(self.data.y.max()) + abs(self.y_res / 2)

    @property
    def bottom(self) -> float:
        """
        Get min latitude coordinate of the image.

        Returns
        -------
        float
            Bottom coordinate
        """

        return float(self.data.y.min()) - abs(self.y_res / 2)

    @property
    def bbox(self) -> Polygon:
        """
        Get bounding box polygon of the image.

        Returns
        -------
        Polygon
            Shapely polygon representing image bounds
        """

        return box(self.left, self.bottom, self.right, self.top)

    @property
    def values(self) -> np.ndarray:
        """
        Get array of all band values.

        Returns
        -------
        np.ndarray
            Array containing band values
        """

        return np.array([self.data[band].values.copy() for band in self.band_names])

    @property
    def attrs(self) -> dict:
        """
        Get the attributes dictionary of the underlying xarray Dataset.

        Provides access to metadata attributes stored in the Dataset,
        such as sensor information, acquisition time, processing history,
        or custom metadata added by the user.

        Returns
        -------
        dict
            Dictionary containing all Dataset attributes

        Examples
        --------
        >>> # Access attributes
        >>> print(image.attrs)
        >>> 
        >>> # Add custom attribute
        >>> image.attrs['sensor'] = 'Sentinel-2'
        >>> image.attrs['acquisition_date'] = '2024-01-15'
        >>> 
        >>> # Check if attribute exists
        >>> if 'crs_wkt' in image.attrs:
        >>>     print(image.attrs['crs_wkt'])

        See Also
        --------
        attrs_keys : Get list of attribute keys
        attrs_values : Get list of attribute values
        """
        return self.data.attrs
    
    @property
    def attrs_keys(self) -> list:
        """
        Get list of attribute keys from the underlying xarray Dataset.

        Returns a list of all metadata attribute names stored in the Dataset.

        Returns
        -------
        list
            List of attribute key names

        Examples
        --------
        >>> # View all attribute keys
        >>> print(image.attrs_keys)
        >>> ['sensor', 'acquisition_date', 'processing_level']
        >>> 
        >>> # Iterate through attributes
        >>> for key in image.attrs_keys:
        >>>     print(f"{key}: {image.attrs[key]}")

        See Also
        --------
        attrs : Get the full attributes dictionary
        attrs_values : Get list of attribute values
        """
        return list(self.data.attrs.keys())
    
    @property
    def attrs_values(self) -> list:
        """
        Get list of attribute values from the underlying xarray Dataset.

        Returns a list of all metadata attribute values stored in the Dataset,
        in the same order as attrs_keys.

        Returns
        -------
        list
            List of attribute values

        Examples
        --------
        >>> # View all attribute values
        >>> print(image.attrs_values)
        >>> ['Sentinel-2', '2024-01-15', 'L2A']
        >>> 
        >>> # Pair keys with values
        >>> for key, value in zip(image.attrs_keys, image.attrs_values):
        >>>     print(f"{key}: {value}")

        See Also
        --------
        attrs : Get the full attributes dictionary
        attrs_keys : Get list of attribute keys
        """
        return list(self.data.attrs.values())


    def reproject(
        self, new_crs: pyproj.CRS, interpolation: Resampling = Resampling.nearest,
        inplace: bool = True
    ) -> Image:
        """
        Reproject image to new coordinate reference system.

        Parameters
        ----------
        new_crs : pyproj.CRS
            Target coordinate reference system
        interpolation : Resampling, optional
            Resampling method to use during reprojection, by default Resampling.nearest.
            Available options from rasterio.warp.Resampling include:
            - nearest: Nearest neighbor (default, preserves exact values)
            - bilinear: Bilinear interpolation (smooth, better for continuous data)
            - cubic: Cubic interpolation (smoother than bilinear)
            - cubic_spline: Cubic spline interpolation (smoothest)
            - lanczos: Lanczos windowed sinc interpolation (sharp edges)
            - average: Average of all contributing pixels
            - mode: Mode of all contributing pixels
            - max: Maximum value of all contributing pixels
            - min: Minimum value of all contributing pixels
            - med: Median of all contributing pixels
            - q1: First quartile of all contributing pixels
            - q3: Third quartile of all contributing pixels
        inplace : bool, optional
            If True (default), modifies the image in-place and returns self.
            If False, returns a modified copy without changing the original.

        Returns
        -------
        Self
            The modified Image object. Returns self if inplace=True,
            otherwise returns a new Image instance with the new CRS.

        Examples
        --------
        >>> # Reproject to UTM Zone 10N (in-place, default)
        >>> utm_crs = pyproj.CRS.from_epsg(32610)
        >>> image.reproject(utm_crs, interpolation=Resampling.bilinear)
        >>>
        >>> # Reproject to Web Mercator, keep original unchanged
        >>> webmerc_crs = pyproj.CRS.from_epsg(3857)
        >>> reprojected = image.reproject(webmerc_crs, inplace=False)
        """
        target = self._prepare_target(inplace)
        
        src_crs = target.crs
        dst_crs = new_crs

        src_height, src_width = target.height, target.width

        dst_transform, dst_width, dst_height = calculate_default_transform(
            src_crs,
            dst_crs,
            src_width,
            src_height,
            left=float(target.data.x.min()),
            bottom=float(target.data.y.min()),
            right=float(target.data.x.max()),
            top=float(target.data.y.max()),
        )

        target.data = target._Image__update_data(
            interpolation, dst_transform, dst_width, dst_height, target.crs, dst_crs
        )
        target.crs = dst_crs

        return target

    def align(
        self, reference: Image, interpolation: Resampling = Resampling.nearest,
        inplace: bool = True
    ) -> Image:
        """
        Align image to match reference image's CRS, resolution and extent.

        Transforms this image to match the coordinate reference system (CRS), spatial resolution,
        and geographic extent of a reference image.

        Parameters
        ----------
        reference : Image
            Reference image to align to. This image will be used as the
            template for CRS, resolution, and extent.
        interpolation : Resampling, optional
            Resampling method from rasterio.warp.Resampling to use
            during transformation, by default Resampling.nearest. Options include:
            - nearest: Nearest neighbor (preserves original values, best for categorical data)
            - bilinear: Bilinear interpolation (smooth, better for continuous data)
            - cubic: Cubic interpolation (smoother than bilinear)
            - lanczos: Lanczos windowed sinc interpolation (sharp edges)
        inplace : bool, optional
            If True (default), modifies the image in-place and returns self.
            If False, returns a modified copy without changing the original.

        Returns
        -------
        Self
            The modified Image object. Returns self if inplace=True,
            otherwise returns a new Image instance aligned to the reference.

        Examples
        --------
        >>> # Align a Landsat image to match a Sentinel-2 reference (in-place, default)
        >>> landsat_img.align(sentinel2_img, interpolation=Resampling.bilinear)
        >>> assert landsat_img.width == sentinel2_img.width
        >>>
        >>> # Create aligned copy, keep original unchanged
        >>> aligned = landsat_img.align(sentinel2_img, inplace=False)
        >>> assert aligned.width == sentinel2_img.width
        >>> assert landsat_img.width != sentinel2_img.width  # Original unchanged
        """
        target = self._prepare_target(inplace)
        
        if target.crs != reference.crs:
            target.reproject(reference.crs, interpolation, inplace=True)

        dst_transform = reference.transform
        dst_width, dst_height = reference.width, reference.height

        new_data_vars = {}

        for var_name, var_data in target.data.data_vars.items():
            dst_array = np.zeros((dst_height, dst_width), dtype=np.float32)
            dst_array[:] = np.nan

            dst_array, _ = reproject(
                source=var_data.values,
                destination=dst_array,
                src_transform=target.transform,
                src_crs=target.crs,
                dst_transform=dst_transform,
                dst_crs=reference.crs,
                dst_nodata=np.nan,
                resampling=interpolation,
            )

            new_data_vars[var_name] = xr.DataArray(
                data=dst_array,
                dims=("y", "x"),
                coords={"y": reference.data.y, "x": reference.data.x},
                attrs={"grid_mapping": target.grid_mapping},
            )

        target.data = xr.Dataset(
            data_vars=new_data_vars,
            coords={
                "x": reference.data.x.copy(),
                "y": reference.data.y.copy(),
                target.grid_mapping: xr.DataArray(data=0, attrs=reference.crs.to_cf()),
            },
            attrs=target.data.attrs,
        )

        target.crs = reference.crs

        return target

    def merge(self, other: Image) -> Image:
        """
        Merge two images into a new Image covering the union of their extents.

        Creates a new image that encompasses both images' geographic extents.
        If images have different sizes or extents, a new matrix is created and
        filled with data from each image at their respective positions.

        Parameters
        ----------
        other : Image
            The other image to merge with this one. Must have the same CRS and bands.

        Returns
        -------
        Image
            New merged image covering both input images

        Raises
        ------
        ValueError
            If the CRS of the two images do not match
            If the bands of the two images do not match

        Examples
        --------
        >>> # Merge two adjacent images
        >>> merged = image1.merge(image2)
        >>> print(f"Original sizes: {image1.width}x{image1.height}, {image2.width}x{image2.height}")
        >>> print(f"Merged size: {merged.width}x{merged.height}")
        """

        # Check CRS compatibility
        if self.crs != other.crs:
            raise ValueError(
                f"CRS mismatch: self.crs is {self.crs.to_string()}, "
                f"but other.crs is {other.crs.to_string()}. "
                "Images must have the same CRS to merge."
            )

        # Check bands compatibility
        if set(self.band_names).difference(set(other.band_names)) != set():
            raise ValueError("Images must have the same bands to merge.")

        left = min(self.left, other.left)
        top = max(self.top, other.top)
        right = max(self.right, other.right)
        bottom = min(self.bottom, other.bottom)

        transform = other.transform
        if self.x_res < other.x_res or self.y_res < other.y_res:
            transform = self.transform

        W = (
            abs(
                rasterio.transform.rowcol(transform, left, top)[1]
                - rasterio.transform.rowcol(transform, right, top)[1]
            )
            + 1
        )
        H = (
            abs(
                rasterio.transform.rowcol(transform, left, top)[0]
                - rasterio.transform.rowcol(transform, left, bottom)[0]
            )
            + 1
        )
        transform = Affine(
            transform.a, transform.b, left, transform.d, transform.e, top
        )

        new_x = xy(transform, np.zeros((W)), range(W))[0]
        new_y = xy(transform, range(H), np.zeros((H)))[1]

        new_data_vars = {}
        for band in self.band_names:
            data = np.zeros((H, W), dtype=np.float32)
            data[:] = np.nan

            rows, cols = rasterio.transform.rowcol(transform, *self.xs_ys)
            data[rows, cols] = self.select(band).ravel()
            rows, cols = rasterio.transform.rowcol(transform, *other.xs_ys)
            data[rows, cols] = other.select(band).ravel()

            new_data_vars[band] = xr.DataArray(
                data=data,
                dims=("y", "x"),
                coords={"y": new_y, "x": new_x},
                attrs={"grid_mapping": self.grid_mapping},
            )

        self.data = xr.Dataset(
            data_vars=new_data_vars,
            coords={
                "x": new_x.copy(),
                "y": new_y.copy(),
                self.grid_mapping: xr.DataArray(data=0, attrs=self.crs.to_cf()),
            },
            attrs=self.data.attrs,
        )

        return self

    def resample(
        self,
        scale: int,
        downscale: bool = True,
        interpolation: Resampling = Resampling.nearest,
        inplace: bool = True,
    ) -> Image:
        """
        Resample image by scaling factor to change spatial resolution.

        Changes the spatial resolution of the image by either increasing or decreasing the number
        of pixels while maintaining the same geographic extent.

        Parameters
        ----------
        scale : int
            Scale factor to apply. For example, a scale factor of 2 with downscale=True
            will reduce the image dimensions by half, while with downscale=False it will
            double the image dimensions.
        downscale : bool, optional
            Direction of scaling operation, by default True:
            - True: Reduce resolution by dividing dimensions by scale factor
            - False: Increase resolution by multiplying dimensions by scale factor
        interpolation : Resampling, optional
            Resampling method from rasterio.warp.Resampling to use, by default Resampling.nearest:
            - nearest: Nearest neighbor (preserves exact values, best for categorical data)
            - bilinear: Bilinear interpolation (smooth, better for continuous data)
            - cubic: Cubic interpolation (smoother than bilinear)
            - lanczos: Lanczos windowed sinc interpolation (preserves sharp edges)
            - average: Averages all pixels that contribute to the output pixel
        inplace : bool, optional
            If True (default), modifies the image in-place and returns self.
            If False, returns a modified copy without changing the original.

        Returns
        -------
        Self
            The modified Image object. Returns self if inplace=True,
            otherwise returns a new Image instance with the new resolution.

        Examples
        --------
        >>> # Reduce image resolution by half (in-place, default)
        >>> image.resample(scale=2, downscale=True)
        >>> print(f"New dimensions: {image.width}x{image.height}")
        >>>
        >>> # Double the image resolution, keep original unchanged
        >>> upsampled = image.resample(scale=2, downscale=False, 
        ...                            interpolation=Resampling.bilinear,
        ...                            inplace=False)
        >>> print(f"Original: {image.width}x{image.height}")
        >>> print(f"Upsampled: {upsampled.width}x{upsampled.height}")
        """
        target = self._prepare_target(inplace)
        
        if downscale:
            scale = 1 / scale

        dst_transform = target.transform * Affine.scale(1 / scale, 1 / scale)
        dst_width = int(len(target.data.x) * scale)
        dst_height = int(len(target.data.y) * scale)

        target.data = target.__update_data(
            interpolation, dst_transform, dst_width, dst_height, target.crs, target.crs
        )
        return target

    def __update_data(
        self,
        interpolation: Resampling,
        new_transform: Affine,
        dst_width: int,
        dst_height: int,
        src_crs: pyproj.CRS,
        dst_crs: pyproj.CRS,
    ) -> xr.Dataset:
        """
        Update image data using new spatial parameters and coordinate reference system.

        Parameters
        ----------
        interpolation : Resampling
            Resampling method to use when transforming data
        new_transform : Affine
            New affine transform matrix
        dst_width : int
            Width of destination image in pixels
        dst_height : int
            Height of destination image in pixels
        src_crs : pyproj.CRS
            Source coordinate reference system
        dst_crs : pyproj.CRS
            Destination coordinate reference system

        Returns
        -------
        xr.Dataset
            New dataset with updated spatial parameters

        Notes
        -----
        Internal method used by reproject() and resample() to update the image data with new
        spatial parameters. Performs resampling and coordinate transformation for all bands.

        Examples
        --------
        >>> # Used internally by reproject():
        >>> self.__update_data(
        ...     Resampling.nearest,
        ...     dst_transform,
        ...     dst_width,
        ...     dst_height,
        ...     self.crs,
        ...     new_crs
        ... )
        """

        dst_x, _ = rasterio.transform.xy(
            new_transform, np.zeros(dst_width), np.arange(dst_width)
        )
        _, dst_y = rasterio.transform.xy(
            new_transform, np.arange(dst_height), np.zeros(dst_height)
        )

        try:
            x_meta, y_meta = dst_crs.cs_to_cf()

            # Ensure proper coordinate order for geographic vs projected CRS
            if x_meta.get("standard_name") == "latitude":
                x_meta, y_meta = y_meta, x_meta
        except Exception:
            # Fallback for CRS that don't support cs_to_cf()
            x_meta = {
                "units": "degrees_east" if dst_crs.is_geographic else "m",
                "standard_name": (
                    "longitude" if dst_crs.is_geographic else "projection_x_coordinate"
                ),
            }
            y_meta = {
                "units": "degrees_north" if dst_crs.is_geographic else "m",
                "standard_name": (
                    "latitude" if dst_crs.is_geographic else "projection_y_coordinate"
                ),
            }

        wkt_meta = dst_crs.to_cf()

        coords = {
            "x": xr.DataArray(data=dst_x, coords={"x": dst_x}, attrs=x_meta),
            "y": xr.DataArray(data=dst_y, coords={"y": dst_y}, attrs=y_meta),
            self.grid_mapping: xr.DataArray(data=0, attrs=wkt_meta),
        }

        new_data_vars = {}
        for band in self.band_names:
            data = self.data[band].values
            dst_shape = (len(dst_y), len(dst_x))
            new_data = np.empty(dst_shape, dtype=data.dtype)

            new_data, _ = reproject(
                source=data,
                destination=new_data,
                src_transform=self.transform,
                src_crs=src_crs,
                dst_transform=new_transform,
                dst_crs=dst_crs,
                dst_nodata=0 if data.dtype == np.uint8 else np.nan,
                resampling=interpolation,
            )

            new_data_vars[band] = xr.DataArray(
                data=new_data,
                dims=("y", "x"),
                coords={"y": coords["y"], "x": coords["x"]},
                attrs={"grid_mapping": self.grid_mapping},
            )

        return xr.Dataset(data_vars=new_data_vars, coords=coords, attrs=self.data.attrs)

    def clip(self, geometries: List[BaseGeometry], inplace: bool = True) -> Image:
        """
        Clip image to given geometries.

        Creates a mask from the input geometries and trims the image extent to the minimum
        bounding box that contains all non-zero values.

        Parameters
        ----------
        geometries : List[BaseGeometry]
            List of geometries to clip to. The image will be
            clipped to the combined extent of all geometries.
        inplace : bool, optional
            If True (default), modifies the image in-place and returns self.
            If False, returns a modified copy without changing the original.

        Returns
        -------
        Self
            The modified Image object. Returns self if inplace=True,
            otherwise returns a new Image instance clipped to the geometries.

        Notes
        -----
        The new extent is calculated by:
        1. Finding the first and last rows that contain any values
        2. Finding the first and last columns that contain any values
        3. Keeping only the data within these bounds

        Examples
        --------
        >>> # Clip in-place (default)
        >>> image.clip([polygon])
        >>> # Image is now smaller
        >>> 
        >>> # Create clipped copy, keep original unchanged
        >>> clipped = image.clip([polygon], inplace=False)
        >>> # Original image dimensions unchanged
        """
        target = self._prepare_target(inplace)
        
        inshape = rasterio.features.geometry_mask(
            geometries=geometries,
            out_shape=(target.height, target.width),
            transform=target.transform,
            invert=True,
        )

        rows, cols = target._Image__find_empty_borders(inshape)
        target.data = target.data.isel({"y": rows, "x": cols})
        return target

    def mask(
        self,
        condition: np.ndarray,
        bands: str | List[str] = None,
        fill_true=None,
        fill_false=np.nan,
        inplace: bool = True,
    ) -> Image:
        """
        Mask image bands using condition array.

        Parameters
        ----------
        condition : np.ndarray
            Boolean mask array
        bands : str or List[str], optional
            Band(s) to apply mask to, by default None which applies to all bands
        fill_true : Any, optional
            Value to set where condition is True, by default None (no change)
        fill_false : Any, optional
            Value to set where condition is False, by default np.nan
        inplace : bool, optional
            If True (default), modifies the image in-place and returns self.
            If False, returns a modified copy without changing the original.

        Returns
        -------
        Self
            The modified Image object. Returns self if inplace=True,
            otherwise returns a new Image instance with the mask applied.

        Examples
        --------
        >>> # Mask values to NaN where condition is False (in-place, default)
        >>> image.mask(water_mask)
        >>> 
        >>> # Set values to 0 where False, keep original image unchanged
        >>> masked = image.mask(land_mask, fill_false=0, inplace=False)
        >>> 
        >>> # Set values to 1 where True, 0 where False (in-place)
        >>> image.mask(binary_mask, fill_true=1, fill_false=0)
        """
        target = self._prepare_target(inplace)
        condition_da = xr.DataArray(data=condition, dims=("y", "x"))
        
        if bands is not None:
            if fill_false is not None:
                target.data[bands] = target.data[bands].where(condition_da, fill_false)
            if fill_true is not None:
                target.data[bands] = target.data[bands].where(~condition_da, fill_true)
        else:
            if fill_false is not None:
                target.data = target.data.where(condition_da, fill_false)
            if fill_true is not None:
                target.data = target.data.where(~condition_da, fill_true)
        return target

    def geometry_mask(
        self,
        geometries: List[BaseGeometry],
        mask_out: bool = True,
        bands: str | List[str] = None,
        fill_true=None,
        fill_false=np.nan,
        inplace: bool = True,
    ) -> Image:
        """
        Mask image using geometries.

        Creates a binary mask from the input geometries and sets values to NaN either inside
        or outside the geometries depending on the mask_out parameter.

        Parameters
        ----------
        geometries : List[BaseGeometry]
            List of geometries for masking
        mask_out : bool, optional
            If True mask outside geometries, if False mask inside, by default True
        bands : str or List[str], optional
            Band(s) to apply mask to, by default None which applies to all bands
        fill_true : Any, optional
            Value to set where condition is True (inside/outside depending on mask_out),
            by default None (no change)
        fill_false : Any, optional
            Value to set where condition is False, by default np.nan
        inplace : bool, optional
            If True (default), modifies the image in-place and returns self.
            If False, returns a modified copy without changing the original.

        Returns
        -------
        Self
            The modified Image object. Returns self if inplace=True,
            otherwise returns a new Image instance with the mask applied.

        Examples
        --------
        >>> # Mask outside geometries to NaN (in-place, default)
        >>> image.geometry_mask(polygons)
        >>> 
        >>> # Mask outside to 0, keep original image unchanged
        >>> masked = image.geometry_mask(polygons, fill_false=0, inplace=False)
        >>> 
        >>> # Set inside to 1, outside to 0 (in-place)
        >>> image.geometry_mask(polygons, fill_true=1, fill_false=0)
        """
        target = self._prepare_target(inplace)
        
        condition = rasterio.features.geometry_mask(
            geometries=geometries,
            out_shape=(target.height, target.width),
            transform=target.transform,
            invert=mask_out,
        )

        target.mask(condition, bands, fill_true=fill_true, fill_false=fill_false, inplace=True)
        return target

    def dropna(self, inplace: bool = True) -> Image:
        """
        Remove rows and columns that contain all NaN values only when adjacent rows/columns also contain all NaN values.

        Parameters
        ----------
        inplace : bool, optional
            If True (default), modifies the image in-place and returns self.
            If False, returns a modified copy without changing the original.

        Returns
        -------
        Self
            The modified Image object. Returns self if inplace=True,
            otherwise returns a new Image instance with NaN borders removed.

        Notes
        -----
        The method preserves rows/columns with all NaN values if they are between rows/columns containing valid values.
        For example, if row 1 has values, row 2 is all NaN, and row 3 has values, row 2 will be preserved.

        Examples
        --------
        >>> # Drop NaN borders in-place (default)
        >>> image.dropna()
        >>> print(f"New size: {image.width}x{image.height}")
        >>> 
        >>> # Create copy without NaN borders, keep original unchanged
        >>> trimmed = image.dropna(inplace=False)
        >>> # Original image dimensions unchanged
        """
        target = self._prepare_target(inplace)
        
        mask = np.zeros((target.height, target.width))
        for data in target.data.data_vars.values():
            mask = np.logical_or(mask, ~np.isnan(data.values))

        rows, cols = target.__find_empty_borders(mask)
        target.data = target.data.isel({"y": rows, "x": cols})
        return target

    def __find_empty_borders(self, array: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Find non-empty row and column ranges in a binary array.

        Parameters
        ----------
        array : np.ndarray
            Binary array where True/non-zero values indicate data to keep

        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            Two arrays containing:
            - Row indices spanning first to last non-empty rows
            - Column indices spanning first to last non-empty columns

        Notes
        -----
        Finds the minimum spanning range of rows and columns that contain non-zero values.
        Used internally by clip() and dropna() methods to trim image extents.

        Examples
        --------
        >>> # For input array:
        >>> # 0 0 0 0 0
        >>> # 0 1 1 0 0
        >>> # 0 1 1 0 0
        >>> # 0 0 0 0 0
        >>> rows, cols = __find_empty_borders(array)
        >>> # rows = [1, 2]  # Indices of rows with data
        >>> # cols = [1, 2]  # Indices of columns with data
        """

        rows = np.where(array.any(axis=1))[0]
        rows = np.arange(rows.min(), rows.max() + 1)

        cols = np.where(array.any(axis=0))[0]
        cols = np.arange(cols.min(), cols.max() + 1)

        return rows, cols

    def select(self, bands: str | List[str]) -> np.ndarray:
        """
        Select specific bands from the image and return as numpy array (copy).

        This method returns a copy of the band data as a numpy array.
        Modifications to the returned array will not affect the original Image.

        Parameters
        ----------
        bands : str or List[str]
            Band(s) to select. Single string for one band,
            list of strings for multiple bands.

        Returns
        -------
        np.ndarray
            Copy of selected band data as numpy array:
            - For single band: 2D array with shape (height, width)
            - For multiple bands: 3D array with shape (n_bands, height, width)

        Examples
        --------
        >>> # Get single band as numpy array
        >>> blue = image.select('blue')
        >>> print(blue.shape)  # (height, width)
        >>> blue[mask] = 0  # Does NOT modify original image
        >>> 
        >>> # Get multiple bands
        >>> rgb = image.select(['red', 'green', 'blue'])
        >>> print(rgb.shape)  # (3, height, width)
        >>> 
        >>> # To modify original image, use add_band or __setitem__
        >>> modified = image.select('blue')
        >>> modified[mask] = 0
        >>> image['blue'] = modified  # Update original

        See Also
        --------
        __getitem__ : Equivalent method using bracket notation
        add_band : Add or update a band in the image
        """

        if isinstance(bands, str):
            return self.data[bands].values.copy()
        else:
            return np.array([ self.data[band].values.copy() for band in bands ])

    def add_band(self, band_name: str, data: np.ndarray | xr.DataArray, 
                 inplace: bool = True) -> Image:
        """
        Add a new band to the image or update an existing band.

        Parameters
        ----------
        band_name : str
            Name of the band to add or update
        data : np.ndarray or xr.DataArray
            Band data to add. Must match the spatial dimensions of existing bands
        inplace : bool, optional
            If True (default), modifies the image in-place and returns self.
            If False, returns a modified copy without changing the original.

        Returns
        -------
        Self
            The modified Image object. Returns self if inplace=True,
            otherwise returns a new Image instance with the band added/updated.

        Examples
        --------
        >>> # Add new band in-place (default)
        >>> image.add_band('ndvi', ndvi_data)
        >>> print(image.band_names)  # [..., 'ndvi']
        >>> 
        >>> # Create copy with new band, keep original unchanged
        >>> with_ndvi = image.add_band('ndvi', ndvi_data, inplace=False)
        >>> # 'ndvi' not in original image.band_names
        >>> 
        >>> # Update existing band (in-place)
        >>> image.add_band('blue', new_blue_data)
        """
        target = self._prepare_target(inplace)
        
        if isinstance(data, np.ndarray):
            if band_name not in target.band_names:
                target.data[band_name] = (("y", "x"), data)
            else:
                target.data[band_name].values = data
        else:
            target.data[band_name] = data
        return target

    def drop_bands(self, bands: str | List[str], inplace: bool = True) -> Image:
        """
        Remove specified bands from the image.

        Parameters
        ----------
        bands : str or List[str]
            Band(s) to remove
        inplace : bool, optional
            If True (default), modifies the image in-place and returns self.
            If False, returns a modified copy without changing the original.

        Returns
        -------
        Self
            The modified Image object. Returns self if inplace=True,
            otherwise returns a new Image instance without the dropped bands.

        Examples
        --------
        >>> # Drop bands in-place (default)
        >>> image.drop_bands(['B1', 'B2'])
        >>> print(image.band_names)  # B1, B2 removed
        >>> 
        >>> # Create copy without certain bands, keep original unchanged
        >>> subset = image.drop_bands(['B1', 'B2'], inplace=False)
        >>> # Original image still has B1, B2
        """
        target = self._prepare_target(inplace)
        target.data = target.data.drop_vars(bands)
        return target

    def keep_bands(self, bands: str | List[str], inplace: bool = True) -> Self:
        """
        Keep only specified bands and remove all others from the image.

        This is the inverse operation of drop_bands. Only the specified bands
        will be retained in the image, and all other bands will be removed.

        Parameters
        ----------
        bands : str or List[str]
            Band(s) to keep. All other bands will be removed.
        inplace : bool, optional
            If True (default), modifies the image in-place and returns self.
            If False, returns a modified copy without changing the original.

        Returns
        -------
        Self
            The modified Image object. Returns self if inplace=True,
            otherwise returns a new Image instance with only the specified bands.

        Examples
        --------
        >>> # Keep only RGB bands in-place (default)
        >>> image.keep_bands(['red', 'green', 'blue'])
        >>> print(image.band_names)  # ['red', 'green', 'blue']
        >>> 
        >>> # Keep single band
        >>> image.keep_bands('ndvi')
        >>> 
        >>> # Create copy with only specific bands, keep original unchanged
        >>> rgb_only = image.keep_bands(['red', 'green', 'blue'], inplace=False)
        >>> # Original image still has all bands

        See Also
        --------
        drop_bands : Remove specified bands (inverse operation)
        """
        target = self._prepare_target(inplace)
        bands_to_drop = set(target.band_names).difference(bands if isinstance(bands, list) else [bands])
        target.drop_bands(list(bands_to_drop), inplace=True)
        return target

    def normalized_diference(self, band1: str, band2: str) -> np.ndarray:
        """
        Calculate normalized difference between two bands.

        Computes the normalized difference index between two bands using the formula:
        (band1 - band2) / (band1 + band2)

        Parameters
        ----------
        band1 : str
            Name of the first band in the calculation (numerator)
        band2 : str
            Name of the second band in the calculation (denominator)

        Returns
        -------
        np.ndarray
            2D array containing the normalized difference values ranging from -1 to 1.
            Areas where both bands have zero values will result in NaN values.

        Notes
        -----
        This is a common operation in remote sensing used to create various spectral indices
        such as NDVI (Normalized Difference Vegetation Index), NDWI (Normalized Difference
        Water Index), etc.

        Values outside the -1 to 1 range can occur if negative values are present
        in the input bands.

        Examples
        --------
        >>> # Calculate NDVI using NIR and Red bands
        >>> ndvi = image.normalized_diference('nir', 'red')
        >>> image.add_band('ndvi', ndvi)
        >>>
        >>> # Calculate NDWI using Green and NIR bands
        >>> ndwi = image.normalized_diference('green', 'nir')
        >>> image.add_band('ndwi', ndwi)
        """

        b1 = self.data[band1].values.copy()
        b2 = self.data[band2].values.copy()

        return (b1 - b2) / (b1 + b2)

    def extract_values(
        self, xs: np.ndarray, ys: np.ndarray, bands: List[str] = None
    ) -> np.ndarray:
        """
        Extract values at specified coordinates from the image.

        Parameters
        ----------
        xs : np.ndarray
            X coordinates (longitude/easting) in the image's CRS
        ys : np.ndarray
            Y coordinates (latitude/northing) in the image's CRS
        bands : List[str], optional
            List of band names to extract values from.
            If None, extracts from all bands, by default None

        Returns
        -------
        np.ndarray
            Array of extracted values with shape:
        """

        bands = self.band_names if bands is None else bands
        rows, cols = rowcol(self.transform, xs, ys)

        # Verificar que las coordenadas estén dentro del raster
        valid_mask = (
            (rows >= 0) & (rows < self.height) & (cols >= 0) & (cols < self.width)
        )

        results = []
        for band in bands:
            band_data = self.select(band)
            values = np.full(len(xs), np.nan, dtype=band_data.dtype)

            if np.any(valid_mask):
                values[valid_mask] = band_data[rows[valid_mask], cols[valid_mask]]

            results.append(values)

        if len(bands) == 1:
            return results[0]

        return np.array(results)

    def interval_choice(
        self, band: str, size: int, intervals: Iterable, replace: bool = True
    ) -> np.ndarray:
        """
        Choose random values from intervals in specified band.

        Parameters
        ----------
        band : str
            Band to sample from
        size : int
            Number of samples
        intervals : Iterable
            Value intervals to sample from
        replace : bool, optional
            Sample with replacement if True, by default True

        Returns
        -------
        np.ndarray
            Selected values
        """

        if not isinstance(band, str):
            raise ValueError("band argument must a string")

        array = self.select(band).ravel()
        return selector.interval_choice(array, size, intervals, replace)

    def arginterval_choice(
        self, band: str, size: int, intervals: Iterable, replace: bool = True
    ) -> np.ndarray:
        """
        Choose random indices from intervals in specified band.

        .. deprecated:: 2.1.0
            Use :meth:`sample_indices_by_interval` instead. This method will be removed in version 3.0.0.

        Parameters
        ----------
        band : str
            Band to sample from
        size : int
            Number of samples
        intervals : Iterable
            Value intervals to sample from
        replace : bool, optional
            Sample with replacement if True, by default True

        Returns
        -------
        np.ndarray
            Selected indices
        """
        import warnings
        warnings.warn(
            "arginterval_choice is deprecated and will be removed in version 3.0.0. "
            "Use sample_indices_by_interval instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return self.sample_indices_by_interval(band, size, intervals, replace)

    def sample_indices_by_interval(
        self, band: str, size: int, intervals: Iterable, replace: bool = True
    ) -> np.ndarray:
        """
        Get indices of random samples from value intervals in a specified band.

        Parameters
        ----------
        band : str
            Band to sample from
        size : int
            Number of samples per interval
        intervals : Iterable
            Value intervals to sample from, e.g., [(0, 2), (2, 4), (4, 6)]
        replace : bool, optional
            Sample with replacement if True, by default True

        Returns
        -------
        np.ndarray
            Selected indices

        Examples
        --------
        >>> # Sample 100 indices from each depth interval
        >>> indices = image.sample_indices_by_interval('depth', 100, [0, 5, 10, 15])
        """

        if not isinstance(band, str):
            raise ValueError("band argument must a string")

        array = self.select(band).ravel()
        return selector.sample_indices_by_interval(array, size, intervals, replace)

    def empty_like(self) -> Image:
        """
        Create empty image with same metadata and coordinates.

        Returns
        -------
        Image
            New empty image
        """

        result = Image(deepcopy(self.data), deepcopy(self.crs))
        result.drop_bands(result.band_names)
        return result

    def copy(self) -> Image:
        """
        Create a deep copy of the image.

        Returns
        -------
        Image
            Deep copy of the image
        """

        return deepcopy(self)

    def to_netcdf(self, filename):
        """
        Save image to NetCDF file.

        Parameters
        ----------
        filename : str
            Output filename
        """

        self.data.attrs["proj4_string"] = self.crs.to_proj4()
        self.data.attrs["crs_wkt"] = self.crs.to_wkt()

        return self.data.to_netcdf(filename)

    def to_tif(self, filename):
        """
        Save image to GeoTIFF file.

        Parameters
        ----------
        filename : str
            Output filename
        """

        height, width = self.height, self.width
        count = self.count

        # Prepare the metadata for rasterio
        meta = {
            "driver": "GTiff",
            "height": height,
            "width": width,
            "count": count,
            "dtype": next(iter(self.data.data_vars.values())).dtype,
            "crs": self.crs,
            "transform": self.transform,
        }

        with rasterio.open(filename, "w", **meta) as dst:
            # Write each band
            for idx, (band_name, band_data) in enumerate(
                self.data.data_vars.items(), start=1
            ):
                dst.write(band_data.values, idx)
                dst.set_band_description(idx, band_name)

    def __str__(self) -> str:
        return f"Bands: {self.band_names} | Height: {self.height} | Width: {self.width}"

    def __repr__(self) -> str:
        return str(self)

    def _repr_html_(self) -> str:
        return self.data._repr_html_()


def compose(
    images: List[Image], method: Callable | np.ndarray, bands: List[str] | None = None
) -> Image:
    """
    Compose multiple images into one using a composition method.

    This function combines multiple images by applying a composition method to
    corresponding pixels across all input images. Common uses include creating
    cloud-free composites, calculating statistics across time series, or
    selecting optimal pixels based on quality metrics.

    Parameters
    ----------
    images : List[Image]
        List of Image objects to compose. All images should have compatible
        dimensions and coordinate reference systems.
    method : Callable or np.ndarray
        Method to use for composition. Can be either:
        - A callable function that takes an array of values across images and
          returns a single value (e.g., np.nanmean, np.nanmax)
        - An array of indices specifying which image to select for each pixel
    bands : List[str], optional
        List of band names to include in the composition, by default None which
        uses all bands from the first image

    Returns
    -------
    Image
        New Image object containing the composition result

    Notes
    -----
    The output image retains the spatial metadata (CRS, transform) from the first
    image in the list, but contains new pixel values based on the composition method.

    Examples
    --------
    >>> # Create a mean composite from multiple images
    >>> mean_composite = compose(image_list, np.nanmean)
    >>>
    >>> # Create a maximum NDVI composite
    >>> import numpy as np
    >>> ndvi_values = np.array([img.normalized_diference('nir', 'red') for img in image_list])
    >>> best_indices = np.nanargmax(ndvi_values, axis=0)
    >>> max_ndvi_composite = compose(image_list, best_indices)
    """
    if bands is None:
        bands = images[0].band_names

    result = images[0].empty_like()
    for band in bands:
        result.add_band(
            band,
            selector.composite(
                np.array([image.data[band].values for image in images]), method
            ),
        )

    return result
