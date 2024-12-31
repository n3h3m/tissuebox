import re


def exists(d, attrs):
    try:
        for at in attrs:
            d = d[at]
        return True
    except (KeyError, TypeError):
        return False


def sattr(d, *attrs):
    try:
        for attr in attrs[:-2]:
            if type(d.get(attr)) is not dict:
                d[attr] = {}
                # raise Exception("Overriding Attempt")
            d = d[attr]
        d[attrs[-2]] = attrs[-1]
    except IndexError:
        print()


def kgattr(d, sofar, *attrs):
    # gattr but very strict, tries to go nested, upon KeyError return the sofar list.
    for at in attrs:
        sofar.append(at)
        d = d[at]


def regex_in(r, l):
    return bool(list(filter(re.compile(r).match, l)))
