import Projectparser
from z3 import *


def solve(input):
    """
    >>> print(solve('example1.txt'))
    No solution!
    """
    s = Solver()
    eq, constr = Projectparser.ParseFile(input)
    equations = [x.toZ3() for x in eq]
    constrains = [y.toZ3() for y in constr]
    conditions = equations + constrains
    for x in conditions:
        s.add(x)
    if s.check() == sat:
        ans = str(s.model())
        ansStr = ans[1:-1]  # remove the square brackets from the string
        ansLst = ansStr.split(", ")  # split the string into a list of strings, where each string represents a single
        # variable-value pair.
        ansSet = set()  # new empty set
        ansSet.update(ansLst)
        return ansSet
    else:
        return "No solution!"


sol = solve('example1.txt')
print(sol)
