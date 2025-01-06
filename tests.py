from decimal import Decimal
from unittest import TestCase

from tissuebox import SchemaError, normalise, sort_unique, is_valid_schema, validate as v, not_
from tissuebox import validate
from tissuebox.basic import divisible, lt, uuid4
from tissuebox.basic import integer, string, email, url, numeric
from tissuebox.basic import strong_password


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
        assert is_valid_schema(None)
        assert is_valid_schema(True)
        assert is_valid_schema(False)
        assert is_valid_schema(-1)
        assert is_valid_schema(0)
        assert is_valid_schema(1)
        assert is_valid_schema(1.1)
        assert is_valid_schema(1e3)
        assert is_valid_schema(3 + 4j)
        assert is_valid_schema("hello")
        assert is_valid_schema([])
        assert is_valid_schema(())
        assert is_valid_schema(set())

    # All primitive types are valid schemas
    def test_schema_primitive_types(self):
        assert is_valid_schema(int)
        assert is_valid_schema(str)
        assert is_valid_schema(float)
        assert is_valid_schema(list)
        assert is_valid_schema(set)
        assert is_valid_schema(dict)
        assert is_valid_schema(tuple)
        assert is_valid_schema(complex)
        assert is_valid_schema(bool)

    def test_schema_is_list_of_mixed_primitives__ok(self):
        schema = [int, str, bool]
        assert is_valid_schema(schema)

    def test_schema_is_tissue__ok(self):
        s = email
        assert is_valid_schema(s)

    def test_schema_is_tissuelist__ok(self):
        s = [email]
        assert is_valid_schema(s)

    def test_schema_is_tissuelistmixed__ok(self):
        s = [email, url, uuid4]
        assert is_valid_schema(s)

    def test_schema_is_tissuelistmixed_literal_nok(self):
        s = [email, url, uuid4, "hello"]
        assert is_valid_schema(s)

    def test_schema_is_tissues_mixed_with_primitives__ok(self):
        s = [email, url, uuid4, bool, integer, int, str]
        assert is_valid_schema(s)


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
        payload = "Hello"
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
        payload = 1e3
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
        payload = 4.08e10
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
        payload = "Hello"
        assert validate(schema, payload)

    def test_schema_str_payload_empty_str__ok(self):
        schema = str
        payload = ""
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
        payload = ["hello", "world"]
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
        payload = "hello"
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
        assert errors == ["must be list"]

    def test_scheme_mixedlist_payload_within__ok(self):
        schema = [str, bool]
        payload = ["hello", False]
        assert validate(schema, payload)

    def test_scheme_mixedlist_payload_outside__nok(self):
        schema = [str, bool, None, int]
        payload = ["hello", False, 5.5]
        errors = []
        assert not validate(schema, payload, errors)
        # assert '5.5 must be either null, boolean, string or integer' in errors


