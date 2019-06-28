from decimal import Decimal
from unittest import TestCase

from tissuebox import SchemaError, normalise, sort_unique, valid_schema, validate, validate as v, aster_to_list
from tissuebox.basic import divisible, email, integer, lt, url, uuid4

class TestMiscellaneous(TestCase):
    def test_sort_unique(self):
        l = [4, 3, 2, 1, 1, 2, 3, 4]
        sort_unique(l)
        assert l == [1, 2, 3, 4]

class TestValidSchema(TestCase):
    def setup(self):
        pass

    def teardown(self):
        pass

    # All primitive literals are valid schemas
    def test_schema_primitive_literals(self):
        assert valid_schema(None)
        assert valid_schema(True)
        assert valid_schema(False)
        assert valid_schema(-1)
        assert valid_schema(0)
        assert valid_schema(1)
        assert valid_schema(1.1)
        assert valid_schema(1e3)
        assert valid_schema(3 + 4j)
        assert valid_schema('hello')
        assert valid_schema([])
        assert valid_schema(())
        assert valid_schema(set())

    # All primitive types are valid schemas
    def test_schema_primitive_types(self):
        assert valid_schema(int)
        assert valid_schema(str)
        assert valid_schema(float)
        assert valid_schema(list)
        assert valid_schema(set)
        assert valid_schema(dict)
        assert valid_schema(tuple)
        assert valid_schema(complex)
        assert valid_schema(bool)

    def test_schema_is_list_of_mixed_primitives__ok(self):
        schema = [int, str, bool]
        assert valid_schema(schema)

    def test_schema_is_tissue__ok(self):
        s = email
        assert valid_schema(s)

    def test_schema_is_tissuelist__ok(self):
        s = [email]
        assert valid_schema(s)

    def test_schema_is_tissuelistmixed__ok(self):
        s = [email, url, uuid4]
        assert valid_schema(s)

    def test_schema_is_tissuelistmixed_literal_nok(self):
        s = [email, url, uuid4, 'hello']
        assert valid_schema(s)

    def test_schema_is_tissues_mixed_with_primitives__ok(self):
        s = [email, url, uuid4, bool, integer, int, str]
        assert valid_schema(s)

class TestPrimitives(TestCase):
    def setup(self):
        pass

    def teardown(self):
        pass

    def test_schema_list_payload_empty_list(self):
        schema = list
        payload = []
        assert validate(schema, payload)

    def test_schema_list_payload_non_empty_list(self):
        schema = list
        payload = [1, 2, "hello", True, None]
        assert validate(schema, payload)

    def test_schema_list_payload_non_list(self):
        schema = list
        payload = 'Hello'
        assert not validate(schema, payload)

    def test_schema_int_payload_int(self):
        schema = int
        payload = 5
        assert validate(schema, payload)

    def test_schema_int_payload_int_0(self):
        schema = int
        payload = 0
        assert validate(schema, payload)

    def test_schema_int_payload_int_negative(self):
        schema = int
        payload = -10
        assert validate(schema, payload)

    def test_schema_int_payload_scientific__nok(self):
        schema = int
        payload = 1e3
        assert not validate(schema, payload)
        payload = 1e+3
        assert not validate(schema, payload)
        payload = 1e-3
        assert not validate(schema, payload)

    def test_schema_int_payload_boolean(self):
        schema = int
        payload = False
        assert not validate(schema, payload)

    def test_schema_int_payload_none(self):
        schema = int
        payload = None
        assert not validate(schema, payload)

    def test_schema_int_payload_string__nok(self):
        schema = int
        payload = "Hello"
        assert not validate(schema, payload)

    def test_schema_float_payload_int__ok(self):
        schema = float
        payload = 5
        assert validate(schema, payload)

    def test_schema_float_payload_float__ok(self):
        schema = float
        payload = 5.5
        assert validate(schema, payload)

    def test_schema_float_payload_float_scientific__ok(self):
        schema = float
        payload = 4.08E+10
        assert validate(schema, payload)

    def test_schema_float_payload_bool__nok(self):
        schema = float
        payload = False
        assert not validate(schema, payload)

    def test_schema_float_payload_string__nok(self):
        schema = float
        payload = "Hello"
        assert not validate(schema, payload)

    def test_schema_float_payload_list__nok(self):
        schema = float
        payload = [1, 2]
        assert not validate(schema, payload)

    def test_schema_float_payload_set__nok(self):
        schema = float
        payload = {1, 2}
        assert not validate(schema, payload)

    def test_schema_float_payload_dict__nok(self):
        schema = float
        payload = {1: 2}
        assert not validate(schema, payload)

    def test_schema_float_payload_tuple__nok(self):
        schema = float
        payload = (1, 2)
        assert not validate(schema, payload)

    def test_schema_float_payload_Decimal__ok(self):
        schema = float
        payload = Decimal(5)
        assert validate(schema, payload)

    def test_schema_str_payload_str__ok(self):
        schema = str
        payload = 'Hello'
        assert validate(schema, payload)

    def test_schema_str_payload_empty_str__ok(self):
        schema = str
        payload = ''
        assert validate(schema, payload)

    def test_schema_str_payload_int__nok(self):
        schema = str
        payload = 0
        assert not validate(schema, payload)

    def test_schema_str_payload_none__nok(self):
        schema = str
        payload = None
        assert not validate(schema, payload)

    def test_schema_str_payload_bool__nok(self):
        schema = str
        payload = False
        assert not validate(schema, payload)

    def test_schema_str_payload_list__nok(self):
        schema = str
        payload = ['hello', 'world']
        assert not validate(schema, payload)

    def test_schema_str_payload_tuple__nok(self):
        schema = str
        payload = ()
        assert not validate(schema, payload)

    def test_schema_none_payload_none__ok(self):
        schema = None
        payload = None
        assert validate(schema, payload)

    def test_schema_none_payload_bool__nok(self):
        schema = None
        payload = True
        assert not validate(schema, payload)

    def test_schema_none_payload_str__nok(self):
        schema = None
        payload = 'hello'
        assert not validate(schema, payload)

