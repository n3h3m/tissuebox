import re

def rfc_datetime(x):
    return bool(re.match(r'([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})(\.([0-9]+))?(Z|([+-][0-9]{2}):([0-9]{2}))', x))

def numeric_string(x):
    try:
        float(x)
        return True
    except ValueError:
        return False

def geolocation(x):
    try:
        if len(x) != 2:
            return False
        return -90 <= x[0] <= 90 and -180 <= x[1] <= 180
    except TypeError:
        return False

def integer_string(x):
    try:
        int(x)
        return True
    except ValueError:
        return False

def integer(x):
    if isinstance(x, bool):
        return False
    return isinstance(x, int)

def between(x, a, b, inclusive=True):
    try:
        if inclusive:
            return a <= x <= b
        return a < x < b
    except TypeError:
        return False

def decimal(x):
    return isinstance(x, float)

def numeric(x):
    return integer(x) or decimal(x)

def string(x):
    return isinstance(x, str)

def uuid4(x):
    # https://stackoverflow.com/a/18359032/968442
    regex = re.compile('^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z', re.I)
    return bool(regex.match(x))

def email(x):
    # https://emailregex.com/
    return bool(re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", x))

def url(x):
    # https://stackoverflow.com/a/17773849/968442
    return bool(re.match(r"(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9]\.[^\s]{2,})", x))

def array(X, t=None):  # t is a type_function here.
    if t:
        return all([t(x) for x in X])
    return isinstance(X, list)

def dictionary(x):
    return isinstance(x, dict)

def boolean(x):
    return isinstance(x, bool)

def null(x):
    return x is None

def primitive(x):
    return type(x) in (int, float, bool, str)

def required():
    # Dummy function, doesn't do anything
    pass

def lte(x, n):
    return x <= n

def lt(x, n):
    return x < n

def gte(x, n):
    return x >= n

def gt(x, n):
    return x > n

def divisible(x, n):
    return numeric(x) and numeric(n) and x % n == 0

def negative_integer(x):
    return integer(x) and x < 0

def positive_integer(x):
    return integer(x) and x > 0

def whole_number(x):
    return integer(x) and x >= 0

def negative(x):
    return numeric(x) and x < 0

def positive(x):
    return numeric(x) and x > 0