class TestTissues(TestCase):
    """
    Use cases 4, 5, 6
    """

    def test_schema_email_payload_email_ok(self):
        s = email
        p = "hello@world.com"
        assert validate(s, p)

    def test_schema_emaillist_payload_emaillist_ok(self):
        s = [email]
        p = ["hello@world.com", "world@hello.com"]
        assert validate(s, p)

    def test_schema_mixedlist_payload_within__ok(self):
        s = [email, str, int]
        p = ["hello@world.com", "world", 5]
        assert validate(s, p)

    def test_schema_mixedtissuelist_payload_outslidelist__nok(self):
        s = [email, url]
        p = ["hello@world.com", "world@hello.com", "com"]
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
        assert not validate([{1, 2}], [1, 2, 3, 4], e)
        # assert '3 must be either 1 or 2' in e
        # assert '4 must be either 1 or 2' in e

        assert validate([{int, str}], [1, 2, "hello", "world"])
        assert not validate([{int, str}], [1, 2, "hello", "world", True])
        assert not validate([{int, str}], [1, 2, "hello", "world", None])
        assert not validate([{int, str}], [1, 2, "hello", "world", 3.8])
        assert not validate([{int, str}], [1, 2, "hello", "world", 3.4j])
        assert not validate([{int, str}], [1, 2, "hello", "world", str])

    def test_parentheses(self):
        s = (divisible(2), lt(10))
        assert validate(s, 4)

        e = []
        assert not validate(s, 5, e)
        assert e == ["must be multiple of 2 (but 5)"]

        e = []
        assert not validate(s, 11, e)
        assert e == ["must be less than 10 (but 11)", "must be multiple of 2 (but 11)"]

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
        s = {"name": str, "active": bool, "age": int, "pets": [str]}
        p = {"name": "Roger", "active": True, "age": 38, "pets": ["Jimmy", "Roger", "Jessey"]}
        assert v(s, p)

        # Pass wrong data types
        p = {"name": 50, "active": "Yes", "age": "38", "pets": [1, 2, "Jessey"]}
        e = []
        assert not v(s, p, e)

        assert e == [
            "['active'] must be boolean (but 'Yes')",
            "['age'] must be integer (but '38')",
            "['name'] must be string (but 50)",
            "['pets'] [0] must be string (but 1)",
            "['pets'] [1] must be string (but 2)",
        ]

    def test_subschema(self):
        kid = {
            "name": str,
            "age": int,
            "grade": int,
            "sex": {"Male", "Female"},
        }
        schema = {
            "name": str,
            "active": bool,
            "age": int,
            "pets": [str],
            "kids": [kid],
        }
        payload = {
            "name": "Roger",
            "active": True,
            "age": 38,
            "pets": ["Jimmy", "Roger", "Jessey"],
            "kids": [
                {"name": "Billy", "age": 10, "grade": 4, "sex": "Male"},
                {"name": "Christina", "age": 13, "grade": 8, "sex": "Female"},
            ],
        }
        errors = []
        assert validate(schema, payload, errors)

        # Try passing different value
        payload["kids"][1]["grade"] = None
        e = []
        assert not validate(schema, payload, e)
        assert e == ["['kids'] [1] ['grade'] must be integer (but None)"]

        # Try adding a different value other than 'male' or 'female'
        e = []
        payload["kids"][1]["sex"] = "f"
        assert not validate(schema, payload, e)
        assert e == ["['kids'] [1] ['grade'] must be integer (but None)", "['kids'] [1] ['sex']  must be either Female or Male (but f)"]


class TestNormalise(TestCase):
    def test_exceptions(self):
        schema = {
            "name": str,
            "active": bool,
            "age": int,
            "pets": [str],
            "kids.name": str,
            "kids.oor": str,
            "kids.*.grade": int,
            "kids.grade.marks": int,
            "kids.age": str,
        }

        normalise(schema)

        assert schema == {
            "name": str,
            "active": bool,
            "age": int,
            "pets": [str],
            "kids": {
                "name": str,
                "oor": str,
                "*": {"grade": int},
                "grade": {"marks": int},
                "age": str,
            },
        }

    def test_misc(self):
        schema = {
            "name": str,
            "active": bool,
            "age": int,
            "pets": [str],
            "more": {
                "kid.name": str,
                "kid.age": int,
                "kid.phones.*.model": str,
                "kid.phones.*.year": int,
                "kid.phones.*.career": {"Verizon", "AT & T", "T-Mobile"},
            },
        }
        normalise(schema)
        # pprint(schema)

    def test_array_notation(self):
        # Test valid array notation
        schema = {"name": str, "active": bool, "age": int, "pets": [str], "[kids].name": str, "[kids].age": int, "[kids].grade": int}

        normalise(schema)

        expected = {"name": str, "active": bool, "age": int, "pets": [str], "kids": [{"name": str, "age": int, "grade": int}]}

        assert schema == expected

    def test_array_dict_conflict(self):
        # Test conflicting notation
        schema = {
            "name": str,
            "active": bool,
            "age": int,
            "pets": [str],
            "[kids].name": str,
            "kids.age": int,
        }

        with self.assertRaises(SchemaError) as context:
            normalise(schema)

        assert "Ambiguous schema: 'kids' is used both as array and dict pattern" in str(context.exception)


