import re
from decimal import Decimal


def integer(x, field=None):
    if isinstance(x, bool):
        return False
    return isinstance(x, int)


integer.msg = "integer"


def numeric(x, field=None):
    if isinstance(x, bool):
        return False
    return isinstance(x, int) or isinstance(x, float) or isinstance(x, Decimal)


numeric.msg = "numeric"


def complex_number(x, field=None):
    return type(x) is complex


complex_number.msg = "complex number"


def string(x, field=None):
    return isinstance(x, str)


string.msg = "string"


def array(x, field=None):
    return isinstance(x, list)


array.msg = "list"


def dictionary(x, field=None):
    return isinstance(x, dict)


dictionary.msg = "dictionary"


def boolean(x, field=None):
    return isinstance(x, bool)


boolean.msg = "boolean"


def null(x, field=None):
    return x is None


null.msg = "null"


def uuid4(x, field=None):
    if not isinstance(x, str):
        return False
    regex = re.compile("^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z", re.I)
    return bool(regex.match(x))


uuid4.msg = "a valid uuid"


def email(x, field=None):
    if not isinstance(x, str):
        return False
    return bool(re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", x))


email.msg = "a valid email"


def url(x, field=None):
    if not isinstance(x, str):
        return False
    return bool(
        re.match(
            r"(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9]\.[^\s]{2,})",
            x,
        )
    )


url.msg = "a valid url"


def lt(n):
    def lt(x, field=None):
        return x < n

    lt.msg = f"less than {n}"
    return lt


def gt(n):
    def gt(x, field=None):
        return x > n

    gt.msg = f"greater than {n}"
    return gt


def divisible(n):
    def divisible(x, field=None):
        return numeric(x) and numeric(n) and x % n == 0

    divisible.msg = f"multiple of {n}"
    return divisible


def strong_password(min_len=8):
    def f(x, field=None):
        if not isinstance(x, str):
            return False

        if len(x) < min_len:
            return False

        has_upper = any(c.isupper() for c in x)
        has_lower = any(c.islower() for c in x)
        has_digit = any(c.isdigit() for c in x)
        has_special = any(not c.isalnum() for c in x)

        return has_upper and has_lower and has_digit and has_special

    f.msg = f"a strong password (min {min_len} chars with uppercase, lowercase, number, and special character)"
    return f
