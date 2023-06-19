from baseparser import *
from classesimport import *

# the basic parsers needed to parse Variables or constants

class ParseNat(Parser):
    def __init__(self):
        """
        the parser for a natural number
        it parses an amount of digits and returns the digits as an int
        """
        self.parser = ParseSome(ParseDigit()) >> (lambda ds:Return(int(ds)))


class ParseInt(Parser):
    def __init__(self): 
        """
        the parser for integers
        it does this by trying to parse a - and then a natural number and return that as a Con class object
        If that doesn't work, then just return the number as a Con class object
        """
        self.parser = (ParseChar('-') >> (lambda _:ParseNat() >> (lambda n:Return(Con(-n))))) ^\
                      (ParseNat() >> (lambda n: Return(Con(n))))


class ParseAlph(Parser):
    def __init__(self):
        """
        the parser for single alphabetical letters
        it simply checks if the parsed item is in the list of all alphabetical charachters
        """
        self.parser = ParseIf(lambda c: c in "abcdefghijklmnopqrstuvwxyz")


class ParseVar(Parser):
    def __init__(self):
        """
        the parser for variables
        it does this by trying to parse a - and then an Alphabetical charachter and return that as a Times(Con(-1),Var(str(n)))
            This means it returns the Variable times -1. This was done since I found no other way to make it clear that this variable is negative
        If that doesn't work, then just return the letter as a Var class object
        """
        self.parser = (ParseChar('-') >> (lambda _:ParseAlph() >> (lambda n:Return(Times(Con(-1),Var(str(n))))))) ^\
                      (ParseAlph() >> (lambda n: Return(Var(n))))

# the parsers for parsing an expression

class ParseExprPart(Parser):
    def __init__(self):
        """
        the parser for a base part of an expression
        A base part of an expression is either a variable, a constant, or an expression surrounded by brackets
        an expression surrounded by brackets counts a smallest part, since it has to be able to be inserted anywhere,
            regardless of the normal oder of operations
        """
        self.parser = ParseVar() ^\
                      ParseInt() ^\
                      (ParseChar('(') >> (lambda _: ParseExpr() >> (lambda parens: ParseChar(')') >> (lambda _: Return(parens)))))


class ParseExpr(Parser): # the main function for parsing expressions
    def __init__(self):
        """
        The basic class used to parse Expressions.
        This class only adds minus, since that is the weakest operation
        It is also recursive on the right, this makes it right associative for any minus operations
        If there is no minus in the expression, then it checks the next operation, plus.
        """
        self.parser = (ParseExprPlus() >> (lambda a: ParseChar('-') >> (lambda _: ParseExpr() >> (lambda b: Return(Minus(a, b)))))) ^ \
                      ParseExprPlus()


class ParseExprPlus(Parser):
    def __init__(self):
        """
        The second class used to parse Expressions.
        This class only adds plus, the second strongest operation
        It is also recursive on the right, this makes it right associative for any plus operations
        If there is no plus in the expression, then it checks the next operation, times.
        """
        self.parser = (ParseExprTimes() >> (lambda a: ParseChar('+') >> (lambda _: ParseExprPlus() >> (lambda b: Return(Plus(a, b)))))) ^ \
                      ParseExprTimes()


class ParseExprTimes(Parser):
    def __init__(self):
        """
        The third class used to parse Expressions.
        This class only adds times, the strongest operation
        It is also recursive on the right, this makes it right associative for any times operations
        If there is no plus in the expression, then it checks the basepart.
        """
        self.parser = (ParseExprPart() >> (lambda a: ParseChar('*') >> (lambda _: ParseExprTimes() >> (lambda b: Return(Times(a, b)))))) ^\
                      ParseExprPart()

# the parser used to parse equations
class ParseEquation(Parser):
    def __init__(self):
        """
        The class used to parse Equations.
        It simply checks that there is an expression on both sides of the = sign and returns both expressions in an Equals class
        """
        self.parser = (ParseExpr() >> (lambda a: ParseChar('=') >> (lambda _: ParseExpr() >> (lambda b: Return(Equals(a, b))))))