class TestWildcardValidation(TestCase):
    def test_wildcard_simple_dict(self):
        """Test that any key in dict must have string value"""
        schema = {"*": str}

        # Should pass - all values are strings
        valid_payload = {"name": "John", "city": "NYC", "country": "USA"}
        assert validate(schema, valid_payload)

        # Should fail - has non-string values
        errors = []
        invalid_payload = {"name": "John", "age": 25, "active": True}  # Not a string  # Not a string
        assert not validate(schema, invalid_payload, errors)
        assert len(errors) == 2

    def test_wildcard_nested_pattern(self):
        """Test wildcard in nested structures for dynamic keys"""
        schema = {"users": {"*": {"name": str, "age": int}}}  # Any user ID

        # Should pass - all present values match their types
        valid_payload = {
            "users": {
                "user1": {"name": "John", "age": 25},
                "user2": {"name": "Jane"},
                "user3": {"age": 40},
                "user4": {},
            }
        }
        errors = []
        assert not validate(schema, valid_payload, errors)
        assert errors == [
            "['users'] ['user2'] ['age'] is required",
            "['users'] ['user3'] ['name'] is required",
            "['users'] ['user4'] ['age'] is required",
            "['users'] ['user4'] ['name'] is required",
        ]

        # Should fail - has wrong types for present values
        errors = []
        invalid_payload = {
            "users": {
                "user1": {"name": "John", "age": "25"},
                "user2": {"name": True},
                "user3": {"age": 40},
            }
        }
        assert not validate(schema, invalid_payload, errors)
        assert errors == [
            "['users'] ['user1'] ['age'] must be integer (but '25')",
            "['users'] ['user2'] ['age'] is required",
            "['users'] ['user2'] ['name'] must be string (but True)",
            "['users'] ['user3'] ['name'] is required",
        ]

    def test_wildcard_array_elements(self):
        """Test wildcard for validating array elements with consistent structure"""
        schema = {"products": [{"id": str, "details": {"*": str}}]}  # All details must be strings

        # Should pass - all details are strings
        valid_payload = {
            "products": [
                {"id": "prod1", "details": {"color": "red", "size": "large", "material": "cotton"}},
                {"id": "prod2", "details": {"color": "blue", "weight": "150g"}},
            ]
        }
        assert validate(schema, valid_payload)

        # Should fail - non-string details
        errors = []
        invalid_payload = {
            "products": [{"id": "prod1", "details": {"color": "red", "count": 5, "inStock": True}}]
            # Should be string  # Should be string
        }
        assert not validate(schema, invalid_payload, errors)
        assert len(errors) == 2

    def test_wildcard_with_specific_keys(self):
        """Test that wildcard can't be mixed with specific keys at same level"""
        schema = {"config": {"*": str, "version": int}}  # This should cause SchemaError

        self.assertRaises(SchemaError, validate, schema, {"config": {}})


