![tissuebox.png](tissuebox.png)

## Tissuebox
Tissuebox is a pure Pythonic schema validator which takes advantage of Python's functional style to provide simple yet powerful validation framework. The standard usage would be validating incoming JSON objects upon http requests or to validate any Python dict in other common scenarios. 

#### Installation:
Use `pip` to install Tissuebox

`pip install tissuebox`

#### Requirements:
Tissuebox requires Python 3.7 however we are considering to add support for earlier versions along with Python 2.7. 

#### Examples:

Assume the incoming JSON object or a python dict which contains hotel details. 

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

You can use `tissuebox` to define a schema to validate the payload against basic data types and validate the payload via the `validate` method. 

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

Tissuebox aims to amass a collection of commonly used types to it's library. As of now common data types like `email`, `url`, `rfc_datetime`, `geolocation` are part of `tissuebox`'s standard collections. You can contribute more via Github. 

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
    
One of the ways `tissuebox` stands our from other alternatives is, the type_functions are stored and passed around as Python variables which is helpful in identifying the schema errors ahead of time, while other frameworks like JsonSchema and Cerebrus pass types within strings which is hard for IDEs to detect errors in the schema. 

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

address_schema = {
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
    "address": address_schema
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

#### 5. Writing custom validators
    
By now you would have observed that `tissuebox` schema is simply a collection of `key:value` pairs where `value` contains the data type verified against. `tissuebox` defines them in the style of `type_function` which is simply a boolean function that takes one or more parameters. 

Let us assume you want to validate the zip code as a valid Australian one. Since `tissuebox` does't have a built-in type function, for that purpose you can come up with your own type function as below. For brevity I've removed few fields in the payload & schema.

```python
>>> def australian_zip(x):
...     # https://www.etl-tools.com/regular-expressions/is-australian-post-code.html
...     x = str(x)
...     import re
...     return re.match(r'^(0[289][0-9]{2})|([1345689][0-9]{3})|(2[0-8][0-9]{2})|(290[0-9])|(291[0-4])|(7[0-4][0-9]{2})|(7[8-9][0-9]{2})$', x)
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
(False, ['["address"]["zip"] is failing to be `australian_zip`'])
```
    
#### 6. Getting all the error messages at one. 

We shoud not forget that `tissuebox` will always provide all possible errors upfront wherein the areas payload is failing. That way the user has the opportunity to fix his payload accordingly. 

Let's have a look where the incoming payload has lots of issues

```python
>>> from pprint import pprint
>>> hotel = {
...     "name": "Park Shereton",
...     "available": "True",
...     "price_per_night": "270",
...     "email": "contact@shereton.com",
...     "web": "www.shereton.com",
...     "address": {
...         "street": "128 George St",
...         "city": "Sydney",
...         "state": "TX",
...         "zip": "2000"
...     }
... }
>>>
>>> schema = {
...     "name": string,
...     "available": boolean,
...     "price_per_night": numeric,
...     "email": email,
...     "web": url,
...     "address.street": string,
...     "address.city": string,
...     "address.state": {"ACT", "NSW", "NT", "QLD", "SA", "TAS", "VIC", "WA"},
...     "address.zip": integer
... }
>>>
>>> pprint(validate(schema, hotel))
(False,
 ['["address"]["state"] is failing to be enum of `{\'SA\', \'QLD\', \'NT\', '
  "'TAS', 'VIC', 'WA', 'ACT', 'NSW'}`",
  '["address"]["zip"] is failing to be `integer`',
  '["available"] is failing to be `boolean`',
  '["price_per_night"] is failing to be `numeric`'])
```
      
#### 7. Validating data types that accept parameters. 

Type functions can accept zero, one or more parameters. In such scenario the below syntax needs to be used `()`. Let us try validating where the `price_per_night` must be multiple of 50. Also let us declare the Yelp review rating of a hotel must be between 1-5. 

```python
>>> from tissuebox import validate
>>> from tissuebox.basic import between, divisible, string

