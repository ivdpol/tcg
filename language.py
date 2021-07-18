"""
This file is part of tcg.
"""
from itertools import chain
import random 
from grid import Loc, Orient, Position
from operators import get_all_operators, Operator

class Language():
    """Class to construct a language used in the tcg game.

    Attributes:
        loc_opr: An Operator object. For communicating location.
        orient_opr: An Operator object. For communicating orientation.
        signal_order: A tuple. The order in which the the two 
            meaning components location and orientation are 
            communicated. Either ("loc", "orient"), or 
            ("orient", "loc").

    """
    def __init__(self, loc_oprs: list, orient_oprs: list, verbose=False):
        """Make Language object for the tcg game.

        Select a location and a orientation operator, and set the signal 
        order.

        Restriction: Each meaning component (location and orientation)  
        is communicated with one unique operator, irrespective of
        which location and orientation. This implies compositionality.

        The specific location or orientation determines the values
        of the input variables of the operators. The values can be set
        on the basis of iconicity principles. (TODO: define and 
        implement the the iconicity principles: a subset of biases 
        for setting operator variables.) An operator with the values for 
        its variables is called an intensional trajectory: a recipe for
        a physical trajectory over the tcg grid. The actual 
        physical trajectory over the grid (a sequence of adjacent 
        locations) is called the intensional trajectory.

        Args:
            loc_oprs: A list of Operator objects (named tuples). 
                Potential location operators.
            orient_oprs: A list of Operator objects (named tuples).  
                Potential orientation operators.

        """
        self.loc_opr = random.choice(loc_oprs)
        set_opr_vars(self.loc_opr, verbose)
        remain_oprs = [opr for opr in orient_oprs if opr != self.loc_opr]
        self.orient_opr = random.choice(remain_oprs)
        set_opr_vars(self.orient_opr)
        self.signal_order = random.choice(
            [("loc", "orient"), ("orient", "loc")]
        )


    # TODO: implement biases for setting operator variables.
def set_opr_vars(opr: Operator, verbose=False):
    """Set the values of the operator variables.
    
    Only the values of the variables listed in opr.pos_vals
    are set. There might be more variables. They need 
    to be set later, when using the operator to create
    extensional trajectories in ext_trajects.

    """ 
    if verbose:
        print("opr\t", opr)
    for var, pos_vals in opr.pos_vals.items():
        if verbose:
            print("var\t", var, "\tpos_vls\t", pos_vals)
        # Set operator value. Randomly.
        opr.vals[var] = random.choice(pos_vals)
    if verbose:
        print()

def list_of_len_with_sum(length: int, summ: int):
    """Recursive help function for direct_routes().

    Creates templates for all possible direct routes between a
    start end finish point on a grid. A route is a sequence of adjacent
    positions. 

    Uses the fact that each direct route between start and finish
    can be written as (i_1 * x_move, y_move, i_1 * x_move, y_move,
    ... , i_k * x_move), for k = lenght = abs(y_distance) + 1 between   
    start and finish and sum(i_1, ... , i_k) = summ = abs(x_distance)
    between start and finish. Where the direction of x and y move is
    determined by the sign of the x and y distance between start and 
    finish.

    Args:
        length: An int. The (absolute) y-axis differece between start  
            and finish, + 1. 
        summ: An int. The (absolute) x-axis differece between start and 
            finish.

    Yields: A list with ints. A template for a direct route between 
        two points on a grid. The route can be build as follows. An 
        x-move is either always left or alwayr right, and an y-move 
        is either always up or always down. This depends on the start 
        and finish point, and the corresponding 'sign' of the 
        x-difference and the y-difference between start and finish. 
        Then for each int i in the list put i many sequential x-moves 
        (i may be 0) followed by 1 y-move. For the last int i: only 
        put i x-moves (not followed by an y-move).

    """
    if length == 0 and summ == 0:
        yield []
    elif length > 0:
        for idx in range(summ + 1):
            for x_moves_templates in list_of_len_with_sum(
                length - 1, summ - idx
            ):
                yield [idx] + x_moves_templates

