from pprint import pprint

from tissuebox.basic import between, boolean, integer, primitive, required, rfc_datetime, string
from tissuebox.helpers import gattr, kgattr, ngattr, subscripts
from tissuebox.scrap import payload, schema

class SchemaError(BaseException):
    pass

def _tupled_schema(schema):
    new = dict()
    for key in schema.keys():

        # Transition function uses (tuple) style
        if isinstance(key, tuple):
            if not len(key) == 2:
                raise SchemaError('`{}` Transition function tuple requires exactly two elements'.format(key))
            if not callable(key[0]):
                raise SchemaError('`{}` Transition function must be callable'.format(key))
            left = (key[0], tuple(key[1].split('.')))
            new[left] = schema[key]
            continue

        left = tuple(key.split('.'))
        new[left] = schema[key]

    return new

def _expand_schema(schema, payload):
    new = dict()
    to_remove = []

    for key in schema.keys():
        tab = fab = key  # Don't get overwhelmed by the tab-fab nightmare, fab handles the tuple formation of (callable(key[0]), key[1])
        if callable(key[0]):
            tab = key[1]
            fab = (key[0], key[1])

        for i in range(len(tab)):
            got = ngattr(payload, *tab[:i])
            if isinstance(got, list):
                for j in range(len(got)):
                    p = got[j]
                    s = {tab[i:]: schema[fab]}
                    e = _expand_schema(s, p)

                    for _key in e.keys():
                        if callable(key[0]):
                            left = (key[0], tab[:i] + (j,) + _key)
                            new[left] = schema[fab]
                        else:
                            left = tab[:i] + (j,) + _key
                            new[left] = schema[tab]
                to_remove.append(fab)
                break
        new[fab] = schema[fab]

    for tr in to_remove:
        new.pop(tr)

    return new

def _validate_element(payload, key, value, errors):
    subs = subscripts(key)
    sofar = []

    try:

        if value is required:
            kgattr(payload, sofar, *key)
            return

        if callable(key[0]):
            # Here key[0] is a translation function on the python side, ideally things like `len`, `sum` etc
            elem = key[0](gattr(payload, *key[1]))
            subs = "{}({})".format(key[0].__name__, subscripts(key[1]))
        else:
            elem = gattr(payload, *key)
    except (KeyError, TypeError):
        if value is required:
            errors.append(subscripts(sofar) + ' is required')
        return  # We only care about elements that are resolving properly, else simply continuing

    # Handle primitive
    if primitive(value):
        if elem != value:
            errors.append("{} is not equal to `{}`".format(subs, value))
        return

    # Handle enum
    if isinstance(value, set):
        if isinstance(elem, dict) or elem not in value:
            errors.append("{} is failing to be enum of `{}`".format(subs, value))
        return

    # Handle parameterized function
    if isinstance(value, tuple):
        if not value[0](elem, *value[1:]):  # Here value[0] is the type function and rest of the tuple is it's params
            errors.append("{} is failing to be `{}{}`".format(subs, value[0].__name__, value[1:]))
        return

    # At last validate the type_function
    if not value(elem):  # value is the type_function here.
        errors.append("{} is failing to be `{}`".format(subs, value.__name__))

    return

def _validate_element_schema(value, errors, subs):
    if isinstance(value, dict):
        errors.append("In {} nested schema for Tissuebox isn't implemented yet. Try installing the latest version".format(subs))
        return

    if isinstance(value, set):
        if not value:
            errors.append("In {} tries to define an enum but definition is empty.".format(subs))
        return

    if isinstance(value, tuple):
        if not value:
            errors.append("In {} received an empty tuple".format(subs))
            return
        if not callable(value[0]):
            errors.append("In {} a valid type_function is required.".format(subs))
        return

    if not callable(value) and not primitive(value):
        errors.append("In {} the type_function is not callable".format(subs))
        return

def _validate_schema(schema):
    errors = []

    for key in schema.keys():
        value = schema[key]
        subs = subscripts(key)

        if isinstance(value, list):
            for v in value:
                _validate_element_schema(v, errors, subs)
        else:
            _validate_element_schema(value, errors, subs)

    return not errors, errors

def validate(schema, payload=None):
    errors = []
    schema = _tupled_schema(schema)

    result, details = _validate_schema(schema)  # First validate the schema itself.
    if not result:
        raise SchemaError(details)

    schema = _expand_schema(schema, payload)

    for key in schema.keys():
        value = schema[key]
        if isinstance(value, list):
            for v in value:
                _validate_element(payload, key, v, errors)
        else:
            _validate_element(payload, key, value, errors)

    errors = sorted(set(errors))
    return not errors, errors

if __name__ == '__main__':
    pprint(validate(schema, payload))