class TestArrayNotationValidation(TestCase):

    def test_normalise(self):
        schema = {
            "name": "x",
            "active": "x",
            "pets": ["x"],
            "[kids].name": "x",
            "[kids].age": "x",
            "[kids].grade": "x",
        }

        normalise(schema)

        expected = {
            "name": "x",
            "active": "x",
            "pets": ["x"],
            "kids": [
                {
                    "name": "x",
                    "age": "x",
                    "grade": "x",
                },
            ],
        }

        assert schema == expected

        schema = {
            "name": "x",
            "[children].name": "x",
            "[children].age": "x",
            "[children].[pets].type": "x",
            "[children].[pets].age": "x",
        }

        normalise(schema)

        expected = {
            "name": "x",
            "children": [
                {
                    "name": "x",
                    "age": "x",
                    "pets": [
                        {
                            "type": "x",
                            "age": "x",
                        }
                    ],
                },
            ],
        }

        assert schema == expected

    def test_validate_array_schema(self):
        # Schema using array notation
        schema = {
            "name": str,
            "active": bool,
            "pets": [str],
            "[kids].name": str,
            "[kids].age": int,
            "[kids].grade": int,
        }

        # Valid payload - with multiple kids
        payload = {
            "name": "John",
            "active": True,
            "pets": ["dog", "cat"],
            "kids": [
                {"name": "Alice", "age": 10, "grade": 5},
                {"name": "Bob", "age": 8, "grade": 3},
                {"name": "Charlie", "grade": 4, "age": 12},
            ],
        }
        errors = []
        validate(schema, payload, errors)
        print(schema, payload, errors)

        assert validate(schema, payload)

        payload = {
            "name": "John",
            "active": True,
            "pets": ["dog", "cat"],
        }
        errors = []
        validate(schema, payload, errors)
        assert not validate(schema, payload)

        # Invalid payload - wrong types
        errors = []
        invalid_payload = {
            "name": "John",
            "active": True,
            "pets": ["dog", "cat"],
            "kids": [
                {"name": "Alice", "age": "10"},
                {"name": True, "grade": "3"},
            ],
        }
        assert not validate(schema, invalid_payload, errors)
        assert errors == [
            "['kids'] [0] ['age'] must be integer (but '10')",
            "['kids'] [0] ['grade'] is required",
            "['kids'] [1] ['age'] is required",
            "['kids'] [1] ['grade'] must be integer (but '3')",
            "['kids'] [1] ['name'] must be string (but True)",
            "['kids'][0]['grade'] is required",
            "['kids'][1]['age'] is required",
        ]

        # Invalid payload - kids not an array
        errors = []
        invalid_array_payload = {
            "name": "John",
            "active": True,
            "pets": ["dog", "cat"],
            "kids": {"name": "Alice", "age": 10},
        }
        assert not validate(schema, invalid_array_payload, errors)
        assert len(errors) == 1
        assert "kids" in errors[0] and "must be list" in errors[0]

    def test_validate_nested_array_schema(self):
        schema = {
            "name": str,
            "[children].name": str,
            "[children].age": int,
            "[children].[pets].type": str,
            "[children].[pets].age": int,
        }

        payload = {
            "name": "John",
            "children": [
                {
                    "name": "Alice",
                    "age": 10,
                    "pets": [
                        {"type": "dog", "age": 5},
                        {"type": "cat", "age": 3},
                        {"type": "fish"},
                    ],
                },
                {
                    "name": "Bob",
                    "pets": [
                        {"type": "hamster"},
                    ],
                },
            ],
        }

        errors = []
        result = validate(schema, payload, errors)
        assert not result
        assert errors == [
            "['children'] [0] ['pets'] [2] ['age'] is required",
            "['children'] [0] ['pets'][2]['age'] is required",
            "['children'] [1] ['age'] is required",
            "['children'] [1] ['pets'] [0] ['age'] is required",
            "['children'] [1] ['pets'][0]['age'] is required",
            "['children'][0]['pets'][2]['age'] is required",
            "['children'][1]['age'] is required",
            "['children'][1]['pets'][0]['age'] is required",
        ]

        # Invalid payload - wrong types in nested structure
        errors = []
        invalid_payload = {
            "name": "John",
            "children": [{"name": "Alice", "age": "10", "pets": [{"type": None, "age": "5"}, {"type": "Cat", "age": "Seven"}]}],  # should be int
        }
        assert not validate(schema, invalid_payload, errors)
        assert len(errors) == 4


