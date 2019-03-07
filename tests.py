from decimal import Decimal
from unittest import TestCase

from tissuebox import SchemaError, valid_schema, validate

class TestValidSchema(TestCase):
    def setup(self):
        pass

    def teardown(self):
        pass

    def test_schema_is_int__ok(self):
        schema = int
        assert valid_schema(schema)

    def test_schema_is_float__ok(self):
        schema = float
        assert valid_schema(schema)

    def test_schema_is_str__ok(self):
        schema = str
        assert valid_schema(schema)

    def test_schema_is_bool__ok(self):
        schema = bool
        assert valid_schema(schema)

    def test_schema_is_None__ok(self):
        schema = None
        assert valid_schema(schema)

    def test_schema_is_list__ok(self):
        schema = list
        assert valid_schema(schema)

    def test_schema_is_dict__ok(self):
        schema = dict
        assert valid_schema(schema)

    def test_schema_is_list_of_mixed_primitives__ok(self):
        schema = [int, str, bool]
        assert valid_schema(schema)

    def test_schema_is_string_literal__nok(self):
        schema = 'hello'
        assert not valid_schema(schema)

    def test_schema_is_int_literal__nok(self):
        schema = 10
        assert not valid_schema(schema)

    def test_schema_is_bool_literal__nok(self):
        schema = False
        assert not valid_schema(schema)

    def test_schema_is_list_of_primitives_and_literals__nok(self):
        schema = [int, 'hello', str, 5]
        assert not valid_schema(schema)

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
        schema = 5
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
        assert '1 must be string' in errors
        assert '2 must be string' in errors
        assert '10 must be string' in errors

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
        assert "5.5 must be either string, boolean, null or integer" in errors
