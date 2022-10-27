from enum import Enum

# TODO  very awkward implementation of the moves ???


class AbaloneType(Enum):
    NORMAL = [
        [None, None, None, None, 1, 1, 1, 1, 1],
        [None, None, None, 1, 1, 1, 1, 1, 1],
        [None, None, 0, 0, 1, 1, 1, 0, 0],
        [None, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, None],
        [0, 0, 2, 2, 2, 0, 0, None, None],
        [2, 2, 2, 2, 2, 2, None, None, None],
        [2, 2, 2, 2, 2, None, None, None, None]
    ]
    SPLIT = [
        [None, None, None, None, 1, 1, 0, 2, 2],
        [None, None, None, 1, 1, 1, 2, 2, 2],
        [None, None, 0, 1, 1, 0, 2, 2, 0],
        [None, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, None],
        [0, 0, 2, 2, 2, 0, 0, None, None],
        [2, 2, 2, 2, 2, 2, None, None, None],
        [2, 2, 2, 2, 2, None, None, None, None]
    ]

    def copy(self):
        return [row[:] for row in self.value]


class AbaloneGrid:

    def __init__(self, type_: AbaloneType = AbaloneType.NORMAL):
        grid = type_.copy()
        self.grid = grid

    @staticmethod
    def in_grid(item):
        i, j = item
        return 0 <= i < 9 and 0 <= j < 9

    def __getitem__(self, item):
        i, j = item
        if not self.in_grid(item):
            raise IndexError("Out of the grid")
        val = self.grid[i][j]
        if val is None:
            raise IndexError("Out of the grid")
        return val

    def __setitem__(self, key, value):
        if not self.in_grid(key):
            raise IndexError("Out of the grid")
        i, j = key
        if self.grid[i][j] is None:
            raise IndexError("Out of the grid")
        else:
            self.grid[i][j] = value

    def __str__(self):
        s = ""
        count = 4
        for i in range(9):
            s += "\n" if i != 0 else ""
            s += " "*abs(count)
            s += " ".join(".OX"[a] for a in self.grid[i] if a is not None)
            count -= 1
        return s

    def copy(self):
        cop = AbaloneGrid()
        for i in range(9):
            cop.grid[i] = self.grid[i][:]
        return cop
