from decimal import Decimal
from unittest import TestCase

from tissuebox import SchemaError, valid_schema, validate, validate as v
from tissuebox.basic import email, integer, lt, url, uuid4

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
        assert '`1` must be string' in errors
        assert '`2` must be string' in errors
        assert '`10` must be string' in errors

    def test_schema_strlist_payload_not_a_list__nok(self):
        schema = [str]
        payload = 1
        errors = []
        assert not validate(schema, payload, errors)
        assert '`1` must be list' in errors

    def test_scheme_mixedlist_payload_within__ok(self):
        schema = [str, bool]
        payload = ['hello', False]
        assert validate(schema, payload)

    def test_scheme_mixedlist_payload_outside__nok(self):
        schema = [str, bool, None, int]
        payload = ['hello', False, 5.5]
        errors = []
        assert not validate(schema, payload, errors)
        assert '`5.5` must be either null, boolean, string or integer' in errors

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
        assert '`com` must be either a valid url or a valid email' in e

    def test_schema_lt10(self):
        s = lt(10)
        p = 9
        assert v(s, p)
        p = 11
        e = []
        assert not v(s, p, e)
        assert '`11` must be less than 10' in e

        s = [lt(10)]
        p = 9
        e = []
        assert not v(s, p, e)
        assert '`9` must be list' in e

        p = [7, 8, 9]
        assert v(s, p)

        p = [7, 8, 9, 10, 11, 12]
        e = []
        assert not v(s, p, e)
        assert '`10` must be less than 10' in e
        assert '`11` must be less than 10' in e
        assert '`12` must be less than 10' in e

class TestComplexSyntax(TestCase):
    def test_curly_braces(self):
        assert validate({1, 2}, 1)
        assert validate({1, 2}, 2)

        e = []
        assert not validate({1, 2}, 3, e)
        assert '`3` must be either 1 or 2' in e

        assert validate([{1, 2}], [1, 2, 2, 2, 1, 1, 1])

        e = []
        assert not validate([{1, 2}], [1, 2, 3, 4], e)
        assert '`3` must be either 1 or 2' in e
        assert '`4` must be either 1 or 2' in e

        assert validate([{int, str}], [1, 2, 'hello', 'world'])
        assert not validate([{int, str}], [1, 2, 'hello', 'world', True])
        assert not validate([{int, str}], [1, 2, 'hello', 'world', None])
        assert not validate([{int, str}], [1, 2, 'hello', 'world', 3.8])
        assert not validate([{int, str}], [1, 2, 'hello', 'world', 3.4j])
        assert not validate([{int, str}], [1, 2, 'hello', 'world', str])
