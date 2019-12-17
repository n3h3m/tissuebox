from tissuebox.basic import array, boolean, complex_number, dictionary, integer, null, numeric, string
from tissuebox.helpers import exists, kgattr, sattr


class SchemaError(BaseException):
    pass


def sort_unique(l):
    l[:] = sorted(set(l))


def normalise(schema, start=None):
    if start is None:
        start = []
    """
    Normalises a dot separated schema into nested schema.

    Possible areas where dicts are possible
        - A dict can be self
        - A dict can be value of few other keys
        - A dict can be an elements of an array where that array is a value of other keys
        - A dict can be part of tuple, where that tuple can be part of another list

    Pretty much think of going after all the complex syntax where any dict-tissue is possible
    """

    if type(schema) in [list, tuple, set]:
        for s in schema:
            normalise(s, start + [s])

    if type(schema) is dict:
        for k in schema:
            normalise(schema[k], start + [k])

        for k in list(schema.keys()):
            if '.' not in k:
                continue

            splitted = k.split('.')
            sofar = []
            sch = schema

            try:
                for s in splitted:
                    sch = sch[s]
                    sofar.append(s)
                # A successful completion means discrepancy
                splitted.append(schema[k])
                sofar.append(sch)
                raise SchemaError("Can't normalise {} as it would override {}".format(start + splitted, start + sofar))
            except TypeError:
                sofar.append(sch)
                raise SchemaError("Can't normalise {} as it conflicts with {}".format(start + splitted, start + sofar))
            except KeyError:
                # A good case requires KeyError
                splitted.append(schema[k])
                sattr(schema, *splitted)
                del schema[k]

        if '*' in schema and len(schema) > 1:
            raise SchemaError("Can't normalise {} as it contains more elements{} than expected".format(start + ['*'], schema.keys()))

# def dot_to_dict(schema):
#     # Converts a dot separated schema into nested schema
#     if type(schema) is not dict:
#         return
#
#     dot_found = False
#     for k in schema:
#         if '.' in k:
#             dot_found = True
#             break
#     if dot_found:
#         splitted = k.split('.')
#         head, tail = '.'.join(splitted[:-1]), splitted[-1]
#
#         if not schema.get(head):
#             schema[head] = {}
#         schema[head].update({tail: schema[k]})
#         del schema[k]
#
#         if '*' in schema[head] and len(schema[head]) > 1:
#             other_keys = [head + '.' + _k for _k in schema[head] if _k is not '*']
#             raise SchemaError('Discrepancy in array declaration, `{}` conflicts with other keys {}'.format(k, other_keys))
#             print()
#
#         dot_to_dict(schema)
#     return

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


def decorate(payload):
    # Decorate the payload, i.e if string add quotations, if list add brackets
    if type(payload) is str:
        return "'{}'".format(payload)
    return payload


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

    normalise(schema)
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

    if type(schema) is dict:
        if type(payload) is not dict:
            errors.append("must be dict")
            return
        for k in schema:
            if type(k) is str:  # At the moment we only support string keys for dicts # Todo
                if k not in payload:
                    continue
                E = []
                validate(schema[k], payload.get(k), E)
                for e in E:
                    errors.append("['{}']{}".format(k, e))
                    # errors.append("ᚏ['{}']{} but received {}".format(k, e.replace(re.findall(r'\(.*?)\', e)[0], '').replace('', ''), payload[k]))  # Handle this tidying up text later
        sort_unique(errors)

    elif schema == '*':
        print()

    elif type(schema) is list:
        # If schema is list then payload also must be list, otherwise immediately append error and return
        if type(payload) is not list:
            errors.append("{} must be list".format(payload))
            return

        if len(schema) > 1:
            schema = [set(schema)]

        for i, p in enumerate(payload):
            E = []
            validate(schema[0], p, E)
            for e in E:
                errors.append('[{}]{}'.format(i, e))

    elif type(schema) is set:
        schema = list(schema)
        if not any([validate(s, payload) for s in schema]):
            if len(schema) > 1:
                labels = sorted([msg(s) for s in schema])
                errors.append(" must be either {} or {} (but {})".format(', '.join(labels[:-1]), labels[-1], payload))
            else:
                errors.append("{} must be {}".format(payload, msg(schema[0])))

        sort_unique(errors)
        return not errors

    elif type(schema) is tuple:
        for s in schema:
            if not validate(s, payload):
                errors.append("{} must be {}".format(payload, msg(s)))
        sort_unique(errors)
        return not errors

    else:
        if schema in primitives:
            schema = primitives[schema]

        if callable(schema):
            result = schema(payload)

        if primitive(schema):
            result = schema == payload

        if not result:
            errors.append(" must be {} (but {})".format(msg(schema), decorate(payload)))

    sort_unique(errors)
    return not errors