# the parsers used for parsing constraints
class ParseAnd(Parser):
    def __init__(self):
        """
        This class parses the word "and"
        it simply checks if the letters exist in that order, and fails if not
        """
        self.parser = (ParseChar('a') >> (lambda _: ParseChar('n') >> (lambda _: ParseChar('d'))))


class ParseOr(Parser):
    def __init__(self):
        """
        This class parses the word "or"
        it simply checks if the letters exist in that order, and fails if not
        """
        self.parser = (ParseChar('o') >> (lambda _: ParseChar('r')))


class ParseConstrPart(Parser):
    def __init__(self):
        """
        the parser for a base part of a constraint
        A base part of a constraint is either an expression > another expression,
            an expression < another expression, or a constraint surrounded by brackets
        a contraint surrounded by brackets counts a smallest part, since it has to be able to be inserted anywhere,
            regardless of the normal oder of operations
        """
        self.parser = (ParseExpr() >> (lambda a: ParseChar('>') >> (lambda _: ParseExpr() >> (lambda b: Return(Greater(a, b)))))) ^ \
                      (ParseExpr() >> (lambda a: ParseChar('<') >> (lambda _: ParseExpr() >> (lambda b: Return(Lesser(a, b)))))) ^\
                      (ParseChar('(') >> (lambda _: ParseConstr() >> (lambda parens: ParseChar(')') >> (lambda _: Return(parens)))))

class ParseConstr(Parser): # the main parser for constraints
    def __init__(self):
        """
        The basic class used to parse contraints.
        This class only adds or, since that is weaker than or
        It is also recursive on the right, this makes it right associative for any or operations
        If there is no or in the constraint, then it checks if there is an and.
        """
        self.parser = (ParseConstrAnd() >> (lambda a: ParseOr() >> (lambda _: ParseConstr() >> (lambda b: Return(BOr(a, b)))))) ^ \
                      ParseConstrAnd()
        
class ParseConstrAnd(Parser):
    def __init__(self):
        """
        The second class used to parse contraints.
        This class adds and
        It is also recursive on the right, this makes it right associative for any and operations
        If there is no and in the constraint, then it checks for a base part.
        """
        self.parser = (ParseConstrPart() >> (lambda a: ParseAnd() >> (lambda _: ParseConstrAnd() >> (lambda b: Return(BAnd(a, b)))))) ^ \
                      ParseConstrPart()




# the function that reads a file and applies the parser to it
def ParseFile(name):
    """
    This function takes the name of file, and returns a list equations and a list of constraints in one list.
    [list_of_equations,list_of_constraints]
    testing it with example1.txt,
    we would expect:
    
    >>> print(ParseFile("example1.txt")[0][0])
    ((x + (y + z)) = 10)
    >>> print(ParseFile("example1.txt")[0][1])
    ((x - z) = 5)
    >>> print(ParseFile("example1.txt")[1][0])
    ((x > 5) or ((x < z) and (y > 0)))
    >>> print(ParseFile("example1.txt")[1][1])
    (z < 0)
    """
    with open(name) as file:
        data = file.read()
    data = "".join(data.split())
    equations = []
    constraints = []
    if "suchthat" in data:
        # Remove the "Solve" at the start of the sentence
        data = data[5:-1].split("suchthat")
        equations = data[0].split(",")
        constraints = data[1].split(",")
    else:
        data = data[5:-1]
        equations = data.split(",")

    equations_parsed = []
    constraints_parsed = []
    for eq in equations:
        parsedeq = ParseEquation().parse(eq)[0]
        if parsedeq[1] == "":
            equations_parsed.append(parsedeq[0])
        else:
            raise SyntaxError("Error while parsing the Equations")
    for cons in constraints:
        parsedcons = ParseConstr().parse(cons)[0]
        if parsedcons[1] == "":
            constraints_parsed.append(parsedcons[0])
        else:
            raise SyntaxError("Error while parsing the Constraints")
    return (equations_parsed, constraints_parsed)
