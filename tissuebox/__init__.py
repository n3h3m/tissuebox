class PV_RuleError(BaseException):
    pass

def integer(x):
    if isinstance(x, bool):
        return False
    return isinstance(x, int)

def negative_integer(x):
    return integer(x) and x < 0

def positive_integer(x):
    return integer(x) and x > 0

def whole_number(x):
    return integer(x) and x >= 0

def decimal(x):
    return isinstance(x, float)

def numeric(x):
    return integer(x) or decimal(x)

def negative(x):
    return numeric(x) and x < 0

def positive(x):
    return numeric(x) and x > 0

def string(x):
    return isinstance(x, str)

def email(x):
    # https://emailregex.com/
    import re
    return bool(re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", x))

def url(x):
    # https://stackoverflow.com/a/17773849/968442
    import re
    return bool(re.match(r"(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9]\.[^\s]{2,})", x))

def dictionary(x):
    return isinstance(x, dict)

def array(x):
    return isinstance(x, list)

def typed_array(array, type_function):
    return all([type_function(item) for item in array])

def boolean(x):
    return isinstance(x, bool)

def null(x):
    return x is None

def nested_get(d, attrs):
    for at in attrs:
        d = d[at.strip()]
    return d

def nested_get_quite(d, *attrs):
    """
    Similar to nested_get, but swallows the KeyError exception, Instead returns an empty iterable
    :param d:
    :param attrs:
    :return:
    """
    try:
        for at in attrs:
            d = d[at]
        return d
    except KeyError:
        return ''

def validate(schema, payload):
    """
    Receives a schema and validates against the payload

    :param schema:
    :param payload:
    :return: Tuple of (bool, list)
    """

    details = []

    # Initial sanity checks
    for key in schema.keys():
        if key not in ['required', 'types']:
            raise PV_RuleError

    # Process `exist` option
    for item in nested_get_quite(schema, 'required'):
        if '||' in item:
            found = False
            sub_items = item.strip().split('||')
            for si in sub_items:
                try:
                    nested_get(payload, si.strip().split('.'))
                    found = True
                except KeyError:
                    continue
            if not found:
                details.append("`exist` condition is failing for `{}`".format(item))

            continue

        try:
            nested_get(payload, item.strip().split('.'))
        except KeyError:
            details.append("`exist` condition is failing for `{}`".format(item))

    # Process `types` part
    for key, value in nested_get_quite(schema, 'types').items():
        try:
            elem = nested_get(payload, key.strip().split('.'))
        except KeyError:
            continue  # Simply continue, we only validate data types for values that are found in the payload.

        if isinstance(value, list):
            if not len(value) == 1:
                raise PV_RuleError
            if not typed_array(elem, value[0]):
                details.append("`types` condition is failing for `{}`".format(key))
            continue

        if isinstance(value, tuple):
            if not value:
                raise PV_RuleError
            if not elem in value:
                details.append("Enum tuple is failing for `{}`. Double check the schema".format(key))
            continue

        if not value(elem):
            details.append("`types` condition is failing for `{}`".format(key))

    return not details, details
