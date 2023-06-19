# define the result and rest functions
result = lambda p: p[0][0]
rest   = lambda p: p[0][1]
# the base paraser function
class Parser:
    def __rshift__(self, other):
        return Seq(self, other)

    def __xor__(self, other):
        return OrElse(self, other)
    
    def parse(self, inp):
        return self.parser.parse(inp)

    def cons(x, xs):
        if type(x) == str and xs == []:
            return x
        if type(xs) == str:
            return x + xs
        return [x] + xs


########################################
# Core combinators:                    #
# they override the function "parse".  #
########################################

class Seq(Parser): # used to add multiple parsers in sequence
    def __init__(self, parser, and_then):
        self.parser   = parser
        self.and_then = and_then

    def parse(self, inp):
        p = self.parser.parse(inp)
        if p != []:
            return self.and_then(result(p)).parse(rest(p))

        return []
    
class OrElse(Parser): # used to allow an alternative parser in case one fails
    def __init__(self, parser1, parser2):
        self.parser1 = parser1
        self.parser2 = parser2

    def parse(self, inp):
        p = self.parser1.parse(inp)
        if p != []:
            return p
        return self.parser2.parse(inp)

class ParseItem(Parser): # parses a single item
    def parse(self, inp):
        if inp == "":
            return []
        return [(inp[0], inp[1:])]
    
class Return(Parser): # returns the item and the rest
    def __init__(self, x):
        self.x = x
        
    def parse(self, inp):
        return [(self.x, inp)]

class Fail(Parser): # returns nothing
    def parse(self, inp):
        return []

########################################
# Generic combinators:                 #
# they combine the core functions      #
########################################
class ParseSome(Parser): # allows you to parse multiple times using the same parser
    def __init__(self, parser):                         
        self.parser = parser >> (lambda x: \
                                 (ParseSome(parser) ^ Return([])) >> (lambda xs: \
                                 Return(Parser.cons(x, xs))))
class ParseIf(Parser): # allows you to only parse if a certain condition is met
    def __init__(self, pred):
        self.pred   = pred
        self.parser = ParseItem() >> (lambda c: \
                                      Return(c) if self.pred(c) else Fail())

class ParseChar(Parser): # parses a single charachter
    def __init__(self, c):
        self.parser = ParseIf(lambda x: c == x)

class ParseDigit(Parser):# parses a single digit
    def __init__(self):
        self.parser = ParseIf(lambda c: c in "0123456789")
