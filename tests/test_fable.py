from math import isnan, isinf

from fable.fable import (
    Version,
    Parser,
    Integer,
    Float,
    String,
    Boolean,
    Error,
    ErrorCode,
)

class TestVersion:
    def test_version_specification_parser(self):
        s = '%% 0.2.0'
        version = Version.parse_specification(s)
        assert version == Version(0, 2, 0)

class TestIntegerParser:
    def test1(self):
        """Test generic integer declaration"""
        s = 'integer my_int 10'
        integer = Parser.parse_integer(s)
        assert integer == Integer('my_int', 10, False)

    def test2(self):
        """Test nullable integer type"""
        s = 'integer? my_int 10'
        integer = Parser.parse_integer(s)
        assert integer == Integer('my_int', 10, True)

    def test3(self):
        """Test nullable integer type"""
        s = 'integer? my_int null'
        integer = Parser.parse_integer(s)
        assert integer == Integer('my_int', None, True)

    def test4(self):
        """Test insignificant extra whitespace and trailing comment"""
        s = ' integer   my_int   165  # hello comment   \n'
        integer = Parser.parse_integer(s)
        assert integer == Integer('my_int', 165, False)

    def test5(self):
        """Test explicit downcast from float -> integer"""
        s = 'integer my_int 10.19814'
        integer = Parser.parse_integer(s)
        assert integer == Integer('my_int', 10, False)

    def test6(self):
        """Test parsing error occurs"""
        s = 'integer my_int "hello world"'
        result = Parser.parse_integer(s)
        assert result.code == ErrorCode.PARSING_ERROR

    def test7(self):
        """Test parsing error occurs"""
        s = 'integer my_int "1995"'
        result = Parser.parse_integer(s)
        assert result.code == ErrorCode.PARSING_ERROR

class TestFloatParser:
    def test_generic_float(self):
        s = 'float num 4'
        result = Parser.parse_float(s)
        assert result == Float('num', 4.0, False)

    def test_nullable_float(self):
        s = 'float? num null'
        result = Parser.parse_float(s)
        assert result == Float('num', None, True)

    def test_catch_null_type_error(self):
        s = 'float num null'
        result = Parser.parse_float(s)
        assert result.code == ErrorCode.NULLABLE_TYPE_ERROR

    def test_catch_parsing_error(self):
        s = 'float num # woops forgot the value'
        result = Parser.parse_float(s)
        assert result.code == ErrorCode.PARSING_ERROR

    def test_all_nans(self):
        nans = [
            'float num nan',
            'float num NaN',
            'float num NaN%',
            'float num NAN',
            'float num NaNQ',
            'float num NaNS',
            'float num qNaN',
            'float num sNaN',
            'float num 1.#SNAN',
            'float num 1.#QNAN',
            'float num +nan.0'
        ]
        for nan in nans:
            result = Parser.parse_float(nan)
            assert isnan(result.value)

    def test_all_infs(self):
        infs = [
            'float num inf',
            'float num +inf',
            'float num -inf'
        ]
        for inf in infs:
            result = Parser.parse_float(inf)
            assert isinf(result.value)

    def test_positive_signed_floats(self):
        cases = [
            'float num +14.51',
            'float num +1.451E01',
            'float num +1.451E+01',
            'float num +1.451e01',
            'float num +1.451e+01'
        ]
        for s in cases:
            result = Parser.parse_float(s)
            assert result == Float('num', 14.51, False)

        cases = [
            'float num +0.001451',
            'float num +1.451E-03',
            'float num +1.451e-03'
        ]
        for s in cases:
            result = Parser.parse_float(s)
            assert result == Float('num', 0.001451, False)

    def test_nullable_positive_signed_floats(self):
        cases = [
            'float? num +14.51',
            'float? num +1.451E01',
            'float? num +1.451E+01',
            'float? num +1.451e01',
            'float? num +1.451e+01',
        ]
        for s in cases:
            result = Parser.parse_float(s)
            assert result == Float('num', 14.51, True)

        cases = [
            'float? num +0.001451',
            'float? num +1.451E-03',
            'float? num +1.451e-03'
        ]
        for s in cases:
            result = Parser.parse_float(s)
            assert result == Float('num', 0.001451, True)

    def test_negative_signed_floats(self):
        cases = [
            'float num -14.51',
            'float num -1.451E01',
            'float num -1.451E+01',
            'float num -1.451e01',
            'float num -1.451e+01'
        ]
        for s in cases:
            result = Parser.parse_float(s)
            assert result == Float('num', -14.51, False)

        cases = [
            'float num -0.001451',
            'float num -1.451E-03',
            'float num -1.451e-03'
        ]
        for s in cases:
            result = Parser.parse_float(s)
            assert result == Float('num', -0.001451, False)

    def test_nullable_negative_signed_floats(self):
        cases = [
            'float? num -14.51',
            'float? num -1.451E01',
            'float? num -1.451E+01',
            'float? num -1.451e01',
            'float? num -1.451e+01'
        ]
        for s in cases:
            result = Parser.parse_float(s)
            assert result == Float('num', -14.51, True)

        cases = [
            'float? num -0.001451',
            'float? num -1.451E-03',
            'float? num -1.451e-03'
        ]
        for s in cases:
            result = Parser.parse_float(s)
            assert result == Float('num', -0.001451, True)

    def test_separator_notation_1(self):
        s = 'float num 281_979'
        result = Parser.parse_float(s)
        assert result == Float('num', 281979, False)

    def test_separator_notation_2(self):
        s = 'float num 281_979.441_512'
        result = Parser.parse_float(s)
        assert result == Float('num', 281979.441512, False)

    def test_separator_notation_3(self):
        # weird, but technically possible
        s = 'float num 28_19_79.44_15_12'
        result = Parser.parse_float(s)
        assert result == Float('num', 281979.441512, False)

class TestStringParser:
    def test_generic_string(self):
        s = 'string message "hello world"'
        result = Parser.parse_string(s)
        assert result == String('message', 'hello world', False)

    def test_generic_string_with_comment(self):
        s = 'string message "  . (451)-hello eVery_one "  # weird string'
        result = Parser.parse_string(s)
        assert result == String('message', '  . (451)-hello eVery_one ', False)

    def test_nullable_generic_string(self):
        s = 'string? message null'
        result = Parser.parse_string(s)
        assert result == String('message', None, True)

    def test_catch_null_type_error(self):
        s = 'string message null'
        result = Parser.parse_string(s)
        assert result.code == ErrorCode.NULLABLE_TYPE_ERROR

    def test_catch_parsing_error(self):
        s = 'string message # woops forgot the value'
        result = Parser.parse_string(s)
        assert result.code == ErrorCode.PARSING_ERROR

class TestBooleanParser:
    def test_generic_boolean(self):
        s = 'boolean is_happy true'
        result = Parser.parse_boolean(s)
        assert result == Boolean('is_happy', True, False)

    def test_generic_boolean_with_comment(self):
        s = 'boolean is_happy true   # comment'
        result = Parser.parse_boolean(s)
        assert result == Boolean('is_happy', True, False)

    def test_nullable_generic_boolean(self):
        s = 'boolean? is_happy null'
        result = Parser.parse_boolean(s)
        assert result == Boolean('is_happy', None, True)

    def test_catch_null_type_error(self):
        s = 'boolean is_happy null'
        result = Parser.parse_boolean(s)
        assert result.code == ErrorCode.NULLABLE_TYPE_ERROR

    def test_catch_parsing_error(self):
        s = 'boolean is_happy # woops forgot the rest'
        result = Parser.parse_boolean(s)
        assert result.code == ErrorCode.PARSING_ERROR
