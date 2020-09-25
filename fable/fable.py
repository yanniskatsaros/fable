import sys
import re
from pathlib import Path
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Union, List, IO, Callable

# compile each regex pattern once, reuse many times
SPECIFICATION_PATTERN = re.compile(r'%%\s+(\d.\d.\d)')

# parse variable declarations of the form: <type> <name> <value>
VARIABLE_DECLARATION_PATTERN = re.compile(r'^\s*(integer[\?]?|float[\?]?|string[\?]?|boolean[\?]?)\s+([a-zA-Z_\d]+)\s+(.+)$')

# parse table declarations of the form: table <name> or table+ <name>
TABLE_DECLARATION_PATTERN = re.compile(r'\s*(table[\+]?)\s+([a-zA-Z_\d]+)')

# parse values of defined `integer` types
INTEGER_PATTERN = re.compile(r'\s*(\d+)')
NULLABLE_INTEGER_PATTERN = re.compile(r'\s*(\d+|null)')

# parse values of defined `float` types
FLOAT_PATTERN = re.compile(r'\s*([\+|\-]?[\d{3}_?]+\.?[\d{3}_?]*[e|E]?[\+\-]?[\d]*)')
NULLABLE_FLOAT_PATTERN = re.compile(r'\s*([\+|\-]?[\d{3}_?]+\.?[\d{3}_?]*[e|E]?[\+\-]?[\d]*|null)')

# parse values of defined `string` types
STRING_PATTERN = re.compile(r'\s*(\".*\")')
NULLABLE_STRING_PATTERN = re.compile(r'\s*(\".*\"|null)')

# parse values of defined `boolean` types
BOOLEAN_PATTERN = re.compile(r'\s*(true|false)')
NULLABLE_BOOLEAN_PATTERN = re.compile(r'\s*(true|false|null)')

class ParsingError(Exception):
    pass

@dataclass
class Version:
    major: int
    minor: int
    patch: int

    def __str__(self):
        return f'v{self.major}.{self.minor}.{self.patch}'

    @classmethod
    def parse_specification(cls, s: str) -> Optional['Version']:
        match = SPECIFICATION_PATTERN.match(s)

        if match is None:
            return None
        
        major, minor, patch = match.group(1).split('.')

        return cls(int(major), int(minor), int(patch))

@dataclass
class Variable:
    name: str
    value: Union[int, float, str, bool, None]

@dataclass
class Table:
    name: str
    header: Optional[List[str]]
    values: List[List[Variable]]

@dataclass
class Error:
    message: str
    code: int

class ErrorCode(Enum):
    PARSING_ERROR = auto()
    NULLABLE_TYPE_ERROR = auto()
    UNKNOWN_TYPE = auto()
    TYPE_ERROR = auto()

def parse_integer(s: str) -> Union[int, Error]:
    match = INTEGER_PATTERN.match(s)
    if match is None:
        return Error(f'invalid literal for integer type: {s}', ErrorCode.TYPE_ERROR)
    return int(match.group(1))

def parse_nullable_integer(s: str) -> Union[int, None, Error]:
    match = NULLABLE_INTEGER_PATTERN.match(s)
    if match is None:
        return Error(f'invalid literal for integer type: {s}', ErrorCode.TYPE_ERROR)
    
    value = match.group(1)
    if value == 'null':
        return None
    return int(value)

def parse_float(s: str) -> Union[float, Error]:
    match = FLOAT_PATTERN.match(s)
    if match is None:
        # check for nan/infs first
        if 'nan' in s.lower():
            return float('nan')
        if 'inf' in s.lower():
            return float('inf')

        # otherwise it's really an invalid value
        return Error(f'invalid literal for float type: {s}', ErrorCode.TYPE_ERROR)

    return float(match.group(1))

def parse_nullable_float(s: str) -> Union[float, None, Error]:
    match = NULLABLE_FLOAT_PATTERN.match(s)
    if match is None:
        # check for nan/infs first
        if 'nan' in s.lower():
            return float('nan')
        if 'inf' in s.lower():
            return float('inf')

        # otherwise it's really an invalid value
        return Error(f'invalid literal for float type: {s}', ErrorCode.TYPE_ERROR)

    value = match.group(1)
    if value == 'null':
        return None
    return float(value)

def parse_string(s: str) -> Union[str, Error]:
    match = STRING_PATTERN.match(s)
    if match is None:
        return Error(f'invalid literal for string type: {s}', ErrorCode.TYPE_ERROR)
    return match.group(1).replace('"', '')

def parse_nullable_string(s: str) -> Union[int, None, Error]:
    match = NULLABLE_STRING_PATTERN.match(s)
    if match is None:
        return Error(f'invalid literal for string type: {s}', ErrorCode.TYPE_ERROR)

    value = match.group(1)
    if value == 'null':
        return None
    return value.replace('"', '')

def parse_boolean(s: str) -> Union[bool, Error]:
    match = BOOLEAN_PATTERN.match(s)
    if match is None:
        return Error(f'invalid literal for boolean type: {s}', ErrorCode.TYPE_ERROR)
    value = match.group(1)
    if value == 'true':
        return True
    return False

