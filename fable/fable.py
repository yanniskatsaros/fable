import sys
import re
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Union, List, IO

Value = Union[int, float, str, bool]

SPACE = 32
UNDERSCORE = 95
PERIOD = 46
EOL = 10
COMMENT = 35

@dataclass
class Version:
    major: int
    minor: int
    patch: int

    def __str__(self):
        return f'v{self.major}.{self.minor}.{self.patch}'

    @classmethod
    def parse_specification(cls, s: str) -> Optional['Version']:
        pattern = r'%%\s+(\d.\d.\d)'
        regex = re.compile(pattern)
        match = regex.match(s)

        if match is None:
            return None
        
        major, minor, patch = match.group(1).split('.')

        return cls(int(major), int(minor), int(patch))
    
@dataclass
class Variable:
    name: str
    value: Value

@dataclass
class TableMeta:
    name: str
    header: bool
    rows: int

@dataclass
class Table:
    name: str
    header: Optional[List[str]]
    values: List[List[Value]]

class Document:
    def __init__(self, d: dict):
        for k, v in d.items():
            setattr(self, k, v)
        
        if not hasattr(self, 'version'):
            setattr(self, 'version', None)

def try_cast(v: str) -> Value:
    """
    Helper method to parse integers, floats,
    booleans, and strings from a given input.

    The hierarchy of attempted cast is as follows:
    - integer
    - float
    - boolean (true, false)
    - string ("hello", 'hello', hello)
    """
    try:
        return int(v)
    except ValueError:
        pass
    
    try:
        return float(v)
    except ValueError:
        pass
    
    if v == 'true':
        return True
    
    if v == 'false':
        return False
    
    return v.replace('"', ''). replace("'", '').strip()

def extract_version(s: str) -> Optional[Version]:
    """
    Extracts the version from the given string assuming
    the input is specified as "frontmatter" using the
    %% directive.
    """
    # iterator of the input string
    s_ = iter(s)
    
    # consume and check the %% directive
    directive = next(s_), next(s_)
    if directive != ('%', '%'):
        msg = (
            'Invalid frontmatter. Missing %% directive.'
        )
        raise ValueError(msg)
        
    # discard whitespace until finding 'v'
    c = next(s_)
    while ord(c) in (SPACE, 'v'):
        c = next(s_)
    
    remainder = ''
    for c in s_:
        if ord(c) == SPACE:
            continue
        
        # don't consume the rest of the string
        if ord(c) == COMMENT:
            break
        
        remainder += c

    # extract the version number
    pat = r'[\d]+.[\d].[\d]'
    regex = re.compile(pat)
    match = regex.match(remainder)
    
    if match is None:
        return None
    
    version = match.string
    major, minor, patch = version.split('.')
    
    return Version(int(major), int(minor), int(patch))

def parse_variable(s: str) -> Optional[Variable]:
    """
    Parse a `Variable` type from a @var declaration.
    If a parsing error occurs due to an invalid match,
    the function returns `None`
    """
    pat = r'^(@var)\((.*)\)([\s]+=[\s]+\S+)'
    regex = re.compile(pat)
    match = regex.match(s)
    
    if match is None:
        return None

    name = match.group(2)
    remainder = match.group(3)
    value = remainder.split('=')[-1].strip()
    
    # hierachy: int -> float -> bool -> str
    value = try_cast(value)
    
    return Variable(name, value)

def parse_table_meta(s: str) -> Optional[TableMeta]:
    """
    Parse the metadata from a @table declaration
    required to then parse the values of the table
    values below the @table. 
    """
    pat = r'^(@table)\((.*)\)'
    regex = re.compile(pat)
    match = regex.match(s)
    
    if match is None:
        return None
    
    contents = match.group(2)
    name, remainder = contents.split(',')[0:2]

    remainder = remainder.strip()
    header = False
    if remainder.endswith('+'):
        header = True
        remainder = remainder[0:-1]

    try:
        rows = int(remainder)
    except ValueError:
        msg = (
            f'Table rows must be specified as an integer. '
            f'Found: @table({name}, {remainder})'
        )
        raise ValueError(msg)
        
    return TableMeta(name, header, rows)

def load(io: IO) -> dict:
    """
    Deserialize the contents of a text or binary Fable file (that supports `.read()`)
    to a Python `dict` using the following conversion table:

    Fable -> Python
    - string -> str
    - integer -> int
    - real -> float
    - boolean -> bool
    - table -> List[List[Union[float, int, str, bool]]]
    """
    results = {}

    # document frontmatter
    s = next(io)
    if s.startswith('%%'):
        # TODO: used for forward compatibility with future parsers
        version = extract_version(s)

    for s in io:
        if s.startswith('#'):
            # ignore any comments
            continue

        if not s.startswith('@'):
            # other stuff that we don't know so we ignore
            continue

        if s.startswith('@table'):
            meta = parse_table_meta(s)

            # consume the approprite number of rows
            rows = []
            header = None
            if meta.header:
                s = next(io)
                header = [try_cast(v) for v in s.strip().split(',')]

            for _ in range(meta.rows):
                s = next(io)
                row = [try_cast(v) for v in s.strip().split(',')]
                rows.append(row)

            table = Table(
                meta.name,
                header,
                rows
            )
            results[table.name] = {
                'header': table.header,
                'values': table.values
            }
            continue
        
        if s.startswith('@var'):
            var = parse_variable(s)
            if var is None:
                continue
            
            results[var.name] = var.value

    return results

# example usage
if __name__ == '__main__':
    import pprint

    filepath = Path(sys.argv[1]).resolve()
    with open(filepath, 'r') as f:
        document = load(f)

    pprint.pprint(document)
