from decimal import Decimal
from unittest import TestCase

from tissuebox import SchemaError, normalise, sort_unique, is_valid_schema, validate, validate as v
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
        assert "1 must be list" in errors

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
        assert "5 must be multiple of 2" in e

        e = []
        assert not validate(s, 11, e)
        assert "11 must be multiple of 2" in e
        assert "11 must be less than 10" in e

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
        expected = [
            "['active'] must be boolean (but 'Yes')",
            "['age'] must be integer (but '38')",
            "['name'] must be string (but 50)",
            "['pets'][0] must be string (but 1)",
            "['pets'][1] must be string (but 2)",
        ]
        assert expected == e

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
        assert e == ["['kids'][1]['grade'] must be integer (but None)"]

        # Try adding a different value other than 'male' or 'female'
        e = []
        payload["kids"][1]["sex"] = "f"
        assert not validate(schema, payload, e)
        assert "['kids'][1]['sex'] must be either Female or Male (but f)" in e


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
            "['users']['user2']['age'] is required",
            "['users']['user3']['name'] is required",
            "['users']['user4']['age'] is required",
            "['users']['user4']['name'] is required",
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
            "['users']['user1']['age'] must be integer (but '25')",
            "['users']['user2']['age'] is required",
            "['users']['user2']['name'] must be string (but True)",
            "['users']['user3']['name'] is required",
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
        """
        0 = {str} "['kids'][0]['age'] must be integer (but '10')"
        1 = {str} "['kids'][0]['grade'] is required"
        2 = {str} "['kids'][1]['age'] is required"
        3 = {str} "['kids'][1]['grade'] must be integer (but '3')"
        4 = {str} "['kids'][1]['name'] must be string (but True)"
        """
        assert len(errors) == 5

        # Invalid payload - kids not an array
        errors = []
        invalid_array_payload = {
            "name": "John",
            "active": True,
            "pets": ["dog", "cat"],
            "kids": {"name": "Alice", "age": 10},  # Should be array, not dict
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
        assert len(errors) == 3
        assert errors == [
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


from unittest import TestCase
from tissuebox.basic import strong_password
from tissuebox import validate


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
