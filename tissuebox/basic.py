import re

def rfc_datetime(x):
    return bool(re.match(r'([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})(\.([0-9]+))?(Z|([+-][0-9]{2}):([0-9]{2}))', x)), "a valid RFC datetime"

def numeric_string(x):
    try:
        float(x)
        return True, ''
    except ValueError:
        return False, "a string of numeric which can be parsed"

def geolocation(x):
    try:
        if len(x) != 2:
            return False
        return -90 <= x[0] <= 90 and -180 <= x[1] <= 180, "valid pair of geolocation coordinates"
    except TypeError:
        return False

def integer_string(x):
    try:
        int(x)
        return True, ''
    except ValueError:
        return False, "a string of integer which can be parsed"

def integer(x):
    if isinstance(x, bool):
        return False, "an integer, but received a boolean"
    return isinstance(x, int), "an integer literal"

def _integer(x):
    if isinstance(x, bool):
        return False
    return isinstance(x, int)

def _decimal(x):
    return isinstance(x, float)

def decimal(x):
    return isinstance(x, float), "float"

def numeric(x):
    return _integer(x) or _decimal(x), "numeric i.e integer or float"

def string(x):
    return isinstance(x, str), "a string"

def uuid4(x):
    # https://stackoverflow.com/a/18359032/968442
    regex = re.compile('^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z', re.I)
    return bool(regex.match(x)), "a valid uuid4"

def email(x):
    # https://emailregex.com/
    return bool(re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", x)), "a valid email"

def url(x):
    # https://stackoverflow.com/a/17773849/968442
    return bool(re.match(r"(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9]\.[^\s]{2,})", x)), "a valid url"

def array(x):
    return isinstance(x, list), "a list"

def dictionary(x):
    return isinstance(x, dict), "a dictionary"

def boolean(x):
    return isinstance(x, bool), "boolean"

def null(x):
    return x is None, "null"

def _primitive(x):
    return type(x) in (int, float, bool, str)

def primitive(x):
    return type(x) in (int, float, bool, str), "a python primitive (int, float, bool, str)"

def denied():
    # Dummy function, doesn't do anything, but don't delete
    pass

def allowed():
    # Dummy function, doesn't do anything, but don't delete
    pass

def required():
    # Dummy function, doesn't do anything, but don't delete
    pass

def negative_integer(x):
    return integer(x) and x < 0, "a negative integer"

def positive_integer(x):
    return integer(x) and x > 0, "a positive integer"

def whole_number(x):
    return integer(x) and x >= 0, "a whole number i.e integer greater than or equal to 0"

def negative(x):
    return numeric(x) and x < 0, "less than 0"

def positive(x):
    return numeric(x) and x > 0, "greater than 0"

# Functions that accept parameters. Define them as higher order functions.
def between(a, b, inclusive=True):
    def between(x):
        try:
            if inclusive:
                return a <= x <= b, "between {} & {} inclusively".format(a, b)
            return a < x < b, "between {} & {} strictly".format(a, b)
        except TypeError:
            return False, "comparable with {} & {}".format(a, b)

    return between

def divisible(n):
    def divisible(x):
        return numeric(x) and numeric(n) and x % n == 0, "multiple of {}".format(n)

    return divisible

def gt(n):
    def gt(x):
        return x > n, "greater than {}".format(n)

    return gt

def gte(n):
    def gte(x):
        return x >= n, "greater than or equal to {}".format(n)

    return gte

def lte(n):
    def lte(x):
        return x <= n, "less than or equal to {}".format(n)

    return lte

def lt(n):
    def lt(x):
        return x < n, "less than {}".format(n)

    return lt
