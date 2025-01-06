from tissuebox.basic import array, boolean, complex_number, dictionary, integer, null, numeric, string
from tissuebox.helpers import exists, kgattr, sattr


class SchemaError(BaseException):
    pass


def sort_unique(l):
    l[:] = sorted(set(l))


def get_required_fields(schema):
    """Extract all required fields from a schema"""
    required_fields = []

    def extract_fields(s, prefix=""):
        if isinstance(s, dict):
            for k, v in s.items():
                if k == "*":
                    continue
                new_prefix = f"{prefix}['{k}']" if prefix else f"['{k}']"
                if isinstance(v, (dict, list)):
                    extract_fields(v, new_prefix)
                else:
                    required_fields.append(new_prefix)
        elif isinstance(s, list) and len(s) > 0:
            extract_fields(s[0], prefix)

    extract_fields(schema)
    return required_fields


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
    if type(payload) is str:
        return "'{}'".format(payload)
    return payload


def msg(schema):
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

    if type(schema) in (set, list, tuple):
        return all([is_valid_schema(s) for s in schema])

    if type(schema) is dict:
        if "*" in schema and len(schema) > 1:
            return False
        return all(is_valid_schema(v) for v in schema.values())

    if type(schema) in primitives:
        return True

    if schema in primitives:
        return True

    if callable(schema) and getattr(schema, "msg", None):
        return True

    return False


def normalise(schema, start=None):
    """Normalize schema, treating array notation fields as required."""
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

        # First pass: Check for array vs dict conflicts
        array_keys = set()
        dict_keys = set()

        for k in schema.keys():
            if "." not in k:
                # Direct array notation check
                if k.startswith("[") and k.endswith("]"):
                    array_keys.add(k[1:-1])
                continue

            parts = k.split(".")
            base_key = parts[0]

            if base_key.startswith("[") and base_key.endswith("]"):
                array_keys.add(base_key[1:-1])
            else:
                dict_keys.add(base_key)
                # Check for array notation in subsequent parts
                for part in parts[1:]:
                    if part.startswith("[") and part.endswith("]"):
                        array_keys.add(part[1:-1])

        # Check for conflicts
        conflicts = array_keys.intersection(dict_keys)
        if conflicts:
            raise SchemaError("Ambiguous schema: '{}' is used both as array and dict pattern".format(list(conflicts)[0]))

        # Second pass: Process fields
        for k in list(schema.keys()):
            if "." not in k:
                # Handle direct array notation
                if k.startswith("[") and k.endswith("]"):
                    array_key = k[1:-1]
                    array_schema = schema[k]
                    del schema[k]
                    if array_key not in schema:
                        schema[array_key] = [{}]
                    if isinstance(array_schema, dict):
                        schema[array_key][0].update(array_schema)
                    else:
                        schema[array_key][0] = array_schema
                continue

            parts = k.split(".")
            current = schema
            path = []

            for i, part in enumerate(parts[:-1]):
                if part.startswith("[") and part.endswith("]"):
                    array_key = part[1:-1]
                    if array_key not in current:
                        current[array_key] = [{}]
                    current = current[array_key][0]
                else:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                path.append(part)

            last_part = parts[-1]
            if last_part.startswith("[") and last_part.endswith("]"):
                array_key = last_part[1:-1]
                if array_key not in current:
                    current[array_key] = [{}]
                current[array_key][0] = schema[k]
            else:
                current[last_part] = schema[k]
            del schema[k]

    return schema


def validate(schema, payload, errors=None, field_path=None):
    if errors is None:
        errors = []
    if field_path is None:
        field_path = []

    if not is_valid_schema(schema):
        raise SchemaError("Schema is invalid, Use SchemaInspector to debug the schema")

    # Only normalize if schema is a dict
    if isinstance(schema, dict):
        schema = normalise(schema.copy())
        check_required_fields(schema, payload, errors)

    if type(schema) is dict:
        if type(payload) is not dict:
            errors.append("must be dict")
            return False

        if "*" in schema:
            wildcard_schema = schema["*"]
            for key, value in payload.items():
                E = []
                new_path = field_path + [key]
                validate(wildcard_schema, value, E, new_path)
                for e in E:
                    errors.append("['{}'] {}".format(key, e))
            sort_unique(errors)
            return not errors

        for k in schema:
            if type(k) is str:
                if k not in payload:
                    continue
                E = []
                new_path = field_path + [k]
                validate(schema[k], payload[k], E, new_path)
                for e in E:
                    errors.append("['{}'] {}".format(k, e))

    elif type(schema) is list:
        if type(payload) is not list:
            errors.append("must be list")
            return False

        if len(schema) > 1:
            schema = [set(schema)]

        for i, p in enumerate(payload):
            E = []
            new_path = field_path + [str(i)]
            validate(schema[0], p, E, new_path)
            for e in E:
                errors.append("[{}] {}".format(i, e))

    elif type(schema) is tuple:
        all_valid = True
        tuple_errors = []
        for s in schema:
            E = []
            if not validate(s, payload, E, field_path):
                tuple_errors.extend(E)
                all_valid = False
        if not all_valid:
            errors.extend(tuple_errors)

    elif type(schema) is set:
        if not any([validate(s, payload, field_path=field_path) for s in schema]):
            labels = sorted([msg(s) for s in schema])
            if len(schema) > 1:
                errors.append(" must be either {} or {} (but {})".format(", ".join(labels[:-1]), labels[-1], payload))
            else:
                errors.append(" must be {} (but {})".format(labels[0], payload))

    else:
        if schema in primitives:
            schema = primitives[schema]

        result = False
        if callable(schema):
            current_field = field_path[-1] if field_path else None
            result = schema(payload, field=current_field)
        elif is_primitive_value(schema):
            result = schema == payload

        if not result:
            # Use natural language format only for direct literal validation
            if field_path is None and is_primitive_value(payload) and is_primitive_value(schema):
                errors.append("{} is not {}".format(decorate(payload), msg(schema)))
            else:
                errors.append("must be {} (but {})".format(msg(schema), decorate(payload)))

    sort_unique(errors)
    return not errors


def check_required_fields(schema, payload, errors, path=""):
    """Check if all required fields are present in payload"""
    if isinstance(schema, dict):
        if "*" in schema:
            return

        for k, v in schema.items():
            new_path = f"{path}['{k}']" if path else f"['{k}']"

            # Only check if field exists, don't validate type here
            if k not in payload:
                errors.append(f"{new_path} is required")
            elif isinstance(v, dict):
                check_required_fields(v, payload[k], errors, new_path)
            elif isinstance(v, list) and isinstance(payload[k], list):
                for i, item in enumerate(payload[k]):
                    check_required_fields(v[0], item, errors, f"{new_path}[{i}]")


def not_(validator):
    def not_(x, field=None):
        return not validate(validator, x, field_path=[field] if field else None)

    not_.msg = f"not {msg(validator)}"
    return not_
