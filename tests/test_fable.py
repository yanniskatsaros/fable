from fable.fable import (
    Version,
    Parser,
    Integer,
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