![tissuebox.png](tissuebox.png)

## Tissuebox
Tissuebox is a pure Pythonic schema validator which takes advantage of Python's functional style to provide simple yet powerful validation framework. The standard usage would be validating incoming JSON objects upon http requests or to validate any Python dict in other common scenarios. 

#### Installation:
Use `pip` to install Tissuebox

`pip install tissuebox`

#### Examples:

Assume the incoming JSON object or a python dict which contains `hotel` details. 

```python
hotel = {
    "name": "Park Shereton",
    "available": True,
    "price_per_night": 270,
    "email": "contact@shereton.com",
    "web": "www.shereton.com",
}
```

   
#### 1. Validating basic data types

You can use `tissuebox` to define a schema to validate the payload against basic data types. 

```python
>>> from tissuebox import boolean, integer, string, validate
>>>
>>> schema = {
...     'name': string,
...     'available': boolean,
...     'price_per_night': integer
... }
```

Now you can validate the payload via the `validate` method. 

```python
>>> validate(schema, hotel)
(True, [])
```

#### 2. Validating common datatypes

Tissuebox aims to amass a collection of commonly used types to it's library. As of now common data types like `email`, `url`, `rfc_datetime`, `geolocation` are part of `tissuebox`'s standard collections. You can contribute more via Github. 

```python
>>> from tissuebox import integer, string, validate
>>> from tissuebox.basic import email, url
>>>
>>> schema = {
...     'name': string,
...     'price_per_night': integer,
...     "email": email,
...     "web": url
... }
>>>
>>> validate(schema, hotel)
(True, [])
```
    
One of the ways `tissuebox` stands our from other alternatives is, the type_functions are stored and passed around as Python variables which is helpful in identifying the schema errors ahead of time, while other frameworks like JsonSchema and Cerebrus pass types within strings which is hard for IDEs to detect errors in the schema. 

#### 3. Validating nested fields
You can use the `.` dot as the delimiter to represent nested fields to the payload hierarchy. Apparently this comes up with the downside wherein if `.` dot itself is part of payload keys which would be an unfortunate scenario. But it can improve the readability to a tremendous level. See it yourself how elegantly we can express the schema once we introduce the `address` field to our `hotel` payload. 

```python
>>> from tissuebox import integer, string, validate
>>> from tissuebox.basic import email, url
>>> hotel = {
...     "name": "Park Shereton",
...     "available": True,
...     "price_per_night": 270,
...     "email": "contact@shereton.com",
...     "web": "www.shereton.com",
...     "address": {
...         "street": "128 George St",
...         "city": "Sydney",
...         "state": "NSW",
...         "zip": 2000
...     }
... }
>>>
>>> schema = {
...     'name': string,
...     'price_per_night': integer,
...     "email": email,
...     "web": url,
...     "address.street": string,
...     "address.city": string,
...     "address.state": string,
...     "address.zip": integer
... }
>>>
>>> validate(schema, hotel)
(True, [])
```
    
#### 4. Validating enums. 

Let us try enforcing that the field `address.state` must be one of 8 Australian states. Tissuebox let's you define an enum using the `{}` syntax. Look at the example below. 

```python
>>> schema = {
...     'name': string,
...     'price_per_night': integer,
...     "email": email,
...     "web": url,
...     "address.street": string,
...     "address.city": string,
...     "address.state": {'ACT', 'NSW', 'NT', 'QLD', 'SA', 'TAS', 'VIC', 'WA'},
...     "address.zip": integer
... }
>>>
>>> validate(schema, hotel)
(True, [])
```

To have a feel how Tissuebox responds when we pass something which is not an Australian state

```python
>>> hotel = {
...     "name": "Park Shereton",
...     "available": True,
...     "price_per_night": 270,
...     "email": "contact@shereton.com",
...     "web": "www.shereton.com",
...     "address": {
...         "street": "128 George St",
...         "city": "Sydney",
...         "state": "TX",
...         "zip": 2000
...     }
... }
>>>
>>> validate(schema, hotel)
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
>>>
>>> from tissuebox import integer, string, validate
>>> from tissuebox.basic import boolean, email, numeric, url
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

#### Tissuebox Advantages:
- Tissuebox has lots of advantages than the current alternatives like jsonschema, cerebrus etc.
- Truly Pythonic and heavily relies on short & static methods. The schema definition itself takes full advantages of Python's built-in syntax like `{}` for enum, `()` for parameterized function etc
- Highly readable with concise schema definition. 
- Highly extensible with ability to insert your own custom methods without complicated code. 
