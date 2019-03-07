from decimal import Decimal

from tissuebox.basic import array, boolean, dictionary, integer, null, numeric, string
from tissuebox.helpers import memoize

class SchemaError(BaseException):
    pass

primitives_as_string = {
    int: 'integer',
    str: 'string',
    bool: 'boolean',
    float: 'numeric',
    list: 'array',
    dict: dictionary,
    None: 'null',
    Decimal: 'numeric'
}

primitives = {
    int: integer,
    str: string,
    bool: boolean,
    float: numeric,
    list: array,
    dict: dictionary,
    None: null,
}

def valid_schema(schema):
    global primitives, primitives_as_string
    if isinstance(schema, list):
        return all([valid_schema(s) for s in schema])  # If schema is list of schemas, UC#3

    if schema in primitives:
        schema = primitives[schema]

    if not callable(schema):
        return False

    if not getattr(schema, 'msg'):
        return False

    return True

def validate(schema, payload, errors=None):
    if errors is None:
        errors = []

    global primitives, primitives_as_string
    """
    Schema can be a primitives or a tissue
    e.g:
    int --> 1,2,3,4,5
    float --> 1.5, 4 etc
    list --> [], [1,2,4], ["hello", "world"], [1,"hello"]
    dict --> All valid dicts
    bool --> True or False
    None --> Value must be equal to None
    tissue --> Value must be something that is compliant to the said tissuebox schema

    Schema can be list of primitives
    e.g:
    [int] --> [1,2,3,4]
    [str] --> ["Hello", "World"]
    [int, str] --> A list with mixed types, but only int or string allowed. [1, "hello"]
    [tissue] --> Value must be an array, And all array elements must be tissue compliant
    which meets tissue schema
    """
    if not valid_schema(schema):
        raise SchemaError("Schema is invalid, Use SchemaInspector to debug the schema")

    if type(schema) is list:
        # If schema is list then payload also must be list, otherwise immediately append error
        if type(payload) is not list:
            errors.append(f"{payload} must be list")
            return

        # All the elements of payload must fulfill any of an item in schema list
        # i.e for the schema [int, str] a valid payload would be [1, 'hello', 3]

        for p in payload:
            if not any([validate(s, p) for s in schema]):
                if len(schema) > 1:
                    errors.append(f"{p} must be either {', '.join([primitives_as_string[s] for s in schema[:-1]])+' or '+primitives_as_string[schema[-1]]}")
                else:
                    errors.append(f"{p} must be {primitives_as_string[schema[0]]}")
    else:
        schema = primitives[schema]
        result = schema(payload)
        if not result:
            errors.append(f"`{payload}` must be {schema.msg}")

    errors = sorted(set(errors))
    return not errors
