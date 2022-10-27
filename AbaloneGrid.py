from enum import Enum

from game_tools import tools

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


class Position:
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def __iter__(self):
        return (self.row, self.col).__iter__()

    def __add__(self, other):
        if isinstance(other, Position):
            row, col = other.row, other.col
        else:
            row, col = other
        return Position(self.row + row, self.col + col)

    def __sub__(self, other):
        if isinstance(other, Position):
            row, col = other.row, other.col
        else:
            row, col = other
        return self.row - row, self.col - col

    def __eq__(self, other):
        return self.row == self.col


class TypeAction(Enum):
    INLINE = "Inline"
    PARALLEL = "Parallel"
    INVALID = "Invalid"


class AbaloneGame(tools.GameNPlayer):
    _win_nb_marbles = 6
    _directions = [(-1, 0), (-1, 1), (1, -1), (0, 1), (0, -1), (1, 0)]
    _not_a_player = 0

    def __init__(self, type_: AbaloneType = AbaloneType.NORMAL):
        super().__init__()
        self.grid = AbaloneGrid(type_)
        self.type_ = type_
        self.marbles_down = [0, 0]

    def init_game(self, *args, **kwargs):
        self.grid = AbaloneGrid(self.type_)
        self.marbles_down = [0, 0]
        self.turn = 0
        self.player = 0

    def play(self, action: tuple[list[Position], Position]) -> bool:
        selection, goto = action
        if not self.check_selection(selection):
            raise tools.InvalidAction
        type_action, nb_marbles = self.check_action(selection, goto)
        if type_action == TypeAction.INVALID:
            raise tools.InvalidAction
        move = goto - selection[0]
        if type_action == TypeAction.PARALLEL:
            for pos in selection:
                self.grid[pos+move] = self.grid[pos]
                self.grid[pos] = self._not_a_player
            self.next_player()
            return False
        if type_action != TypeAction.INLINE:  # should never happen
            raise ValueError("Wrong action type")
        pos = selection[0]
        opp = (self.player + 1) % 2
        next_val = self._not_a_player
        for _ in range(nb_marbles):
            pos2 = pos+move
            val, next_val = next_val, self.grid[pos]
            self.grid[pos] = val
            try:
                self.grid[pos2] = val
            except IndexError:
                self.marbles_down[opp] += 1
                win = self.win(action) >= 0
                if win:
                    return True
            pos = pos2
        self.next_player()
        return False

    def check_selection(self, sel: list[Position], player=None) -> bool:
        if player is None:
            player = self.player
        player += 1  # on the grid, the space value is +1 the player id
        if len(sel) == 1:
            return self.grid[sel[0]] == player
        if len(sel) > 3:
            return False
        move = sel[1] - sel[0]
        if move not in self._directions:
            return False
        if len(sel) == 3:
            move2 = sel[2] - sel[1]
            if move != move2:
                return False
        for pos in sel:
            if self.grid[pos] != player:
                return False
        return True

    def check_action(self, sel: list[Position],
                     goto: Position, player=None) -> tuple[TypeAction, int]:
        if player is None:
            player = self.player
        player += 1  # on the grid, the space value is +1 the player id
        move = goto - sel[0]
        if move not in self._directions:
            return TypeAction.INVALID, 0
        if len(sel) != 1 and sel[1] != goto:
            # it's a broad-line action of several marbles :
            # the marbles can go only on empty spaces
            for pos in sel:
                pos2 = pos+move
                if self.grid[pos2] != self._not_a_player:
                    return TypeAction.INVALID, 0
            return TypeAction.PARALLEL, len(sel)
        nb = 1
        pos2 = sel[0]+move
        while self.grid.in_grid(pos2) and self.grid[pos2] == player:
            pos2 += move
            nb += 1
            if nb > 3:
                raise tools.InvalidActionError("Too many marbles : max. 3.")
        if not self.grid.in_grid(pos2):
            raise tools.InvalidActionError("Trying to suicide their own marble")
        nb2 = 0
        opp = (self.player + 1) % 2 + 1
        while self.grid.in_grid(pos2) and self.grid[pos2] == opp:
            pos2 += move
            nb2 += 1
            if nb2 >= nb:
                raise tools.InvalidActionError(
                    "Must have strict avantage to push opponent")
        return TypeAction.INLINE, nb+nb2

    def can_play(self) -> bool:
        # The chances are slim that a player will not be able to play
        raise NotImplemented

    def possible_actions(self):
        raise NotImplemented("Too many possibilities, not implemented")

    def win(self, action) -> int:
        a, b = self.marbles_down
        if a >= self._win_nb_marbles:
            return 1
        elif b >= self._win_nb_marbles:
            return 0
        return -1

    def __str__(self):
        a, b = self.marbles_down
        s = f"Action n°{self.turn} | Current player = {self.player}\n" \
            f"  -- Marbles down : {a} - {b}\n\n"
        s += str(self.grid)
        return s


if __name__ == "__main__":
    ab = AbaloneGame()
    action_ = ([Position(0, 4)], Position(1, 3))
    print("===== Action 1 =====")
    ab.play(action_)
    print(ab)
    action_ = ([Position(6, 2), Position(6, 3), Position(6, 4)], Position(5, 2))
    print("===== Action 2 =====")
    ab.play(action_)
    print(ab)
