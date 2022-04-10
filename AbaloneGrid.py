class AbaloneGrid(list):
    def __new__(cls):
        instance = list.__new__(cls)
        return instance

    def __init__(self):
        """

        :type self: list
        """
        grid = [[0] * 9] * 9  # 0 = vacuum case
        grid[0] = [None, None, None, None, 1, 1, 1, 1, 1]
        grid[1] = [None, None, None, 1, 1, 1, 1, 1, 1]
        grid[2] = [None, None, 0, 0, 1, 1, 1, 0, 0]
        grid[3] = [None, 0, 0, 0, 0, 0, 0, 0, 0]
        grid[4] = [0] * 9
        grid[5] = [0, 0, 0, 0, 0, 0, 0, 0, None]
        grid[6] = [0, 0, 2, 2, 2, 0, 0, None, None]
        grid[7] = [2, 2, 2, 2, 2, 2, None, None, None]
        grid[8] = [2, 2, 2, 2, 2, None, None, None, None]
        list.__init__(self, grid)

    def __getitem__(self, item):
        try:
            i, j = item
            if i < 0 or j < 0:
                raise IndexError("Out of Grid")
            if list.__getitem__(self, i)[j] is None:
                raise IndexError("Out of the grid")
            else:
                return list.__getitem__(self, i)[j]
        except IndexError:
            raise IndexError("Out of the grid")
        except TypeError:
            return list.__getitem__(self, item)

    def __setitem__(self, key, value):
        try:
            i, j = key
            if self[i, j] is None:
                raise IndexError("Out of the grid")
            else:
                list.__setitem__(self[i], j, value)
        except IndexError:
            raise IndexError("Out of the grid")
        except TypeError:
            list.__setitem__(self, key, value)

    def __str__(self):
        s = ""
        for i in range(9):
            s += str(self[i])
            s += "\n"
        return s

    def __contains__(self, item):
        for i in range(9):
            for j in range(9):
                try:
                    if self[i, j] == item:
                        return True
                except IndexError:
                    pass
        return False

    def __iter__(self):
        print("hello")
        return list.__iter__(self)

    def copy(self):
        cop = AbaloneGrid()
        for i in range(9):
            cop[i] = self[i].copy()
        return cop
