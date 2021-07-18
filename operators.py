"""
This file is part of tcg.
"""
from collections import namedtuple
from copy import deepcopy
from itertools import chain
import gc

Operator = namedtuple("Operator", "name func_vars pos_vals vals func")
"""Create Operator object: Object(name, vars, pos_vals, func)

At a high level, an operator is a conceptual building block,
used to build communicative signals, according to certain
principle or strategy.
A collection of operators forms a so called "Language of Thought",
which can form the basis for language to communicate goals in the 
tcg.

Args for Operator object: 
    name: A string.
    func_vars: A tuple. The variable names of the operator func.
        Variable "dirc_place_holder" is used for the uniformity of
        how the function can be called.
        For all operator functions the first two variables are 
        position and direction/orientation (they are seen as 
        equivalent). When the operator is not dependent on the 
        direction/orientation then the direction variable is called
        a place holder.
    pos_vals: A dict. Keys: the variable names of the operator 
        function. Values: the possible values for the variables.
    vals: A dict. Keys: the variable names of the operator 
        function. Values: The actual values of the variables 
        (choosen from the possible values). They are set when the 
        operator is used in a language.
        TODO: do we want to use several of the same operators, 
        with different value settings, at the same time?
    func: A function. When calling an operator function (by name) 
        within a language object (see language.py), the first two 
        variables are 'called by' pos and pos.orient.val,
        and the rest is 'called by' taken the rest of the variables 
        and looking up their value in the vals dict:
        name(
            pos, pos.orient.val, 
            *[name.vals[var] for var in name.vars[2:]
        )
"""

# The name of an operator can be used to call it's function.
Operator.__call__ = lambda self, *args: self.func(*args)
# Print only the name of an operator.
Operator.__repr__ = lambda self: self.name
Operator.__str__ = lambda self: self.name

# Pauze operator: Stay at the same location.
pauze = Operator(
    # Name.
    "pauze", 
    # Func_vars.
    ("position", "dirc_place_holder", "duration"),  
    # Pos_vals.
    # The possible values of the variables.
    {"duration": [1, 2]}, 
    # Vals.
    {"duration": None},
    # Func.
    lambda pos, dirc, dur: [deepcopy(pos) for _ in range(dur + 1)]
)

# Wiggle operator: move back and forth between a base location,
# and an adjacent location (or a location adjacent to that adjacent
# location).
# TODO make wiggle dependent on width
wiggle = Operator(
    # Name.
    "wiggle",
    # Func_vars.
    ("position", "direction", "width", "repetition"),
    # Pos_vals.
    {
        "direction": ["up", "right", "down", "left"],
        "width": [1, 2],
        "repetition": [1, 2]
    },
    # Vals.
    # TODO: just use empty dict instead?
    {"width": None, "repetition": None},
    # Func.
    lambda pos, dirc, width, rep: \
        [deepcopy(pos), pos.move(dirc), deepcopy(pos)] + list(
            chain.from_iterable(
                [(pos.move(dirc), deepcopy(pos)) for _ in range(rep - 1)]
            )
        )
)   

def get_all_operators():
    """Return a list of all Operator objects created so far."""
    return [
        opr for opr in gc.get_objects() if isinstance(opr, Operator)
    ]