class TestCauseSchemaError(TestCase):
    def test_schema_is_invalid(self):
        schema = Decimal
        payload = 5
        self.assertRaises(SchemaError, validate, schema, payload)

class TestListOfPrimitives(TestCase):
    def test_schema_list_int_payload_list_int(self):
        schema = [int]
        payload = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        assert validate(schema, payload)

    def test_schema_strlist_payload_intlist__nok(self):
        schema = [str]
        payload = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        errors = []
        assert not validate(schema, payload, errors)
        # assert '1 must be string' in errors
        # assert '2 must be string' in errors
        # assert '10 must be string' in errors

    def test_schema_strlist_payload_not_a_list__nok(self):
        schema = [str]
        payload = 1
        errors = []
        assert not validate(schema, payload, errors)
        assert '1 must be list' in errors

    def test_scheme_mixedlist_payload_within__ok(self):
        schema = [str, bool]
        payload = ['hello', False]
        assert validate(schema, payload)

    def test_scheme_mixedlist_payload_outside__nok(self):
        schema = [str, bool, None, int]
        payload = ['hello', False, 5.5]
        errors = []
        assert not validate(schema, payload, errors)
        # assert '5.5 must be either null, boolean, string or integer' in errors

class TestTissues(TestCase):
    """
    Use cases 4, 5, 6
    """

    def test_schema_email_payload_email_ok(self):
        s = email
        p = 'hello@world.com'
        assert validate(s, p)

    def test_schema_emaillist_payload_emaillist_ok(self):
        s = [email]
        p = ['hello@world.com', 'world@hello.com']
        assert validate(s, p)

    def test_schema_mixedlist_payload_within__ok(self):
        s = [email, str, int]
        p = ['hello@world.com', 'world', 5]
        assert validate(s, p)

    def test_schema_mixedtissuelist_payload_outslidelist__nok(self):
        s = [email, url]
        p = ['hello@world.com', 'world@hello.com', 'com']
        e = []
        assert not validate(s, p, e)
        # assert 'com must be either a valid url or a valid email' in e

    def test_schema_lt10(self):
        s = lt(10)
        p = 9
        assert v(s, p)
        p = 11
        e = []
        assert not v(s, p, e)
        # assert '11 must be less than 10' in e

        s = [lt(10)]
        p = 9
        e = []
        assert not v(s, p, e)
        # assert '9 must be list' in e

        p = [7, 8, 9]
        assert v(s, p)

        p = [7, 8, 9, 10, 11, 12]
        e = []
        assert not v(s, p, e)
        # assert '10 must be less than 10' in e
        # assert '11 must be less than 10' in e
        # assert '12 must be less than 10' in e

