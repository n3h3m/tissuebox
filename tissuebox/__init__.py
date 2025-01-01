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
        if "*" in schema and len(schema) > 1:
            raise SchemaError(
                "Can't normalise {} as it contains more keys {} than expected".format(start + ["*"], [k for k in schema.keys() if k != "*"])
            )

        # Track array vs dict keys
        array_keys = set()
        dict_keys = set()

        # First detect any conflicts
        for k in schema.keys():
            if "." not in k:
                continue

            parts = k.split(".")
            base_key = parts[0]

            if base_key.startswith("[") and base_key.endswith("]"):
                array_keys.add(base_key[1:-1])  # Remove brackets
            else:
                dict_keys.add(base_key)

        # Check for conflicts
        conflicts = array_keys.intersection(dict_keys)
        if conflicts:
            raise SchemaError("Ambiguous schema: '{}' is used both as array and dict pattern".format(list(conflicts)[0]))

        # First pass - identify array patterns and group their fields
        array_fields = {}  # Will store array_key -> fields mapping

        for k in list(schema.keys()):
            if "." not in k:
                continue

            parts = k.split(".")
            if not parts[0].startswith("["):
                # Handle regular dot notation
                try:
                    sch = schema
                    sofar = []
                    for s in parts[:-1]:
                        if s in sch:
                            sch = sch[s]
                        else:
                            sch[s] = {}
                            sch = sch[s]
                        sofar.append(s)
                    sch[parts[-1]] = schema[k]
                    del schema[k]
                except TypeError:
                    raise SchemaError("Can't normalise {} as it conflicts with existing structure".format(k))
                continue

            # Get the first array key
            array_key = parts[0][1:-1]  # Remove brackets

            if array_key not in array_fields:
                array_fields[array_key] = {}

            # Remove the first array part and store remaining path
            remaining_path = ".".join(parts[1:])
            array_fields[array_key][remaining_path] = schema[k]
            del schema[k]

        # Second pass - process each array pattern
        for array_key, fields in array_fields.items():
            if array_key not in schema:
                schema[array_key] = [{}]

            # Group nested array fields
            nested_arrays = {}
            regular_fields = {}

            for field_path, value in fields.items():
                if "." not in field_path:
                    regular_fields[field_path] = value
                    continue

                parts = field_path.split(".")
                if parts[0].startswith("["):
                    nested_key = parts[0][1:-1]
                    if nested_key not in nested_arrays:
                        nested_arrays[nested_key] = {}
                    nested_arrays[nested_key][".".join(parts[1:])] = value
                else:
                    regular_fields[field_path] = value

            # Add regular fields to array schema
            for field, value in regular_fields.items():
                if "." in field:
                    parts = field.split(".")
                    current = schema[array_key][0]
                    for part in parts[:-1]:
                        if part not in current:
                            current[part] = {}
                        current = current[part]
                    current[parts[-1]] = value
                else:
                    schema[array_key][0][field] = value

            # Process nested arrays recursively
            for nested_key, nested_fields in nested_arrays.items():
                nested_schema = {"[" + nested_key + "]." + k: v for k, v in nested_fields.items()}
                normalised = normalise(nested_schema)
                schema[array_key][0].update(normalised)

    return schema


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
