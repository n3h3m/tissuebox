from tissuebox.basic import array, boolean, complex_number, dictionary, integer, null, numeric, string
from tissuebox.helpers import memoize

class SchemaError(BaseException):
    pass

primitives = {
    int: integer,
    str: string,
    bool: boolean,
    float: numeric,
    list: array,
    set: array,
    tuple: array,
    dict: dictionary,
    None: null,
    complex: complex_number
}

def msg(schema):
    if schema is None:
        return 'null'
    if primitive(schema):
        return str(schema)
    if primitive_type(schema):
        schema = primitives[schema]
    return schema.msg

def primitive(schema):
    global primitives
    return type(schema) in primitives

def primitive_type(schema):
    global primitives
    return schema in primitives

def valid_schema(schema):
    global primitives
    if type(schema) in (set, list, tuple):
        return all([valid_schema(s) for s in schema])

    if type(schema) in primitives:
        return True

    if schema in primitives:
        return True

    if callable(schema) and getattr(schema, 'msg', None):
        return True

    return False

def validate(schema, payload, errors=None):
    if errors is None:
        errors = []

    global primitives
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
    
    Schema can be tissues or list of tissues, list of mixed privitives and tissues
    e.g
    email -> 'hello@world.com'
    url -> 'www.duck.com'
    [email] --> ['hello@world.com, world@hello.com']
    [url, email] --> ['www.duck.com', 'hello@world.com, world@hello.com']
    """
    if not valid_schema(schema):
        raise SchemaError("Schema is invalid, Use SchemaInspector to debug the schema")

    if type(schema) is list:
        # If schema is list then payload also must be list, otherwise immediately append error and return
        if type(payload) is not list:
            errors.append(f"`{payload}` must be list")
            return

        if len(schema) > 1:
            schema = [set(schema)]

        for p in payload:
            validate(schema[0], p, errors)

    else:
        if type(schema) is set:
            schema = list(schema)
            if not any([validate(s, payload) for s in schema]):
                if len(schema) > 1:
                    errors.append(f"`{payload}` must be either {', '.join([msg(s) for s in schema[:-1]])} or {msg(schema[-1])}")
                else:
                    errors.append(f"`{payload}` must be {msg(schema[0])}")

            errors = sorted(set(errors))
            return not errors

        if schema in primitives:
            schema = primitives[schema]

        if callable(schema):
            result = schema(payload)

        if primitive(schema):
            result = schema == payload

        if not result:
            errors.append(f"`{payload}` must be {msg(schema)}")

    errors = sorted(set(errors))
    return not errors

assert validate([{1, 2}], [1, 2, 2, 2, 1, 1, 1])