class TestComplexSyntax(TestCase):
    def test_curly_braces(self):
        assert validate({1, 2}, 1)
        assert validate({1, 2}, 2)

        e = []
        assert not validate({1, 2}, 3, e)
        # assert '3 must be either 1 or 2' in e

        assert validate([{1, 2}], [1, 2, 2, 2, 1, 1, 1])

        e = []
        assert not validate([{1, 2}], [1, 2, 3, 4, 15], e)
        assert e == [
            '[2] must be either 1 or 2 (but 3)',
            '[3] must be either 1 or 2 (but 4)',
            '[4] must be either 1 or 2 (but 15)'
        ]
        assert validate([{int, str}], [1, 'hello', 2, 'world'])
        assert not validate([{int, str}], [1, 2, 'hello', 'world', True])
        assert not validate([{int, str}], [1, 2, 'hello', 'world', None])
        assert not validate([{int, str}], [1, 2, 'hello', 'world', 3.8])
        assert not validate([{int, str}], [1, 2, 'hello', 'world', 3.4j])
        assert not validate([{int, str}], [1, 2, 'hello', 'world', str])

    def test_parentheses(self):
        s = (divisible(2), lt(10))
        assert validate(s, 4)

        e = []
        assert not validate(s, 5, e)
        assert '5 must be multiple of 2' in e

        e = []
        assert not validate(s, 11, e)
        assert '11 must be multiple of 2' in e
        assert '11 must be less than 10' in e

        # Validate list of parentheses
        assert validate([s], [2, 4, 6, 8])

        e = []
        assert not validate([s], [3, 13], e)
        # assert '3 must be multiple of 2' in e
        # assert '13 must be multiple of 2' in e
        # assert '13 must be less than 10' in e

        assert not validate([(bool, True)], [1, 2])  # 1 & 2 are not booleans

    def test_dicts(self):
        # Success
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
        assert v(s, p)

        # Pass wrong data types
        p = {
            'name': 50,
            'active': 'Yes',
            'age': "38",
            'pets': [1, 2, 'Jessey']
        }
        e = []
        assert not v(s, p, e)
        expected = ["['active'] must be boolean (but 'Yes')", "['age'] must be integer (but '38')",
                    "['name'] must be string (but 50)", "['pets'][0] must be string (but 1)",
                    "['pets'][1] must be string (but 2)"]
        assert expected == e

    def test_subschema(self):
        kid = {
            'name': str,
            'age': int,
            'grade': int,
            'sex': {'Male', 'Female'}
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
                    'grade': 8,
                    'sex': 'Female'
                }
            ]
        }
        assert validate(schema, payload)

        # Non-existing keys are just fine
        del payload['kids'][1]['grade']
        assert validate(schema, payload)

        # Try passing different value
        payload['kids'][1]['grade'] = None
        e = []
        assert not validate(schema, payload, e)
        assert e == ["['kids'][1]['grade'] must be integer (but None)"]

        # Try adding a different value other than 'male' or 'female'
        e = []
        payload['kids'][1]['sex'] = 'f'
        assert not validate(schema, payload, e)
        assert "['kids'][1]['sex'] must be either Female or Male (but f)" in e

    def test_nonstring_keys(self):
        kid = {
            'name': str,
            1: str
        }
        schema = {
            'name': str,
            1: bool,
            'kids': [kid]
        }
        payload = {
            'name': 'Roger',
            1: True,
            'kids': [
                {
                    'name': "Silly",
                    1: "HW",
                },
                {
                    'name': "Billy",
                    1: "Hello World",
                },
            ]
        }
        assert validate(schema, payload)

        # Change the payload to cause an error
        payload['kids'][0][1] = 10
        e = []
        assert not validate(schema, payload, e)
        assert e == ["['kids'][0][1] must be string (but 10)"]

