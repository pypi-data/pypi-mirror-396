from itertools import pairwise
from typing import Callable, Iterable, List

import numpy as np


def _get_limit_masks(array: np.array, pairs: Iterable) -> List[np.array]:
    """Generates a list of boolean masks for the given array based on the provided pairs of limits.

    Args:
        array (np.array): array to be masked
        pairs (Iterable): list of pairs of limits

            e.g. [(0, 1), (1, 2), (2, 3)]

    Returns:
        List[np.array]: list of boolean masks for the given array based on the provided pairs of limits
    """

    return [(vmin <= array) & (array < vmax) for vmin, vmax in pairs]


def interval_choice(
    array: np.ndarray, size: int, intervals: Iterable, replace=True
) -> np.ndarray:
    """Generates a random sample from the given array based on the provided intervals.

    Args:
        array (np.ndarray): array to be sampled
        size (int): size for each interval
        intervals (Iterable): intervals to be sampled from

                e.g. [(0, 1), (1, 2), (2, 3)]
        replace (bool, optional): np.choice sample argument. Defaults to True.

    Returns:
        np.ndarray: Random sample from the given array based on the provided intervals.
    """

    limit_masks = _get_limit_masks(array, pairwise(intervals))
    return np.array(
        [
            np.random.choice(array[in_limits], size, replace=replace)
            for in_limits in limit_masks
        ]
    ).ravel()


def sample_indices_by_interval(
    array: np.ndarray, size: int, intervals: Iterable, replace=True
) -> np.ndarray:
    """Get indices of a random sample from the array based on value intervals.

    Args:
        array (np.ndarray): array to be sampled
        size (int): number of samples per interval
        intervals (Iterable): value intervals to sample from

                e.g. [(0, 1), (1, 2), (2, 3)]
        replace (bool, optional): whether to sample with replacement. Defaults to True.

    Returns:
        np.ndarray: Indices of the random sample from the given array.

    Examples:
        >>> # Sample 10 indices from each depth interval
        >>> depths = np.array([0.5, 1.5, 2.5, 3.5, 4.5])
        >>> indices = sample_indices_by_interval(depths, 10, [0, 2, 4, 6])
    """

    indexes = np.arange(array.size)
    limit_masks = _get_limit_masks(array, pairwise(intervals))
    return np.array(
        [
            np.random.choice(indexes[in_limits], size, replace=replace)
            for in_limits in limit_masks
        ]
    ).ravel()


def arginterval_choice(
    array: np.ndarray, size: int, intervals: Iterable, replace=True
) -> np.ndarray:
    """Generates the indexes of a random sample from the given array based on the provided intervals.

    .. deprecated:: 2.1.0
        Use :func:`sample_indices_by_interval` instead. This function will be removed in version 3.0.0.

    Args:
        array (np.ndarray): array to be sampled
        size (int): size for each interval
        intervals (Iterable): intervals to be sampled from

                e.g. [(0, 1), (1, 2), (2, 3)]
        replace (bool, optional): np.choice sample argument. Defaults to True.

    Returns:
        np.ndarray: The indexes of a random sample from the given array based on the provided intervals.
    """
    import warnings
    warnings.warn(
        "arginterval_choice is deprecated and will be removed in version 3.0.0. "
        "Use sample_indices_by_interval instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return sample_indices_by_interval(array, size, intervals, replace)


def composite(
    arrays: np.ndarray, method: Callable | np.ndarray = np.nanmax
) -> np.ndarray:
    """Generates a synthetic array based on the provided method.

    Args:
        arrays (np.ndarray): a list of arrays to be composed
        method (Callable | np.ndarray, optional): numpy funcion or list of indexes to compose the final array. Defaults to np.nanmax.

    Returns:
        np.ndarray: a synthetic array based on the provided method.
    """

    if isinstance(method, np.ndarray):
        m, n = method.shape
        i, j = np.ogrid[:m, :n]
        return arrays[method, i, j]

    else:
        return method(arrays, axis=0)


def composite_indices(arrays: np.ndarray, method: Callable = np.argmax) -> np.ndarray:
    """Get indices of optimal values across multiple arrays for compositing.

    Finds which array contains the optimal value (e.g., maximum, minimum) at each position,
    returning an index array that can be used with the composite() function.

    Args:
        arrays (np.ndarray): stack of arrays with shape (n_arrays, height, width)
        method (Callable, optional): numpy argmax/argmin function to determine optimal values.
            Defaults to np.argmax.

    Returns:
        np.ndarray: 2D array of indices indicating which input array has the optimal value
            at each position.

    Examples:
        >>> # Create max NDVI composite
        >>> ndvi_stack = np.array([img1_ndvi, img2_ndvi, img3_ndvi])
        >>> best_indices = composite_indices(ndvi_stack, np.argmax)
        >>> max_ndvi_composite = composite(image_stack, best_indices)
    """

    nans = np.isnan(arrays).all(axis=0)
    arrays[:, nans] = np.inf
    indexes = method(arrays, axis=0)
    arrays[:, nans] = np.nan
    return indexes


def argcomposite(arrays: np.ndarray, method: Callable = np.argmax) -> np.ndarray:
    """Generates the indexes of a synthetic array based on the provided method.

    .. deprecated:: 2.1.0
        Use :func:`composite_indices` instead. This function will be removed in version 3.0.0.

    Args:
        arrays (np.ndarray): the array to be composed
        method (Callable, optional): a numpy method such as argmax. Defaults to np.argmax.

    Returns:
        np.ndarray: The indexes of a synthetic array
    """
    import warnings
    warnings.warn(
        "argcomposite is deprecated and will be removed in version 3.0.0. "
        "Use composite_indices instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return composite_indices(arrays, method)
