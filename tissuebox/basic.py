# Checks if the input is an int, bool is not allowed
import re
from decimal import Decimal


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


def complex_number(x):
    return type(x) is complex


complex_number.msg = "complex number"


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


def uuid4(x):
    if not isinstance(x, str):
        return False
    # https://stackoverflow.com/a/18359032/968442
    regex = re.compile("^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z", re.I)
    return bool(regex.match(x))


uuid4.msg = "a valid uuid"


def email(x):
    if not isinstance(x, str):
        return False
    # https://emailregex.com/
    return bool(re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", x))


email.msg = "a valid email"


def url(x):
    if not isinstance(x, str):
        return False
    # https://stackoverflow.com/a/17773849/968442
    return bool(
        re.match(
            r"(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9]\.[^\s]{2,})",
            x,
        )
    )


url.msg = "a valid url"


def lt(n):
    def lt(x):
        return x < n

    lt.msg = f"less than {n}"
    return lt


def divisible(n):
    def divisible(x):
        return numeric(x) and numeric(n) and x % n == 0

    divisible.msg = f"multiple of {n}"
    return divisible


def strong_password(min_len=8):
    """
    Returns a validator function that checks if a password is strong enough.
    Requirements:
    - At least minlength characters long (default 8)
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one number
    - Contains at least one special character
    """

    def f(x):
        if not isinstance(x, str):
            return False

        if len(x) < min_len:
            return False

        has_upper = any(c.isupper() for c in x)
        has_lower = any(c.islower() for c in x)
        has_digit = any(c.isdigit() for c in x)
        has_special = any(not c.isalnum() for c in x)

        return has_upper and has_lower and has_digit and has_special

    # Set message for error reporting
    f.msg = f"a strong password (min {min_len} chars with uppercase, lowercase, number, and special character)"

    return f