class TestNormalise(TestCase):
    def test_normalise_basics(self):
        schema = {
            'name': str,
            'active': bool,
            'age': int,
        }
        normalise(schema)
        assert schema == {
            'name': str,
            'active': bool,
            'age': int,
        }

        # Bit more realistic case
        schema = {
            'name': str,
            'active': bool,
            'age': int,
            'pets': [str],
            'kid.name': str,
            'kid.age': int,
            'kid.grade': int,
            'kid.phone.model': str,
            'kid.phone.year': int,
            'kid.phone.career': {'Verizon', 'AT & T', 'T-Mobile'},
        }
        normalise(schema)
        assert schema == {
            'name': str,
            'active': bool,
            'age': int,
            'pets': [str],
            'kid': {
                'name': str,
                'age': int,
                'grade': int,
                'phone': {
                    'model': str,
                    'year': int,
                    'career': {'Verizon', 'AT & T', 'T-Mobile'},
                }
            }
        }

        # Corner cases
        schema = {}
        normalise(schema)
        assert schema == {}

        schema = {
            'names': []
        }
        normalise(schema)
        assert schema == {
            'names': []
        }

        schema = {
            'names': [1, 2]
        }
        normalise(schema)
        assert schema == {
            'names': [1, 2]
        }

        schema = {
            'names': {1, 2}
        }
        normalise(schema)
        assert schema == {
            'names': {1, 2}
        }

        schema = 5
        normalise(schema)
        assert schema == 5

        schema = str
        normalise(schema)
        assert schema == str

    def test_schema_dotted(self):
        schema = {
            'name': str,
            'active': bool,
            'age': int,
            'pets': [str],
            'kid.name': str,
            'kid.age': int,
            'kid.grade': int,
            'kid.phone.model': str,
            'kid.phone.year': int,
            'kid.phone.career': {'Verizon', 'AT & T', 'T-Mobile'},
        }
        payload = {
            'name': 'Roger',
            'active': False,
            'age': 42,
            'pets': ['Elise', 'Richard', 'Caprice'],
            'kid': {
                'name': 'Julia',
                'age': 12,
                'grade': 6,
                'phone': {
                    'model': 'iPhone X',
                    'year': 2017,
                    'career': 'Verizon',
                }
            }
        }
        assert validate(schema, payload)

        # Send an incorrect career name
        e = []
        payload['kid']['phone']['career'] = 'X'
        assert not validate(schema, payload, e)
        assert "['kid']['phone']['career'] must be either" in e[0]

    def test_more_normalise(self):
        schema = {
            'name': str,
            'active': bool,
            'age': int,
            'pets': [str],
            'more': {
                'kid.name': str,
                'kid.age': int,
                'kid.phones.*.model': str,
                'kid.phones.*.year': int,
                'kid.phones.*.career': {'Verizon', 'AT & T', 'T-Mobile'},
            }
        }
        normalise(schema)
        assert schema == {
            'name': str,
            'active': bool,
            'age': int,
            'pets': [str],
            'more': {
                'kid': {
                    'name': str,
                    'age': int,
                    'phones': {
                        '*': {
                            'model': str,
                            'year': int,
                            'career': {'Verizon', 'T-Mobile', 'AT & T'}
                        }
                    }
                }
            }
        }
        schema = aster_to_list(schema)
        assert schema == {
            'name': str,
            'active': bool,
            'age': int,
            'pets': [str],
            'more': {
                'kid': {
                    'name': str,
                    'age': int,
                    'phones': [
                        {
                            'model': str,
                            'year': int,
                            'career': {'Verizon', 'T-Mobile', 'AT & T'}
                        }
                    ]
                }
            }
        }

        # Corner case
        schema = {
            'kid.name': str,
            'kid.friends.*': str,  # In this case '*' is enough to justify that 'kid.friends' is a string array
        }
        normalise(schema)
        schema = aster_to_list(schema)
        assert schema == {
            'kid': {
                'name': str,
                'friends': [str]
            }
        }

    def test_dotted_asterisk(self):
        schema = {
            'name': str,
            'active': bool,
            'age': int,
            'pets': [str],
            'kid.name': str,
            'kid.age': int,
            'kid.phones.*.model': str,
            'kid.phones.*.year': int,
            'kid.phones.*.career': {'Verizon', 'AT & T', 'T-Mobile'}
        }

        payload = {
            'name': 'Roger',
            'active': False,
            'age': 42,
            'pets': ['Elise', 'Richard', 'Caprice'],
            'kid': {
                'name': 'Julia',
                'age': 12,
                'grade': 6,
                'phones': [
                    {
                        'model': 'iPhone X',
                        'year': 2017,
                        'career': 'Verizon',
                    },
                    {
                        'model': 'iPhone XS',
                        'year': 2019,
                        'career': 'Verizon',
                    },
                    {
                        'model': 'Huawei P30',
                        'year': 2019,
                        'career': 'Vodafone',
                    }
                ]
            }
        }

        e = []
        assert not validate(schema, payload, e)
        assert '[\'kid\'][\'phones\'][2][\'career\'] must be either' in e[0]

# class TestRequiredDenied(TestCase):
#     def test_required(self):
#         s = {
#             required: 'age',
#             'name': str,
#         }
#         p = {
#             'name': 'Peter',
#             'active': True
#         }
#         assert not validate(s, p)
class TestSchemaError(TestCase):
    def test_dotted_override(self):
        schema = {
            'name': str,
            'active': bool,
            'age': int,
            'pets': [str],
            'kid.name': str,
            'kid.name.first': str  # This line means 'kid.name' is a dict{} however the previous line claims 'kid.name' is a `str`, which is a conflict, expect SchemaError
        }

        with self.assertRaises(SchemaError):
            validate(schema, None)

        schema = {
            'name': str,
            'active': bool,
            'age': int,
            'pets': [str],
            'kid.name.first': str,
            'kid.name': str,  # Same case as above, this time this line has the chance to override previously declared deeper schema. Expect SchemaError
            # i.e 'kid.name.first' is already declared as `str`, now while declaring `'kid.name` as something else Tissuebox MUST NOT override the previous and MUST detect the conflict.
        }

        # Warning: Depending on the run time this test might fail, because it depends on the order where Python iterates the key. In both the scenarios SchemaError is expected.
        # Once a while manually run these cases while enabling debugger
        with self.assertRaises(SchemaError):
            validate(schema, None)
