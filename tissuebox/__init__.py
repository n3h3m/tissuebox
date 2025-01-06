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


def check_required_fields(schema, payload, errors, path=""):
    """Check if all required fields are present in payload"""
    if isinstance(schema, dict):
        if "*" in schema:
            return

        for k, v in schema.items():
            new_path = f"{path}['{k}']" if path else f"['{k}']"

            if k.startswith("[") and k.endswith("]"):
                # Handle array notation
                array_key = k[1:-1]
                if array_key not in payload:
                    errors.append(f"{new_path} is required")
                elif isinstance(payload[array_key], list):
                    for i, item in enumerate(payload[array_key]):
                        array_path = f"{path}['{array_key}'][{i}]"
                        if isinstance(v, list):
                            check_required_fields(v[0], item, errors, array_path)
                        else:
                            # For dot notation arrays that haven't been normalized yet
                            field_schema = {"dummy": v}
                            check_required_fields(field_schema, {"dummy": item}, errors, array_path)
            elif k not in payload:
                errors.append(f"{new_path} is required")
            elif isinstance(v, (dict, list)):
                check_required_fields(v, payload[k], errors, new_path)

    elif isinstance(schema, list) and len(schema) > 0:
        if not isinstance(payload, list):
            return
        for i, item in enumerate(payload):
            check_required_fields(schema[0], item, errors, f"{path}[{i}]")


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

        # First pass: Check for array vs dict conflicts
        array_keys = set()
        dict_keys = set()

        for k in schema.keys():
            if "." not in k:
                continue

            parts = k.split(".")
            base_key = parts[0]

            if base_key.startswith("[") and base_key.endswith("]"):
                array_keys.add(base_key[1:-1])  # Remove brackets
            else:
                dict_keys.add(base_key)
                # Also check if any part of the path is using array notation
                for part in parts[1:]:
                    if part.startswith("[") and part.endswith("]"):
                        array_keys.add(part[1:-1])

        # Check for conflicts
        conflicts = array_keys.intersection(dict_keys)
        if conflicts:
            raise SchemaError("Ambiguous schema: '{}' is used both as array and dict pattern".format(list(conflicts)[0]))

        # Second pass: Group fields by their root array
        array_groups = {}
        regular_fields = {}

        for k, v in list(schema.items()):
            if "." not in k:
                regular_fields[k] = v
                continue

            parts = k.split(".")
            if parts[0].startswith("["):
                root_array = parts[0][1:-1]
                if root_array not in array_groups:
                    array_groups[root_array] = {}
                array_groups[root_array][k] = v
            else:
                regular_fields[k] = v
            del schema[k]

        # Add back regular fields
        schema.update(regular_fields)

        # Third pass: Process each array group
        for array_key, fields in array_groups.items():
            array_schema = {}

            # Group fields by their nested structure
            for field_path, value in fields.items():
                parts = field_path.split(".")
                # Skip the root array part
                parts = parts[1:]

                current = array_schema
                for i, part in enumerate(parts):
                    if part.startswith("["):
                        # Handle nested array
                        array_name = part[1:-1]
                        if array_name not in current:
                            current[array_name] = [{}]
                        if i == len(parts) - 1:
                            # This shouldn't happen - arrays should have fields
                            continue
                        current = current[array_name][0]
                    else:
                        if i == len(parts) - 1:
                            # Last part is the field name
                            current[part] = value
                        else:
                            if part not in current:
                                current[part] = {}
                            current = current[part]

            schema[array_key] = [array_schema]

        # Process remaining dot notation fields
        for k in list(schema.keys()):
            if "." not in k:
                continue

            parts = k.split(".")
            try:
                current = schema
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = schema[k]
                del schema[k]
            except TypeError:
                raise SchemaError("Can't normalise {} as it conflicts with existing structure".format(k))

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


def validate(schema, payload, errors=None, field_path=None):
    if errors is None:
        errors = []
    if field_path is None:
        field_path = []

    if not is_valid_schema(schema):
        raise SchemaError("Schema is invalid, Use SchemaInspector to debug the schema")

    normalise(schema)

    # Check required fields first
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
                    errors.append("['{}']{}".format(key, e))
            sort_unique(errors)
            return not errors

        for k in schema:
            if type(k) is str:
                if k not in payload:
                    continue
                E = []
                new_path = field_path + [k]
                validate(schema[k], payload.get(k), E, new_path)
                for e in E:
                    errors.append("['{}']{}".format(k, e))

    elif type(schema) is list:
        if type(payload) is not list:
            errors.append("{} must be list".format(payload))
            return False

        if len(schema) > 1:
            schema = [set(schema)]

        for i, p in enumerate(payload):
            E = []
            new_path = field_path + [str(i)]
            validate(schema[0], p, E, new_path)
            for e in E:
                errors.append("[{}]{}".format(i, e))
        return not errors

    elif type(schema) is set:
        schema = list(schema)
        if not any([validate(s, payload, field_path=field_path) for s in schema]):
            if len(schema) > 1:
                labels = sorted([msg(s) for s in schema])
                errors.append(" must be either {} or {} (but {})".format(", ".join(labels[:-1]), labels[-1], payload))
            else:
                errors.append("{} must be {}".format(payload, msg(schema[0])))

    elif type(schema) is tuple:
        all_valid = True
        for s in schema:
            if not validate(s, payload, field_path=field_path):
                errors.append("{} must be {}".format(payload, msg(s)))
                all_valid = False
        return all_valid

    else:
        if schema in primitives:
            schema = primitives[schema]

        result = False
        if callable(schema):
            # Get the current field name from the path
            current_field = field_path[-1] if field_path else None
            result = schema(payload, field=current_field)
        elif is_primitive_value(schema):
            result = schema == payload

        if not result:
            errors.append(" must be {} (but {})".format(msg(schema), decorate(payload)))

    sort_unique(errors)
    return not errors
