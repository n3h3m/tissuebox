from tissuebox.basic import array, boolean, complex_number, dictionary, integer, null, numeric, string
from tissuebox.helpers import exists, kgattr, sattr


class SchemaError(BaseException):
    pass


def sort_unique(l):
    l[:] = sorted(set(l))


def normalise(schema, start=None):
    if start is None:
        start = []

    if type(schema) in [list, tuple, set]:
        for s in schema:
            normalise(s, start + [s])

    if type(schema) is dict:
        # First check for "*" with other keys
        if "*" in schema and len(schema) > 1:
            raise SchemaError(
                "Can't normalise {} as it contains more keys {} than expected".format(start + ["*"], [k for k in schema.keys() if k != "*"])
            )

        # Normalize all values
        for k in schema:
            normalise(schema[k], start + [k])

        # Handle dot notation
        for k in list(schema.keys()):
            if "." not in k:
                continue

            splitted = k.split(".")
            sofar = []
            sch = schema

            try:
                for s in splitted:
                    sch = sch[s]
                    sofar.append(s)
                splitted.append(schema[k])
                raise SchemaError("Can't normalise {} as it would override {}".format(start + splitted, start + sofar))
            except TypeError:
                sofar.append(sch)
                raise SchemaError("Can't normalise {} as it conflicts with {}".format(start + splitted, start + sofar))
            except KeyError:
                splitted.append(schema[k])
                sattr(schema, *splitted)
                del schema[k]


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
    complex: complex_number,
}


def decorate(payload):
    # Decorate the payload, i.e if string add quotations, if list add brackets
    if type(payload) is str:
        return "'{}'".format(payload)
    return payload


def msg(schema):
    # Returns human-friendly validation error message for schema type using .msg attribute (e.g. "must be integer", "must be null", etc.)
    if schema is None:
        return "null"
    if is_primitive_value(schema):
        return str(schema)
    if is_primitive_type(schema):
        schema = primitives[schema]
    return schema.msg


def is_primitive_value(schema):
    global primitives
    return type(schema) in primitives


def is_primitive_type(schema):
    global primitives
    return schema in primitives


def is_valid_schema(schema):
    global primitives

    # Handle collections
    if type(schema) in (set, list, tuple):
        return all([is_valid_schema(s) for s in schema])

    # Handle dictionaries
    if type(schema) is dict:
        # If dict has "*", it should be the only key
        if "*" in schema and len(schema) > 1:
            return False
        # Recursively validate all values in dict
        return all(is_valid_schema(v) for v in schema.values())

    # Handle primitives and tissue functions
    if type(schema) in primitives:
        return True

    if schema in primitives:
        return True

    if callable(schema) and getattr(schema, "msg", None):
        return True

    return False


def validate(schema, payload, errors=None):
    if errors is None:
        errors = []

    if not is_valid_schema(schema):
        raise SchemaError("Schema is invalid, Use SchemaInspector to debug the schema")

    normalise(schema)

    if type(schema) is dict:
        if type(payload) is not dict:
            errors.append("must be dict")
            return False

        # Handle wildcard schema
        if "*" in schema:
            wildcard_schema = schema["*"]
            for key, value in payload.items():
                E = []
                validate(wildcard_schema, value, E)
                for e in E:
                    errors.append("['{}']{}".format(key, e))
            sort_unique(errors)
            return not errors

        # Handle normal dict schema
        for k in schema:
            if type(k) is str:
                if k not in payload:
                    continue
                E = []
                validate(schema[k], payload.get(k), E)
                for e in E:
                    errors.append("['{}']{}".format(k, e))
        sort_unique(errors)
        return not errors

    elif type(schema) is list:
        if type(payload) is not list:
            errors.append("{} must be list".format(payload))
            return False

        if len(schema) > 1:
            schema = [set(schema)]

        for i, p in enumerate(payload):
            E = []
            validate(schema[0], p, E)
            for e in E:
                errors.append("[{}]{}".format(i, e))
        return not errors

    elif type(schema) is set:
        schema = list(schema)
        if not any([validate(s, payload) for s in schema]):
            if len(schema) > 1:
                labels = sorted([msg(s) for s in schema])
                errors.append(" must be either {} or {} (but {})".format(", ".join(labels[:-1]), labels[-1], payload))
            else:
                errors.append("{} must be {}".format(payload, msg(schema[0])))
        sort_unique(errors)
        return not errors

    elif type(schema) is tuple:
        all_valid = True
        for s in schema:
            if not validate(s, payload):
                errors.append("{} must be {}".format(payload, msg(s)))
                all_valid = False
        sort_unique(errors)
        return all_valid

    else:
        if schema in primitives:
            schema = primitives[schema]

        result = False
        if callable(schema):
            result = schema(payload)
        elif is_primitive_value(schema):
            result = schema == payload

        if not result:
            errors.append(" must be {} (but {})".format(msg(schema), decorate(payload)))

    sort_unique(errors)
    return not errors
