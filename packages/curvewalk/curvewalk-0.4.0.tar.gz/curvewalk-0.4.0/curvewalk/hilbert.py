from typing import Tuple, Iterable, Generator, Dict


def hilbert(
    index: int,
    shape: Tuple[int, ...],
) -> Tuple[int, ...]:
    """
    Returns a position in the hilbert curve, given an index and a shape to follow.
    """

    dim = shape[0]
    for shape_dim in shape:
        if shape_dim <= 0:
            raise ValueError("Shape dimensions must be greater than zero.")
        if shape_dim != dim:
            raise ValueError("All dimensions in shape must be equal for Hilbert curve.")

    if (dim & (dim - 1)) != 0:
        raise ValueError("Shape dimension must be a power of two for Hilbert curve.")

    iterations = dim.bit_length() - 1

    if len(shape) == 2:

        def grow_2d_hilbert_path(path: Iterable[str]) -> Generator[str, None, None]:
            """Grow the Hilbert path by one iteration."""
            for char in path:
                if char == "A":
                    yield from "+BF-AFA-FB+"
                elif char == "B":
                    yield from "-AF+BFB+FA-"
                else:
                    yield char

        path = "A"
        for _ in range(iterations):
            path = grow_2d_hilbert_path(path)

        pos = (0, 0)
        dir = (0, 1)

        path = list(path)

        def iterate_2d(
            position: Tuple[int, int], direction: Tuple[int, int], next: str
        ) -> Tuple[Tuple[int, int], Tuple[int, int], bool]:
            """Iterate over hilbert path in 2d."""
            right_rotations: Dict[Tuple[int, int], Tuple[int, int]] = {
                (1, 0): (0, 1),
                (0, 1): (-1, 0),
                (-1, 0): (0, -1),
                (0, -1): (1, 0),
            }
            left_rotations = {b: a for a, b in right_rotations.items()}

            moved = False

            match next:
                case "F":
                    position = (position[0] + direction[0], position[1] + direction[1])
                    moved = True
                case "+":
                    direction = left_rotations[direction]
                case "-":
                    direction = right_rotations[direction]
                case "A" | "B":
                    pass

            return position, direction, moved

        movements = 0
        for char in path:
            if movements == index:
                break
            pos, dir, moved = iterate_2d(pos, dir, char)
            if moved:
                movements += 1

    return pos
