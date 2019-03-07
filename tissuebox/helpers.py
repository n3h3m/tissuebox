import jsonpickle

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

def memoize(f):
    memo = {}

    def inner(*args, **kwargs):
        s = jsonpickle.dumps(args) + jsonpickle.dumps(kwargs)
        if not s in memo:
            memo[s] = f(*args, **kwargs)
        return memo[s]

    return inner