class TestStrongPassword(TestCase):
    def test_strong_password_validation(self):
        """Test strong password validator with default length (8)"""
        validator = strong_password()

        # Valid passwords
        self.assertTrue(validator("Password1!"))
        self.assertTrue(validator("Complex123$"))
        self.assertTrue(validator("Abcd123!@#"))

        # Invalid passwords - missing requirements
        self.assertFalse(validator("noupperno1!"))  # No uppercase
        self.assertFalse(validator("NOLOWERNO1!"))  # No lowercase
        self.assertFalse(validator("NoSpecial123"))  # No special char
        self.assertFalse(validator("NoNumber!@#"))  # No number
        self.assertFalse(validator("Short1!"))  # Too short

        # Non-string input
        self.assertFalse(validator(12345))
        self.assertFalse(validator(None))
        self.assertFalse(validator([]))

    def test_strong_password_custom_length(self):
        """Test strong password validator with custom minimum length"""
        validator = strong_password(min_len=12)

        # Valid passwords (12+ chars)
        self.assertTrue(validator("SuperStrong123!"))
        self.assertTrue(validator("VeryComplex123$#"))

        # Invalid passwords - too short
        self.assertFalse(validator("Short123!Aa"))  # 11 chars

        # Check that other requirements still apply
        self.assertFalse(validator("toolongbutnoupperno1!"))  # No uppercase
        self.assertFalse(validator("TOOLONGBUTNOLOWERNO1!"))  # No lowercase
        self.assertFalse(validator("TooLongNoSpecial123"))  # No special char
        self.assertFalse(validator("TooLongNoNumber!!!"))  # No number

    def test_strong_password_in_schema(self):
        """Test using strong_password in a schema"""
        schema = {"username": str, "password": strong_password(min_len=10)}

        # Valid payload
        valid_payload = {"username": "john_doe", "password": "SecurePass123!"}
        self.assertTrue(validate(schema, valid_payload))

        # Invalid payload
        invalid_payload = {"username": "john_doe", "password": "weak"}
        errors = []
        self.assertFalse(validate(schema, invalid_payload, errors))
        self.assertTrue(any("strong password" in err for err in errors))


class TestFieldNameAwareness(TestCase):
    def setUp(self):
        # Create a custom validator that tracks field names
        def field_tracking_validator(x, field=None):
            field_tracking_validator.last_field = field
            return isinstance(x, str)

        field_tracking_validator.msg = "field tracking validator"
        field_tracking_validator.last_field = None
        self.field_tracker = field_tracking_validator

    def test_basic_field_passing(self):
        """Test that field names are passed to basic validators"""
        schema = {"username": self.field_tracker, "email": self.field_tracker}

        payload = {"username": "john_doe", "email": "john@example.com"}

        validate(schema, payload)
        self.assertEqual(self.field_tracker.last_field, "email")

    def test_nested_field_passing(self):
        """Test that field names are passed correctly in nested structures"""
        schema = {"user": {"profile": {"name": self.field_tracker}}}

        payload = {"user": {"profile": {"name": "John Doe"}}}

        validate(schema, payload)
        self.assertEqual(self.field_tracker.last_field, "name")

    def test_array_field_passing(self):
        """Test that field names are passed correctly in arrays"""
        schema = {"users": [{"name": self.field_tracker}]}

        payload = {"users": [{"name": "John"}, {"name": "Jane"}]}

        validate(schema, payload)
        self.assertEqual(self.field_tracker.last_field, "name")

    def test_field_specific_validation(self):
        """Test a validator that changes behavior based on field name"""

        def field_specific_validator(x, field=None):
            if field == "password":
                # Require at least 8 chars for passwords
                return isinstance(x, str) and len(x) >= 8
            elif field == "username":
                # Require at least 3 chars for usernames
                return isinstance(x, str) and len(x) >= 3
            return True

        field_specific_validator.msg = "field specific validator"

        schema = {"username": field_specific_validator, "password": field_specific_validator}

        # Valid payload
        valid_payload = {"username": "joe", "password": "securepass"}  # 3 chars  # 10 chars
        self.assertTrue(validate(schema, valid_payload))

        # Invalid username (too short)
        invalid_username = {"username": "jo", "password": "securepass"}  # 2 chars
        self.assertFalse(validate(schema, invalid_username))

        # Invalid password (too short)
        invalid_password = {"username": "joe", "password": "short"}  # 5 chars
        self.assertFalse(validate(schema, invalid_password))

    def test_wildcard_field_passing(self):
        """Test that field names are passed correctly with wildcard schemas"""
        schema = {"config": {"*": self.field_tracker}}

        payload = {"config": {"setting1": "value1", "setting2": "value2"}}

        validate(schema, payload)
        self.assertEqual(self.field_tracker.last_field, "setting2")

    def test_array_notation_field_passing(self):
        """Test that field names are passed correctly with array notation"""
        schema = {"[users].name": self.field_tracker, "[users].email": self.field_tracker}

        payload = {"users": [{"name": "John", "email": "john@example.com"}, {"name": "Jane", "email": "jane@example.com"}]}

        validate(schema, payload)
        # Should receive the last field name processed
        self.assertEqual(self.field_tracker.last_field, "email")

    def test_combination_validation(self):
        """Test complex validation combining multiple field-aware validators"""

        def length_validator(min_length):
            def validate_length(x, field=None):
                if not isinstance(x, str):
                    return False
                return len(x) >= min_length

            validate_length.msg = f"at least {min_length} characters"
            return validate_length

        def field_format_validator(x, field=None):
            if field == "username":
                # Username must be alphanumeric
                return isinstance(x, str) and x.isalnum()
            elif field == "email":
                # Use built-in email validator
                return email(x)
            return True

        field_format_validator.msg = "properly formatted"

        schema = {"username": (length_validator(3), field_format_validator), "email": (length_validator(5), field_format_validator)}

        # Valid payload
        valid_payload = {"username": "john123", "email": "john@example.com"}
        self.assertTrue(validate(schema, valid_payload))

        # Invalid username (special characters)
        invalid_username = {"username": "john@123", "email": "john@example.com"}
        self.assertFalse(validate(schema, invalid_username))

        # Invalid email (wrong format)
        invalid_email = {"username": "john123", "email": "not-an-email"}
        self.assertFalse(validate(schema, invalid_email))


