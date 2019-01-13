from tissuebox.basic import _integer

def subscripts(X):
    # Receives an iterable and returns the string of array subscripts
    ret = ''
    for x in X:
        if _integer(x):
            ret += '[{}]'.format(x)
        else:
            ret += '["{}"]'.format(x)
    return ret

def ngattr(d, *attrs):
    try:
        for at in attrs:
            d = d[at]
        return d
    except (KeyError, TypeError):
        return None

def kgattr(d, sofar, *attrs):
    # gattr but very strict, tries to go nested, upon KeyError return the sofar list.
    for at in attrs:
        sofar.append(at)
        d = d[at]

def gattr(d, *attrs):
    for at in attrs:
        d = d[at]
    return d

def lgattr(d, *attrs):
    try:
        for at in attrs:
            d = d[at]
        return d
    except KeyError:
        return []

def sattr(d, *attrs):
    try:
        for attr in attrs[:-2]:
            # If such key is not found or the value is primitive supply an empty dict
            if d.get(attr) is None or not isinstance(d.get(attr), dict):
                d[attr] = {}
            d = d[attr]
        d[attrs[-2]] = attrs[-1]
    except IndexError:
        print()

def appendr(d, *attrs):
    if not lgattr(d, attrs[:-1]):
        sattr(d, *attrs[:-1], [])
    lgattr(d, *attrs[:-1]).append(attrs[-1])
