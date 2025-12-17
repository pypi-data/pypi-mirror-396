from typing import Optional, Tuple


def lawnmower(
    index: int, shape: Tuple[int, ...], order: Optional[Tuple[int, ...]] = None
) -> Tuple[int, ...]:
    """
    Returns a position in the lawnmower pattern, given a shape to traverse
    over. If order is specified, perform the iteration over a different
    ordering of the axes.
    """

    # Setup an ascending order
    if order is None:
        order = tuple(range(len(shape)))

    # Check the size of the input are correct
    if len(order) != len(shape):
        raise ValueError("Order must match the number of dimensions in shape.")

    reshape = [shape[i] for i in order]

    # Convert flat index to normal coordinates (row-major order)
    coords = []
    remaining = index
    for dim in reversed(reshape):
        coords.append(remaining % dim)
        remaining //= dim
    coords.reverse()

    # Apply lawnmower flipping: flip axis i if the sum of parities of all previous axes is odd
    for i in range(1, len(coords)):
        flip = sum(coords[j] % 2 for j in range(i)) % 2 == 1
        if flip:
            coords[i] = reshape[i] - 1 - coords[i]

    recoords = [0] * len(shape)
    for pos, value in zip(order, coords):
        recoords[pos] = value
    return tuple(recoords)


def inverse_lawnmower(
    position: Tuple[int, ...],
    shape: Tuple[int, ...],
    order: Optional[Tuple[int, ...]] = None,
) -> int:
    """
    Returns the inverse of the lawnmower function, given a position in the
    walk, returns the index along the walk.
    """
    if order is None:
        order = tuple(range(len(shape)))

    if len(order) != len(shape):
        raise ValueError("Order must match the number of dimensions in shape.")

    # Reorder the position and shape
    reshape = [shape[i] for i in order]
    coords = [position[i] for i in order]

    # reverse the flipping that `lawnmower` applied
    for i in range(len(coords) - 1, 0, -1):
        # Compute whether a flip was applied at this axis
        flip = sum(coords[j] % 2 for j in range(i)) % 2 == 1
        if flip:
            coords[i] = reshape[i] - 1 - coords[i]

    # flatten coords to linear index (row-major)
    index = 0
    for i in range(len(coords)):
        index = index * reshape[i] + coords[i]

    return index
