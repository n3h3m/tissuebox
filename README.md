![tissuebox.png](tissuebox.png)

## Tissuebox
Tissuebox is a pure Pythonic schema validator which takes advantage of Python's functional style programming to provide simple yet powerful validation framework. The standard usage would be validating incoming JSON objects upon http requests or to validate any Python dict in other common scenarios.

#### Installation:
Use `pip` to install Tissuebox

`pip install tissuebox`

#### Requirements:
Tissuebox requires Python 3.7 however we are considering to add support for earlier versions of Python3

#### Examples:

Assume the incoming JSON object or a python dict which contains hotel details and we will build upon this example.

```python
payload = {
    "name": "Park Shereton",
    "available": True,
    "price_per_night": 270,
    "email": "contact@shereton.com",
    "web": "www.shereton.com",
}
```

   
#### 1. Validating basic data types

You can use `tissuebox` to define a schema to validate the payload against basic data types and validate using `validate` method.

```python
from tissuebox import validate
from tissuebox.basic import boolean, integer, string

schema = {
    'name': string,
    'available': boolean,
    'price_per_night': integer
}

validate(schema, payload)

```
will return 
```python
(True, [])
```

#### 2. Validating common datatypes

A `tissuebox` schema is simply a dict where keys are payload keys and values are type_functions to which the payload value would be passed. A type_function simply accepts a single parameter and returns a tuple with two items `(boolean, msg)`.

Tissuebox aims to amass a collection of commonly used types to it's library. For now common data types like `email`, `url`, `rfc_datetime`, `geolocation` are part of `tissuebox`'s standard collections. You can contribute more via Github.

```python
from tissuebox import validate
from tissuebox.basic import email, integer, string, url
schema = {
    'name': string,
    'price_per_night': integer,
    "email": email,
    "web": url
}

validate(schema, payload)
```
will return
```python
(True, [])
```
    
One of the ways `tissuebox` stands our from other alternatives is, the type_functions are stored and passed around as Python variables which is helpful in identifying the schema definition errors ahead of time as most IDEs will display squiggly lines if the variables aren't resolved, while other frameworks like JsonSchema and Cerebrus pass types within strings which is hard for IDEs to detect errors in the schema.

#### 3. Validating nested fields

##### Method 1:

Defining a schema in a nested fashion is very straight forward which enables re-use schemas around. Consider if the payload has an `address` field. We can define a separate schema as `address_schema` and pass it to the main schema as below. 

```python
from tissuebox import validate
from tissuebox.basic import email, integer, string, url
payload = {
    "name": "Park Shereton",
    "available": True,
    "price_per_night": 270,
    "email": "contact@shereton.com",
    "web": "www.shereton.com",
    "address": {
        "street": "128 George St",
        "city": "Sydney",
        "state": "NSW",
        "zip": 2000
    }
}

address = {
    "street": string,
    "city": string,
    "state": string,
    "zip": integer
}

schema = {
    'name': string,
    'price_per_night': integer,
    "email": email,
    "web": url,
    "address": address
}

validate(schema, payload)
```
would return
```python
(True, [])
```

##### Method 2:

The prefered method of defining nested schema is by using `.` dot as delimiter to represent nested fields of the payload hierarchy. Apparently this comes up with the downside wherein if `.` dot itself is part of keys which would be an unfortunate scenario. But it can improve the readability to a tremendous level. See it yourself how elegantly we can express the schema once we introduce the `address` field to our payload. 

```python
schema = {
    'name': string,
    'price_per_night': integer,
    "email": email,
    "web": url,
    "address.street": string,
    "address.city": string,
    "address.state": string,
    "address.zip": integer
}
```

The primary reason why we suggest the later method is we can quickly define a nested field with any depth without creating unnecessary schema objects in the middle. 
    
#### 4. Validating enums. 

Let us try enforcing that the field `address.state` must be one of 8 Australian states. Tissuebox let's you define an enum using the `{}` i.e `set()` syntax. Look at the example below. 

```python
schema = {
    'name': string,
    'price_per_night': integer,
    "email": email,
    "web": url,
    "address.state": {'ACT', 'NSW', 'NT', 'QLD', 'SA', 'TAS', 'VIC', 'WA'},
    "address.zip": integer
}
```

To have a feel how Tissuebox responds when we pass something which is not an Australian state

