from decimal import Decimal

# Checks if the input is an int, bool is not allowed
def integer(x):
    if isinstance(x, bool):
        return False
    return isinstance(x, int)

integer.msg = "integer"

# Checks if the input is int, float or Decimal, bool is not allowed
def numeric(x):
    if isinstance(x, bool):
        return False
    return isinstance(x, int) or isinstance(x, float) or isinstance(x, Decimal)

numeric.msg = "numeric"

def string(x):
    return isinstance(x, str)

string.msg = "string"

def array(x):
    return isinstance(x, list)

array.msg = "list"

def dictionary(x):
    return isinstance(x, dict)

dictionary.msg = "dictionary"

def boolean(x):
    return isinstance(x, bool)

boolean.msg = "boolean"

def null(x):
    return x is None

null.msg = "null"

def lt(n):
    def lt(x):
        lt.msg = "less than {}".format(n)
        return x < n

    return lt