>>> schema = {
...     "name": string,
...     "rating": (between, 1, 5),
...     "price_per_night": (divisible, 50)
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

#### 8. Combining multiple type_functions for same element
As we have observed `tissuebox` schema is a dict with `key:value` format. In Python keys in dicts are unique. It's a terrible idea to redeclare same key since the data will be overridden. 

Assume that you are attempting to do something like this

```python
from tissuebox.basic import divisible, integer, positive, string
schema = {
    'name': string,
    'price_per_night': integer,
    'price_per_night': positive,
    'price_per_night': (divisible, 50),
    "address.zip": integer
}
```

While this is a good intention since `price_per_night` cannot go negative in Python dict keys cannot be duplicated. This can be solved in two ways

1. Write a custom validator which takes care of the logic that is performed by all the three functions as below

    ```python
    from tissuebox.basic import divisible, integer, positive, string
 
    def price_per_night(x):
       return integer(x) and positive(x) and divisible(x, 50)
    
    schema = {
        'name': string,
        'price_per_night': price_per_night,
        "address.zip": integer
    }
    ```
2. While the above method would surely help the cleaner way to do that is by chaining them under `[]` operator.

    ```python
    from tissuebox.basic import divisible, integer, positive, string
 
    schema = {
        'name': string,
        'price_per_night': [integer, positive, (divisible, 50)],
        "address.zip": integer
    }
    ```
#### 9. Declaring a field as `required`

All the fields that are declare in `tissuebox` schema are iteratively checked against the type_function defined in the schema. If an element is not found in the payload it gets skipped and `tissuebox` will not mark it as an error because the `type_function` is invoked if and only if when the element is found in the payload. 

If you want an element to be declared as mandatory then use the `required` option in the schema. 

And it's a common scenario to combine them under `[]` operator as described in the above topic. 

```python
from tissuebox.basic import integer, required, string
schema = {
    'name': [required, string],
    "address.city": [required, string],
    "address.zip": integer
}
```

#### 10. Arrays
Arrays in Tissuebox are very intuitive to work with. Unlike other frameworks `tissuebox` doesn't require us to declare `many=True`. Instead it dynamically detects if the payload contains `list` and acts accordingly. 
- If a list is found then the given condition is checked against all the elements of the list. 
- Meaningful error messages are provided with exact index of the array element. 
- It is still possible to declare it as `array` while defining but there is not a need to do so and its something not usually recommended. 

Let's consider a detailed payload & schema where payload contains few details of actors

```python
from tissuebox import validate
from tissuebox.basic import integer, numeric, positive, required, string, url
payload = [
    {
        "name": "Tom Cruise",
        "age": 56,
        "birth_place": "Syracuse, NY",
        "birth_date": "July 3, 1962",
        "photo": "https://jsonformatter.org/img/tom-cruise.jpg",
        "wife": None,
        "weight": 67.5,
        "has_children": True,
        "has_greyhair": False,
        "children": [
            "Suri",
            "Isabella Jane",
            "Connor"
        ]
    },
    {
        "name": "Robert Downey Jr.",
        "age": 53,
        "birth_place": "New York City, NY",
        "birth_date": "April 4, 1965",
        "photo": "https://jsonformatter.org/img/Robert-Downey-Jr.jpg",
        "wife": "Susan Downey",
        "weight": 77.1,
        "has_children": True,
        "has_greyhair": False,
        "children": [
            "Indio Falconer",
            ["bad value"],
            "Avri Roel",
            "Exton Elias"
        ]
    }
]

schema = {
    "name": string,
    "age": [positive, integer],
    "birth_place": string,
    "photo": url,
    "wife": [required, string],
    "weight": [required, numeric],
    "children": string
}

validate(schema, payload)

```

Will output 

```python
(False, [
    '[0]["wife"] is failing to be `string`', 
    '[1]["children"][1] is failing to be `string`'
])
```

As noted above, `"children": string` means `children` must be either string or array of strings. We don't have to declare that as array. Tissuebox will detect it dynamically and ensure whether all the elements fulfilling the condition. Also the error details received are helpful as they indicate failing indices. 


#### Tissuebox Advantages:
- Tissuebox has lots of advantages than the current alternatives like jsonschema, cerebrus etc.
- Truly Pythonic and heavily relies on short & static methods. The schema definition itself takes full advantages of Python's built-in syntax like `{}` for enum, `()` for parameterized function, `[]` chaining multiple rules etc
- Highly readable with concise schema definition. 
- Highly extensible with ability to insert your own custom methods without complicated class inheritance. 