```python
payload = {
    "name": "Park Shereton",
    "available": True,
    "price_per_night": 270,
    "email": "contact@shereton.com",
    "web": "www.shereton.com",
    "address": {
        "street": "128 George St",
        "city": "Sydney",
        "state": "TX",
        "zip": 2000
    }
}

validate(schema, hotel)
```
would return 
```python
(False, ['["address"]["state"] is failing to be enum of `{\'SA\', \'QLD\', \'NT\', \'TAS\', \'VIC\', \'WA\', \'ACT\', \'NSW\'}`'])
```

#### 5. Validating arrays

Let us assume the payload has `staffs` which is array of staff names.

```python
payload = {
    "name": "Park Shereton",
    "email": "contact@shereton.com",
    "web": "www.shereton.com",
    "staffs" ["John Doe", "Jane Smith"],
}
```

Now the schema simple looks as below

```python
schema = {
    'name': string,
    "email": email,
    "web": url,
    "staffs": [string]
}
```

So in order to declare an element as array simply use `[]` syntax, if it's array of string simply say `[string]`. If it's array of cats simply say `[cat]`. Array syntax can be either empty or single length where the element means a type_function or another nested schema.

There are two scenarios where Tissuebox implicitly handles the array.

1. The incoming payload is simply list of dicts then Tissuebox knows that the given schema must be validated against all the items in the array.
2. While declaring `.` dot separated nested attribute, and any of the middle element is array, Tissuebox is aware of such fact and will iterate the validation automatically.

These two cases are implemented to make Tissuebox as intuitive as possible,

#### 6. Writing custom validators
    
By now you would have observed that `tissuebox` schema is simply a collection of `key:value` pairs where `value` contains the data type verified against. `tissuebox` defines them in the style of `type_function` which is simply a boolean function that takes one or more parameters. 

Let us assume you want to validate the zip code as a valid Australian one. Since `tissuebox` does't have a built-in type function, for that purpose you can come up with your own type function as below. For brevity I've removed few fields in the payload & schema.

```python
>>> def australian_zip(x):
...     # https://www.etl-tools.com/regular-expressions/is-australian-post-code.html
...     x = str(x)
...     import re
...     return re.match(r'^(0[289][0-9]{2})|([1345689][0-9]{3})|(2[0-8][0-9]{2})|(290[0-9])|(291[0-4])|(7[0-4][0-9]{2})|(7[8-9][0-9]{2})$', x), "must be a valida Australian zip"
...
>>> hotel = {
...     "address": {
...         "zip": 200
...     }
... }
>>>
>>> schema = {
...     "address.zip": australian_zip
... }
>>>
>>> validate(schema, hotel)
(False, ['["address"]["zip"] must be a valida Australian zip"])
```
    
#### 7. Validating with type_functions that accept parameters.

In `tissuebox` type_functions always accept one argument which is the payload value. There are times for a type_function it makes sense to accepts multiple parameters. To achieve that they are declared as Python's higher order functions.

Let us try validating where the `price_per_night` must be multiple of 50. Also let us declare the Yelp review rating of a hotel must be between 1-5.

```python
>>> from tissuebox import validate
>>> from tissuebox.basic import between, divisible, string

>>> schema = {
...     "name": string,
...     "rating": between(1, 5),
...     "price_per_night": divisible(50)
... }
>>>
>>> hotel = {
...     "name": "Park Shereton",
...     "price_per_night": 370,
...     "rating": 5.1
... }
>>>
>>> validate(schema, hotel)
(False, [
    '["price_per_night"] is failing to be `divisible(50)`', 
    '["rating"] is failing to be `between(1, 5)`'
    ])
```

For curiosity here is the implementation of `divisible`  from Tissuebox library. It has been defined as a higher order function which returns another function which always accepts single parameter. While writing custom validators you are encouraged to use the same pattern.
```python
def divisible(n):
    def divisible(x):
        return numeric(x) and numeric(n) and x % n == 0, "multiple of {}".format(n)

    return divisible
```

#### 8. Combining multiple type_functions for same element
As we have observed `tissuebox` schema is a dict with `key:value` format. In Python keys in dicts are unique. It's a terrible idea to redeclare same key since the data will be overridden. 

Assume that you are attempting to do something like this

```python
from tissuebox.basic import divisible, integer, positive, string
schema = {
    'name': string,
    'price_per_night': integer,
    'price_per_night': positive,
    'price_per_night': divisible(50),
    "address.zip": integer
}
```

Here `price_per_night` will be overridden by the latest declaration which must be avoided. This can be solved with another special syntax which yet Pythonic

Simply use `()` to chain type_functions.

    ```python
    from tissuebox.basic import divisible, integer, positive, string
 
    schema = {
        'name': string,
        'price_per_night': (integer, positive, divisible(50)),
        "address.zip": integer
    }
    ```

Now Tissuebox will iterate all these conditions against `price_per_night`

#### 9. Declaring a field as `required`

While Tissuebox validates the values with type_functions, it only does so only for the values are found in the payload. Otherwise they were simply ignored silently.

In a situation where a specific value is expected in payload declared them as `required` function. And it's a common scenario to combine them under `()` operator as described in the above.

```python
from tissuebox.basic import integer, required, string
schema = {
    'name': (required, string),
    "address.city": (required, string),
    "address.zip": integer
}
```

#### Tissuebox Advantages:
- Tissuebox has lots of advantages than the current alternatives like jsonschema, cerebrus etc.
- Truly Pythonic and heavily relies on short & static methods. The schema definition itself takes full advantages of Python's built-in syntax like `{}` for enum, `()` for parameterized function, `[]` chaining multiple rules etc
- Highly readable with concise schema definition. 
- Highly extensible with ability to insert your own custom methods without complicated class inheritance. 
- Ability to provide all the error messages upfront upon validation.

#### Usecases
0 - Tissuebox needs to support primitive literals
- `validate(5, 5)` would be `True` while `validate(5, 4)` is `False`

1 - Tissuebox needs to validate basic primitives, Supported primitives are `int`, `str`, `float`, `list`, `dict`, `Decimal`, `bool`, `None`
- `validate(int, 5)` would return `True`
- `validate(str, 'hello)` would return `True`

2 - Tissuebox needs to validate array of primitives
- `valiate([int], [1,2,3])` would return `True`

3 - Tissuebox needs to validate array of mixed primitives
- `validate([int, str], [1, 'hello', 'world', 2, 3, 4])` would return `True`

4 - Tissuebox needs to support tissues. A tissue is a tiny function which takes 'single' argument and returns a boolean
- `validate(email, 'hello@world.com)` would return `True`

5 - Tissuebox needs to support list of tissues
- `validate([email], ['hello@world.com', 'world@hello.com'])` would return `True`

6 - Tissuebox needs to support list of mixed tissues
- `validate([email, url], ['hello@world.com', 'world@hello.com', 'www.duck.com'])` would return `True`

7 - Tissuebox needs to support tissues with parameters
- `validate(lt(10), 9))` would return `True`

8 - Tissuebox needs to support tissues with parameters
- `validate(lt(10), 9))` would return `True`
- `validate(lt(10), 11))` would return `False`

9 - Tissuebox must support `{}` syntax which refers to `or` condition also should work for list
- `validate({int, str}, 1)` is `True`
- `validate({int, str}, 'Hello')` is `True`
- `validate({int, str}, 1.1)` is `False`
- `validate([{int, str}], [1, 2, 'hello', 'world'])` is `True`

10 - Tissuebox must support `()` syntax which refers to `and` condition also should work for list
- `validate((divisible(2), lt(10)), 4` is `True`
- `validate([(divisible(2), lt(10))], [2, 4, 6, 8]` is `True`

11 - Tissuebox must support dict based schemas

```python
    s = {
        'name': str,
        'active': bool,
        'age': int,
        'pets': [str]
    }
    p = {
        'name': 'Roger',
        'active': True,
        'age': 38,
        'pets': ['Jimmy', 'Roger', 'Jessey']
    }
    validate(s, p)
```

would return `True`

12 - Tissuebox must support sub schema, i.e schemas can be reused
```python
kid = {
    'name': str,
    'age': int,
    'grade': int
}
schema = {
    'name': str,
    'active': bool,
    'age': int,
    'pets': [str],
    'kids': [kid]
}
payload = {
    'name': 'Roger',
    'active': True,
    'age': 38,
    'pets': ['Jimmy', 'Roger', 'Jessey'],
    'kids': [
        {
            'name': "Billy",
            'age': 10,
            'grade': 4
        },
        {
            'name': "Christina",
            'age': 13,
            'grade': 8
        }
    ]
}
validate(schema, payload)
```

would return `True`

#### Later:
- Add support for preemptive evaluation of schema, i.e (1,2) doesn't make sense, it would always be False. So evaluate once and cache it.
