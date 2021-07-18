"""
This file is part of tcg.
"""
from dataclasses import dataclass
from copy import deepcopy
from itertools import product
import numpy as np

@dataclass
class Loc:
    """Make Location object to represent location on grid.

    Locations on a 3x3 grid. Locations are represented by their
    x and y coordinates. For locations 1,...,9 numbered in the same 
    order as on a phone keypad, the coordinates are:
    1: (0, 2), 2: (1, 2), 3: (2, 2), 
    4: (0, 1), 5: (1, 1), 6: (2, 1),
    7: (0, 0), 8: (1, 0), 9: (2, 0).

    Args:
        x: An int. The x coordinate on the grid.
        y: An int. The y coordinate on the grid.

    """
    x: int
    y: int 

    # Define the build-in + operation.
    def __add__(self, move):
        """Return location that results from self + move.

        Args:
            move: A string or an integer.
        
        Return: Loc object.

        """
        # Use to switch between string, int, and array representation
        # of move.
        move_str2arr = {
            "up": np.array((0, 1)), "right": np.array((1, 0)), 
            "down": np.array((0, -1)), "left": np.array((-1, 0))
        }
        move_int2arr = {
            1: np.array((0, 1)), 2: np.array((1, 0)),
            3: np.array((0, -1)), 4: np.array((-1, 0))
        }
        if isinstance(move, str):
            new_loc = np.array((self.x, self.y)) + move_str2arr[move]
        elif isinstance(move, int):
            new_loc = np.array((self.x, self.y)) + move_int2arr[move]
        # Else isintstance(move, Loc)
        return Loc(new_loc[0], new_loc[1])
        # TODO: raise Error or not? (valuecheck or not, related to on_grid and
        # direct_routes)
        # if on_grid(tuple(new_loc)):
        #     return Loc(new_loc[0], new_loc[1])
        # else:
        #     raise ValueError("Supply a valid move, given grid location!")


    # Define the build-in - operation.
    def __sub__(self, other):
        """Return distance (x_dist, y_dist) between self and other.

        Args:
            other: A Location object.

        Return: Numpy array.

        """
        return np.array((self.x, self.y)) - \
            np.array((other.x, other.y))

# TODO: add differentiation between rectangle and triangle
# in the + and - fuctions, now only works for circle and triangle.
@dataclass
class Orient:
    """Make Orientation object to represent orientation of token.

    Token can be circle, rectangel, or triangle.

    Circle: orientation is always 0. (Cirle has not orientation.)
    Rectangle: orientation is 1 or 2.
    Triangle: orientation is 1: "up", 2 "right", 3: "down", 4: "right".

    Args:
        val: An int. Represents the orientation.
    """
    val: int

    def __add__(self, int_val):
        """Return orientation: int_val turns to the right from self.

        Args:
            int_val: An integer. The nr of turns.

        Returns: An Orientation object.

        """
        # Case: circle. Turning does not change its orientation.
        if self.val == 0:
            return deepcopy(self)
        return Orient((self.val + int_val) % 5)

    
    def __sub__(self, int_val):
        """ Return orientation: int_val turns to the left from self.

        Args:
            int_val: An integer. The nr of turns.

        Returns: An Orientation object.

        """
        # Case: circle. Turning does not change its orientation.
        if self.val == 0:
            return Orient(0)
        return Orient((self.val - int_val) % 5)

@dataclass
class Position:
    """Make Position object to represent token position on grid.

    A position is defined as a location together with an orientation.

    Args:
        loc: A Location object. Represents location on grid.
        orient: An Orientation object. Represents orientation of token.

    Returns: A Position object.

    """
    loc: Loc
    orient: Orient

    def move(self, move):
        """Return position that results from self.loc + location move.

        Args:
            move: A string or int. Represents a movement up, right, 
                down, or left.

        Returns: A Position object: location adjacent to self.loc, and 
            orientation equal to self.orient.

        """
        return Position(deepcopy(self.loc) + move, deepcopy(self.orient))


    def move_seq(self, moves: list):
        """Return sequence of positions resulting from self.loc + moves.

        The sequence includes self as start position.
        Use in direct_routes() in language.py.

        Args:
            moves: A list with moves. A move is a string or int, and
                represents a movement up, right, down, or left.

        Returns: A list of Position objects: a sequence of adjacent 
            locations. (The orientation is constant.)

        """
        seqs = [deepcopy(self)]
        for move in moves:
            new_pos = Position(seqs[-1].loc + move, deepcopy(seqs[-1].orient))
            seqs.append(new_pos)
        return seqs


    def turn(self, turn: str):
        """Return Position with orientation self.orient + turn.

        Args:
            turn: A string. Either "clock" or "counter" for 
                turning clockwise and counter-clockwise.
                TODO: Also make work for int and Orientation object?

        Returns: A Position object.

        """
        if turn == "clock":
            return Position(deepcopy(self.loc), self.orient + 1)
        if turn == "counter":
            return Position(deepcopy(self.loc), self.orient - 1)
        raise ValueError("Supply a valid turn!")

# TODO: extend so that loc may also be Position object?
def on_grid(loc: np.ndarray):
    """Check whether a given "location" is on the grid.

    Use to check whether a move is valid on a loction.
    TODO: decide where to to this check.

    Args:
        loc: A numpy array, tuple or Location object.

    Returns: A Boolean.

    """
    grid = list(product(range(3), repeat=2))
    if isinstance(loc, (np.ndarray, tuple)):
        if len(loc) != 2:
            raise ValueError("Supply a tuple of length 2!")
        return loc in grid
    if isinstance(loc, Loc):
        return (loc.x, loc.y) in grid
    raise ValueError("Supply a location as tuple or Loc object!")


# Not used at the moment.
move_tup2str = {
    (0, 1): "up", (1, 0): "right", 
    (0, -1): "down", (-1, 0): "left"
}
pos_int2tup = {
    1: (0, 2), 2: (1, 2), 3: (2, 2), 
    4: (0, 1), 5: (1, 1), 6: (2, 1),
    7: (0, 0), 8: (1, 0), 9: (2, 0)
}
