from z3 import *


class Expr:
    def __add__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            other = Con(other)

        if isinstance(other, str):
            other = Var(other)
            
        if isinstance(other, Expr):
            return Plus(self, other)

        print(f"Non-matching types for +: {type(self)} and {type(other)}")
        return None

    def __mul__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            other = Con(other)

        if isinstance(other, str):
            other = Var(other)
            
        if isinstance(other, Expr):
            return Times(self, other)

        print(f"Non-matching types for +: {type(self)} and {type(other)}")
        return None

    def __sub__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            other = Con(other)

        if isinstance(other, str):
            other = Var(other)

        if isinstance(other, Expr):
            return Minus(self, other)

        print(f"Non-matching types for +: {type(self)} and {type(other)}")
        return None

    
class Con(Expr):
    #  constant
    def __init__(self, val: float):
        self.val = val

    def ev(self, env={}):
        return self.val

    def __str__(self):
        return str(self.val)

    def __eq__(self, other):
        if isinstance(other, Con):
            return self.val == other.val

        return False

    def vars(self):
        return []

    def toZ3(self):
        #  return val attribute directly as val is expected in z3 form
        return self.val


class Var(Expr):
    #  variable
    def __init__(self, name: str):
        self.name = name

    def ev(self, env={}):
        return env[self.name]

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, Var):
            return self.name == other.name

        return False

    def vars(self):
        return [self.name]

    def toZ3(self):
        #  returns an integer variable in z3 format
        return Int(f"{self.name}")


class BinOp(Expr):
    def __init__(self, left: Expr, right: Expr):
        self.left = left
        self.right = right

    def ev(self, env={}):
        return self.op(self.left.ev(env), self.right.ev(env))

    def __str__(self):
        return f"({self.left} {self.name} {self.right})"

    def __eq__(self, other):
        if isinstance(other, BinOp) and self.name == other.name:
            return self.left == other.left and self.right == other.right

        return False

    def vars(self):
        return self.left.vars() + self.right.vars()

    def toZ3(self):
        #  pass, because it depends on what left and right is.
        pass


class Plus(BinOp):

    name = '+'

    def op(self, x, y):
        return x + y

    def toZ3(self):
        #  return z3 expression representing addition operation of left and right side of the operation.
        return self.left.toZ3() + self.right.toZ3()

    
class Times(BinOp):

    name = '*'
    
    def op(self, x, y):
        return x * y

    def toZ3(self):
        #  return z3 expression representing multiplication operation of left and right side of the operation.
        return self.left.toZ3() * self.right.toZ3()
    

class Minus(BinOp):

    name = '-'

    def op(self, x, y):
        return x - y

    def toZ3(self):
        #  return z3 expression representing subtraction operation of left and right side of the operation.
        return self.left.toZ3() - self.right.toZ3()


class Equals(BinOp):
    
    name = '='

    def op(self, x, y):
        return x == y

    def toZ3(self):
        # returns a Z3 expression representing the equality operation between the left and right sides of the
        # operation.
        return self.left.toZ3() == self.right.toZ3()


class BOr(BinOp):

    name = 'or'

    def op(self, x, y):
        return x or y

    def toZ3(self):
        # returns a Z3 expression representing the boolean "or" operation between the left and right sides of the
        # operation.
        return Or(self.left.toZ3(), self.right.toZ3())


class BAnd(BinOp):

    name = 'and'

    def op(self, x, y):
        return x and y

    def toZ3(self):
        # returns a Z3 expression representing the boolean "and" operation between the left and right sides of the
        # operation.
        return And(self.left.toZ3(), self.right.toZ3())


class Greater(BinOp):

    name = '>'

    def op(self, x, y):
        return x > y

    def toZ3(self):
        # returns a Z3 expression representing the greater than operation between the left and right sides of the
        # operation.
        return self.left.toZ3() > self.right.toZ3()


class Lesser(BinOp):

    name = '<'

    def op(self, x, y):
        return x < y

    def toZ3(self):
        # returns a Z3 expression representing the lesser than operation between the left and right sides of the
        # operation.
        return self.left.toZ3() < self.right.toZ3()