def direct_routes(start: Position, finish: Position):
    """Yield all direct routes on the grid from start to finish.

    Uses list_of_len_with_sum() to determine templates of all direct 
    routes. A template is a list of ints. Use this template as follows.  
    An x-move is either always left or alwayr right, and an y-move 
    is either always up or always down. This depends on the start 
    and finish point, and the corresponding 'sign' of the 
    x-difference and the y-difference between start and finish.
    Then for each int i in the list put i many sequential x-moves 
    (i may be 0) followed by 1 y-move. For the last int i: only 
    put i x-moves (not followed by an y-move).

    Args:
        start: A Postion object: location (x, y) and an orientation.
        finish: A Position object: location (x, y) and an orientation.

    Yields: A list of Position objects: a sequence of adjacent 
        locations. (The orientation is constant.)
        TODO: incorporate a possible turn or orientation, so that
        start and finish may be a rectangle or triangle in different 
        orientation. Current version works for circle token.

    """
    x_dist, y_dist = finish.loc - start.loc
    # Determine the x,y moves, depending on the sign of the difference.
    if x_dist < 0:
        x_move = "left"
    else:
        x_move = "right"
    if y_dist < 0:
        y_move = "down"
    else:
        y_move = "up"

    x_moves_templates = list_of_len_with_sum(abs(y_dist) + 1, abs(x_dist))
    for x_template in x_moves_templates:
        # The x_template is a list of ints, each int i represents a 
        # a sequence of i x-moves alternated by 1 y-move (where i may 
        # be 0).
        # Translate template to list of moves.
        direct_route_moves = list(chain.from_iterable(map(
            lambda num_x_moves: [x_move] * num_x_moves + [y_move], 
            x_template
        ))
        )[:-1]
        # Translate starting point + sequences of moves into sequence
        # Positions: the extensional trajectory.
        yield start.move_seq(direct_route_moves)

def ext_trajects(
    lang: Language, goal: Position, start_finish: tuple, verbose=False
):
    """Yield all ext trajectories, given language, goal, star, finish.

    Extensional trajectories are a sequence of adjacent locations over 
    the grid. (Definition: a location is adjacent to itself, and to
    a location up, right, down, or left to itself.

    Args:
        language: A Language object with location operator, orientation 
            operator, and signal order (location or orientation first).
            The language/strategy used by the sender.
        goals: A Position object. The receiver goals: the meaning
            components to be communicated to the receiver by the sender.
        start_finish: A tuple with the start position and the finish
            position of the sender. 
    
    Yields: A lists of adjacent Positions. A trajectories from start to 
        finish, with location signal and orientation signal in the rigth 
        order. 

    """
    start_pos, end_pos = start_finish
    # This is under assumption of location and orientation iconicity:
    # the first two varable values of the operators are set to goal 
    # Position and goal orientation.
    # TODO: How to make it more general?
    loc_seq = lang.loc_opr(
        goal, goal.orient.val, 
        *[lang.loc_opr.vals[var] for var in lang.loc_opr.func_vars[2:]]
    )
    orient_seq = lang.orient_opr(
        goal, goal.orient.val, 
        *[lang.orient_opr.vals[var] for var in lang.orient_opr.func_vars[2:]]
    )
    if lang.signal_order == ("loc", "orient"):
        comm_seq_1 = loc_seq
        comm_seq_2 = orient_seq
    else:
        comm_seq_1 = orient_seq 
        comm_seq_2 = loc_seq
    start_seqs = list(direct_routes(start_pos, comm_seq_1[0]))
    mid_seqs = list(direct_routes(comm_seq_1[-1], comm_seq_2[0]))
    end_seqs = list(direct_routes(comm_seq_2[-1], end_pos))
    if verbose:
        print("loc_seq")
        for pos in loc_seq:
            print(pos)
        print()
        print("orient_seq")
        for pos in orient_seq:
            print(pos)
    # Build all possible ext_trajectories from the seperate building
    # blocks.
    for start_seq in start_seqs:
        for mid_seq in mid_seqs: 
            for end_seq in end_seqs:
                if comm_seq_1[-1] == comm_seq_2[0]:
                    # To avoid artificial "pauze" (= repetition of the
                    # same location), leave out the end or start of
                    # some of the building blocks.
                    # Case: communicative sequences share end and start
                    # of their sequences.
                    yield (
                        start_seq[:-1] + comm_seq_1 + comm_seq_2[1:] + 
                        end_seq[1:]
                    )
                    # Case: no overlap between start and end of 
                    # communicative sequences.
                else:    
                    yield (
                        start_seq[:-1] + comm_seq_1 + mid_seq[1:-1] + 
                        comm_seq_2 + end_seq[1:]
                    )

operators = get_all_operators()

if __name__ == "__main__": 

    loc1 = Loc(0, 0)
    orient1 = Orient(1)
    pos1 = Position(loc1, orient1)
    pos2 = pos1.move("up")
    pos3 = pos2.move("right")
    pos4 = pos3.turn("clock")
    pos5 = pos4.turn("clock")
    pos6 = pos5.move("right")
    pos7 = pos6.move("up")

    s_lang = Language(operators, operators, verbose=False)
    print(
        "location-opr:", s_lang.loc_opr, "\t"
        "orientation-opr:", s_lang.orient_opr, "\n")
    print("loc opr vals:", s_lang.loc_opr.vals, "\n")
    print("orient opr vals:", s_lang.orient_opr.vals, "\n")
    print(s_lang.signal_order, "\n")

    print("pos1\t", pos1, "\n") 
    print("pos3\t", pos3, "\n")
    print("pos7\t", pos7, "\n")

    for i in list(ext_trajects(s_lang, pos3, (pos1, pos7))):
        print("ext_traject")
        for j in i:
            print(j)
        print()
