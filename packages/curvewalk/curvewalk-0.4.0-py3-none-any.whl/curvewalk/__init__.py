from typing import Any, Callable, Optional, Tuple, Generator
from functools import reduce


def iterate_over(
    array: Any,
    method: Callable[
        [int, Tuple[int, ...], Optional[Tuple[int, ...]]], Tuple[int, ...]
    ],
    order: Optional[Tuple[int, ...]] = None,
) -> Generator[Any, None, None]:
    """
    Use a walker method to iterate over an array. The array can either be a
    plain python array or a numpy style array.
    """
    shape = []
    allows_multidimension = False

    # Handle numpy style arrays
    if hasattr(array, "shape"):
        shape = array.shape
        allows_multidimension = True
    else:
        # Fallback for nested lists or other iterable structures
        try:
            inside = array
            while True:
                shape.append(len(inside))
                inside = inside[0]
        except TypeError:
            pass

    shape = tuple(shape)

    size = reduce(lambda x, y: x * y, shape, 1)
    if allows_multidimension:
        # Quickly index multi-dimensional arrays
        for i in range(size):
            pos = method(i, shape, order)
            yield array[pos]
    else:

        def get(a, p):
            """Recursive function to get the value at a specific position."""
            if len(p) == 1:
                return a[p[0]]
            else:
                return get(a[p[0]], p[1:])

        for i in range(size):
            pos = method(i, shape, order)
            yield get(array, pos)


def flatten(
    array: Any,
    method: Callable[
        [int, Tuple[int, ...], Optional[Tuple[int, ...]]], Tuple[int, ...]
    ],
    order: Optional[Tuple[int, ...]] = None,
) -> Any:
    """
    Flattens a multi-dimensional array into a 1D array using the specified method.
    """
    return list(iterate_over(array, method, order))