def parse_nullable_boolean(s: str) -> Union[int, None, Error]:
    match = NULLABLE_BOOLEAN_PATTERN.match(s)
    if match is None:
        return Error(f'invalid literal for boolean type: {s}', ErrorCode.TYPE_ERROR)
    value = match.group(1)
    if value == 'null':
        return None

    if value == 'true':
        return True
    return False

def parse_variable(type_: str, name: str, value: str) -> Union[Variable, Error]:
    parse_funcs = {
        'integer': parse_integer,
        'integer?': parse_nullable_integer,
        'float': parse_float,
        'float?': parse_nullable_float,
        'string': parse_string,
        'string?': parse_nullable_string,
        'boolean': parse_boolean,
        'boolean?': parse_nullable_boolean
    }

    pfunc = parse_funcs.get(type_)
    if pfunc is None:
        return Error(f'unknown varirable type: {type_}', ErrorCode.UNKNOWN_TYPE)

    val = pfunc(value)    
    if val is None:
        return Variable(name, None)

    if isinstance(val, Error):
        return val

    return Variable(name, val)

def parse_variable_declaration(s: str) -> Union[None, Variable, Error]:
    variable_match = VARIABLE_DECLARATION_PATTERN.match(s)
    if variable_match is None:
        return None

    type_ = variable_match.group(1)
    name = variable_match.group(2)
    value = variable_match.group(3)
    return parse_variable(type_, name, value)

def table_type_parsers(s: str) -> List[Callable]:
    parse_funcs = {
        'integer': parse_integer,
        'integer?': parse_nullable_integer,
        'float': parse_float,
        'float?': parse_nullable_float,
        'string': parse_string,
        'string?': parse_nullable_string,
        'boolean': parse_boolean,
        'boolean?': parse_nullable_boolean
    }
    types = [x.strip() for x in s.strip().split(',')]
    type_checks = [x for x in types if x in parse_funcs.keys()]

    # check for invalid type declarations in the table
    if len(type_checks) < len(types):
        msg = f'Unknown type(s) in table: {", ".join(set(types) - set(type_checks))}'
        return Error(msg, ErrorCode.UNKNOWN_TYPE)

    return [parse_funcs[t] for t in types]

def parse_table_headers(s: str) -> List[str]:
    return [x.strip().replace('"', '') for x in s.strip().split(',')]

def parse_table_row(s: str, parsers: List[Callable]) -> List[Union[int, float, str, bool, None]]:
    row = [x.strip() for x in s.strip().split(',')]
    return [parse(r) for r, parse in zip(row, parsers)]

def parse_table_declaration(s: str, io: IO) -> Union[None, Table, Error]:
    # confirm this is a correct table definition
    match = TABLE_DECLARATION_PATTERN.match(s)
    if match is None:
        return None

    has_header = False
    if match.group(1).endswith('+'):
        has_header = True

    name = match.group(2)
    # now, consume the next line to get parsers for each table type
    parsers = table_type_parsers(next(io))

    # consume the header row if it exists
    header = None
    if has_header:
        header = parse_table_headers(next(io))

    # then consume and parse each row until encountering a blank line
    s = next(io)
    values = []
    while s.strip() != '':
        try:
            row = parse_table_row(s, parsers)
        except:
            return Error(f'error parsing row: {s}', ErrorCode.PARSING_ERROR)
        values.append(row)
        try:
            s = next(io)
        except StopIteration:
            return Table(name, header, values)

    return Table(name, header, values)

def load(io: IO) -> dict:
    """
    Deserialize the contents of a text or binary Fable file (that supports `.read()`)
    to a Python `dict` using the following conversion table:

    Fable -> Python
    - string -> str
    - string? -> Optional[str]
    - integer -> int
    - integer? -> Optional[int]
    - float -> float
    - float? -> Optional[float]
    - boolean -> bool
    - boolean? -> Optional[bool]
    - table -> List[List[Union[float, int, str, bool]]]

    Parameters:
        io: a `.read()`-supporting file-like object containing a Fable document
    """
    results = {}
    errors = []

    # document frontmatter
    s = next(io)
    if s.startswith('%%'):
        # TODO: used for forward compatibility with future parsers
        version = Version.parse_specification(s)

    for s in io:
        # try parsing variable definitions
        maybe_variable = parse_variable_declaration(s)
        if maybe_variable is not None:
            if isinstance(maybe_variable, Error):
                errors.append(maybe_variable)
                continue
            
            # otherwise store the parsed key-value pair
            results[maybe_variable.name] = maybe_variable.value
            continue

        # try parsing table definitions
        if s.strip().startswith('table'):
            maybe_table = parse_table_declaration(s, io)
            if maybe_table is not None:
                if isinstance(maybe_table, Error):
                    errors.append(maybe_table)
                    continue

                # otherwise store the table
                results[maybe_table.name] = {
                    'header': maybe_table.header,
                    'values': maybe_table.values
                }

    if len(errors) != 0:
        raise ParsingError(*errors)

    return results

# example usage
if __name__ == '__main__':
    import pprint

    filepath = Path(sys.argv[1]).resolve()
    with open(filepath, 'r') as f:
        document = load(f)

    pprint.pprint(document)
