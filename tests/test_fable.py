from math import isnan, isinf

from fable.fable import (
    Version,
    Variable,
    Error,
    ErrorCode,
    parse_variable_declaration
)

class TestVersion:
    def test_version_specification_parser(self):
        s = '%% 0.2.0'
        version = Version.parse_specification(s)
        assert version == Version(0, 2, 0)

class TestIntegerDeclarations:
    def test_generic_integer(self):
        s = 'integer my_int 10'
        result = parse_variable_declaration(s)
        assert result == Variable('my_int', 10)

    def test_nullable_integer_1(self):
        s = 'integer? my_int 10'
        result = parse_variable_declaration(s)
        assert result == Variable('my_int', 10)

    def test_nullable_integer_2(self):
        s = 'integer? my_int null'
        result = parse_variable_declaration(s)
        assert result == Variable('my_int', None)

    def test_insignificant_whitespace(self):
        s = '  integer   my_int     10    # plus a comment'
        result = parse_variable_declaration(s)
        assert result == Variable('my_int', 10)

    def test_downcast_float_to_int(self):
        s = 'integer my_int 10.15'
        result = parse_variable_declaration(s)
        assert result == Variable('my_int', 10)

    def test_catch_type_error_1(self):
        s = 'integer my_int "hello world"'
        result = parse_variable_declaration(s)
        assert result.code == ErrorCode.TYPE_ERROR

    def test_catch_type_error_2(self):
        s = 'integer my_int "1995"'
        result = parse_variable_declaration(s)
        assert result.code == ErrorCode.TYPE_ERROR

class TestFloatDeclarations:
    def test_generic_float(self):
        s = 'float num 4'
        result = parse_variable_declaration(s)
        assert result == Variable('num', 4.0)

    def test_nullable_float(self):
        s = 'float? num null'
        result = parse_variable_declaration(s)
        assert result == Variable('num', None)

    def test_catch_null_type_error(self):
        s = 'float num null'
        result = parse_variable_declaration(s)
        assert result.code == ErrorCode.NULLABLE_TYPE_ERROR

    def test_catch_parsing_error(self):
        s = 'float num # woops forgot the value'
        result = parse_variable_declaration(s)
        assert result.code == ErrorCode.PARSING_ERROR

    def test_catch_type_error(self):
        s = 'float num "hello world"'
        result = parse_variable_declaration(s)
        assert result.code == ErrorCode.TYPE_ERROR

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
            result = parse_variable_declaration(nan)
            assert isnan(result.value)

    def test_all_infs(self):
        infs = [
            'float num inf',
            'float num +inf',
            'float num -inf'
        ]
        for inf in infs:
            result = parse_variable_declaration(inf)
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
            result = parse_variable_declaration(s)
            assert result == Variable('num', 14.51)

        cases = [
            'float num +0.001451',
            'float num +1.451E-03',
            'float num +1.451e-03'
        ]
        for s in cases:
            result = parse_variable_declaration(s)
            assert result == Variable('num', 0.001451)

    def test_nullable_positive_signed_floats(self):
        cases = [
            'float? num +14.51',
            'float? num +1.451E01',
            'float? num +1.451E+01',
            'float? num +1.451e01',
            'float? num +1.451e+01',
        ]
        for s in cases:
            result = parse_variable_declaration(s)
            assert result == Variable('num', 14.51)

        cases = [
            'float? num +0.001451',
            'float? num +1.451E-03',
            'float? num +1.451e-03'
        ]
        for s in cases:
            result = parse_variable_declaration(s)
            assert result == Variable('num', 0.001451)

    def test_negative_signed_floats(self):
        cases = [
            'float num -14.51',
            'float num -1.451E01',
            'float num -1.451E+01',
            'float num -1.451e01',
            'float num -1.451e+01'
        ]
        for s in cases:
            result = parse_variable_declaration(s)
            assert result == Variable('num', -14.51)

        cases = [
            'float num -0.001451',
            'float num -1.451E-03',
            'float num -1.451e-03'
        ]
        for s in cases:
            result = parse_variable_declaration(s)
            assert result == Variable('num', -0.001451, False)

    def test_nullable_negative_signed_floats(self):
        cases = [
            'float? num -14.51',
            'float? num -1.451E01',
            'float? num -1.451E+01',
            'float? num -1.451e01',
            'float? num -1.451e+01'
        ]
        for s in cases:
            result = parse_variable_declaration(s)
            assert result == Variable('num', -14.51)

        cases = [
            'float? num -0.001451',
            'float? num -1.451E-03',
            'float? num -1.451e-03'
        ]
        for s in cases:
            result = parse_variable_declaration(s)
            assert result == Variable('num', -0.001451)

    def test_separator_notation_1(self):
        s = 'float num 281_979'
        result = parse_variable_declaration(s)
        assert result == Variable('num', 281979.0)

    def test_separator_notation_2(self):
        s = 'float num 281_979.441_512'
        result = parse_variable_declaration(s)
        assert result == Variable('num', 281979.441512)

    def test_separator_notation_3(self):
        # weird, but technically possible
        s = 'float num 28_19_79.44_15_12'
        result = parse_variable_declaration(s)
        assert result == Variable('num', 281979.441512)

class TestStringDeclarations:
    def test_generic_string(self):
        s = 'string message "hello world"'
        result = parse_variable_declaration(s)
        assert result == Variable('message', 'hello world')

    def test_generic_string_with_comment(self):
        s = 'string message "  . (451)-hello eVery_one "  # weird string'
        result = parse_variable_declaration(s)
        assert result == Variable('message', '  . (451)-hello eVery_one ')

    def test_nullable_generic_string(self):
        s = 'string? message null'
        result = parse_variable_declaration(s)
        assert result == Variable('message', None)

    def test_catch_null_type_error(self):
        s = 'string message null'
        result = parse_variable_declaration(s)
        assert result.code == ErrorCode.NULLABLE_TYPE_ERROR

    def test_catch_parsing_error(self):
        s = 'string message # woops forgot the value'
        result = parse_variable_declaration(s)
        assert result.code == ErrorCode.PARSING_ERROR

    def test_catch_type_error(self):
        s = 'string message 14.15'
        result = parse_variable_declaration(s)
        assert result.code == ErrorCode.TYPE_ERROR

class TestBooleanDeclarations:
    def test_generic_boolean(self):
        s = 'boolean is_happy true'
        result = parse_variable_declaration(s)
        assert result == Variable('is_happy', True)

    def test_generic_boolean_with_comment(self):
        s = 'boolean is_happy true   # comment'
        result = parse_variable_declaration(s)
        assert result == Variable('is_happy', True)

    def test_nullable_generic_boolean(self):
        s = 'boolean? is_happy null'
        result = parse_variable_declaration(s)
        assert result == Variable('is_happy', None)

    def test_catch_null_type_error(self):
        s = 'boolean is_happy null'
        result = parse_variable_declaration(s)
        assert result.code == ErrorCode.NULLABLE_TYPE_ERROR

    def test_catch_parsing_error(self):
        s = 'boolean is_happy # woops forgot the rest'
        result = parse_variable_declaration(s)
        assert result.code == ErrorCode.PARSING_ERROR

    def test_catch_type_error(self):
        s = 'boolean is_happy 14.51'
        result = parse_variable_declaration(s)
        assert result.code == ErrorCode.TYPE_ERROR