class TestBackwardCompatibility(TestCase):
    """Test that the field name changes don't break existing functionality"""

    def test_basic_types_still_work(self):
        """Test that basic types still work without field names"""
        schema = {"name": string, "age": integer, "contact": email}

        valid_payload = {"name": "John Doe", "age": 30, "contact": "john@example.com"}

        self.assertTrue(validate(schema, valid_payload))

        invalid_payload = {"name": 123, "age": "30", "contact": "not-an-email"}  # Should be string  # Should be integer  # Should be email

        self.assertFalse(validate(schema, invalid_payload))

    def test_existing_test_cases(self):
        """Test that existing complex validation scenarios still work"""
        schema = {"user": {"profile": {"name": string, "age": integer, "emails": [email]}}}

        valid_payload = {"user": {"profile": {"name": "John Doe", "age": 30, "emails": ["john@example.com", "doe@example.com"]}}}

        self.assertTrue(validate(schema, valid_payload))

        invalid_payload = {"user": {"profile": {"name": "John Doe", "age": 30, "emails": ["not-an-email", 123]}}}  # Invalid emails

        self.assertFalse(validate(schema, invalid_payload))


class TestNotTissue(TestCase):
    def test_basic_negation(self):
        """Test basic negation of primitive validators"""
        schema = {"field": not_(integer)}

        # These should pass since they're not integers
        self.assertTrue(validate(schema, {"field": "string"}))
        self.assertTrue(validate(schema, {"field": True}))
        self.assertTrue(validate(schema, {"field": 3.14}))
        self.assertTrue(validate(schema, {"field": None}))

        # This should fail since it is an integer
        self.assertFalse(validate(schema, {"field": 42}))

    def test_error_messages(self):
        """Test that error messages are properly formatted"""
        schema = {"field": not_(integer)}
        errors = []
        validate(schema, {"field": 42}, errors)
        self.assertIn("must be not integer", errors[0])

    def test_with_email_validator(self):
        """Test negation of email validator"""
        schema = {"field": not_(email)}

        # These should pass since they're not valid emails
        self.assertTrue(validate(schema, {"field": "not-an-email"}))
        self.assertTrue(validate(schema, {"field": "missing@tld"}))

        # This should fail since it's a valid email
        self.assertFalse(validate(schema, {"field": "test@example.com"}))

    def test_list_validation(self):
        """Test using not_ in a list schema"""
        schema = {"fields": [not_(string)]}

        # Should pass - list of non-strings
        self.assertTrue(validate(schema, {"fields": [1, 2.0, True, None]}))

        # Should fail - contains strings
        self.assertFalse(validate(schema, {"fields": [1, "string", 3]}))

    def test_nested_structures(self):
        """Test not_ in nested structures"""
        schema = {"user": {"id": not_(string), "settings": {"values": [not_(numeric)]}}}

        # Should pass
        valid_payload = {"user": {"id": 123, "settings": {"values": ["string", True, None]}}}
        self.assertTrue(validate(schema, valid_payload))

        # Should fail
        invalid_payload = {"user": {"id": "string-id", "settings": {"values": ["string", 3.14, True]}}}  # should not be string  # contains numeric
        self.assertFalse(validate(schema, invalid_payload))

    def test_field_awareness(self):
        """Test that field name is properly passed through"""

        def field_aware_validator(x, field=None):
            field_aware_validator.last_field = field
            return isinstance(x, str)

        field_aware_validator.msg = "field aware"
        field_aware_validator.last_field = None

        schema = {"username": not_(field_aware_validator)}
        validate(schema, {"username": 123})

        # Check that field name was passed through
        self.assertEqual(field_aware_validator.last_field, "username")

    def test_combining_validators(self):
        """Test using not_ with other validator combinations"""
        # Create a schema that requires values that are neither integers nor valid URLs
        schema = {"field": not_((integer, url))}

        # Should pass - neither integer nor URL
        self.assertTrue(validate(schema, {"field": "just a string"}))
        self.assertTrue(validate(schema, {"field": None}))

        # Should pass - is an integer but also failing to be an url
        self.assertTrue(validate(schema, {"field": 42}))

        schema = {"field": not_((str, url))}
        self.assertFalse(validate(schema, {"field": "https://example.com"}))

        schema = {"field": not_((str, url))}
        self.assertTrue(validate(schema, {"field": "example.com"}))

    def test_literal_values(self):
        """Test not_ with literal primitive values"""
        schema = {"field": not_(4)}

        # Should pass - not equal to 4
        self.assertTrue(validate(schema, {"field": 5}))
        self.assertTrue(validate(schema, {"field": "4"}))
        self.assertTrue(validate(schema, {"field": None}))

        # Should fail - equals 4
        self.assertFalse(validate(schema, {"field": 4}))

        # Test with string literal
        schema = {"field": not_("test")}
        self.assertTrue(validate(schema, {"field": "other"}))
        self.assertFalse(validate(schema, {"field": "test"}))

    def test_custom_validators(self):
        """Test not_ with custom validators"""

        def custom_validator(x, field=None):
            return isinstance(x, str) and x.startswith("test_")

        custom_validator.msg = "test_ prefixed string"

        schema = {"field": not_(custom_validator)}

        # Should pass - doesn't start with test_
        self.assertTrue(validate(schema, {"field": "other_prefix"}))
        self.assertTrue(validate(schema, {"field": 123}))

        # Should fail - starts with test_
        self.assertFalse(validate(schema, {"field": "test_value"}))

    def test_dotted_notation(self):
        """Test underscore with dotted notation"""
        schema = {"user.settings.[devices].status": (integer, string, numeric)}

        payload = {"user": {"settings": {"devices": [{"status": "invalid1"}, {"status": "invalid2"}]}}}

        errors = []
        validate(schema, payload, errors)

        assert errors == [
            "['user'] ['settings'] ['devices'] [0] ['status'] must be integer (but 'invalid1')",
            "['user'] ['settings'] ['devices'] [0] ['status'] must be numeric (but 'invalid1')",
            "['user'] ['settings'] ['devices'] [1] ['status'] must be integer (but 'invalid2')",
            "['user'] ['settings'] ['devices'] [1] ['status'] must be numeric (but 'invalid2')",
        ]
