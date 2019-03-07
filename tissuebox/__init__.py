from tissuebox.basic import array, boolean, dictionary, integer, null, numeric, string
from tissuebox.helpers import memoize

class SchemaError(BaseException):
    pass

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
    global primitives
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
        # If schema is list then payload also must be list, otherwise immediately append error
        if type(payload) is not list:
            errors.append(f"`{payload}` must be list")
            return

        schema = [primitives[s] if s in primitives else s for s in schema]

        # All the elements of payload must fulfill any of an item in schema list
        # i.e for the schema [int, str] a valid payload would be [1, 'hello', 3]

        for p in payload:
            if not any([validate(s, p) for s in schema]):
                if len(schema) > 1:
                    errors.append(f"`{p}` must be either {', '.join([s.msg for s in schema[:-1]])+' or '+schema[-1].msg}")
                else:
                    errors.append(f"`{p}` must be {schema[0].msg}")
    else:
        if schema in primitives:
            schema = primitives[schema]
        result = schema(payload)
        if not result:
            errors.append(f"`{payload}` must be {schema.msg}")

    errors = sorted(set(errors))
    return not errors
