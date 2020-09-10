# fable
A simple, linear, non-recursive data-interchange format designed to be easily emitted, and parsed by any language.

## Specification

The primary purpose of the `fable` format is to provide an easy way to store and transport multiple variables, and tables (in CSV format) with optional header name declarations. The goal was to create a format that could be emitted from any language as simply as possible (originally designed to be emitted from a Fortran95 codebase).

The current specification version is `v0.1.0`. (The `%%` directive is provided for forward compatibility with future versions of the specification/parser.)

`example.fable`
```
%% v0.1.0

# comments work, empty lines are ignored

# we declare things of interest using @ tags
# there are two supported tags, @var and @table

# variable declaration and supported types
@var(my_integer) = 10          # integer
@var(my_string) = hello world  # string   
@var(my_float) = 3.14          # real
@var(my_bool) = true           # boolean

# the following are all valid strings
@var(a_string) = hello world
@var(b_string) = "hello world"
@var(c_string) = 'hello world'

# table declarations

# a table with 5 rows of values, and no headers
# table values are parsed like a CSV file
@table(my_table_no_header, 5)
0,1,3.13141,14.109123
1,1,3.13141,14.109123
2,1,3.13141,14.109123
3,1,3.13141,14.109123
4,1,3.13141,14.109123

# table declaration with 5 rows of values, with headers (using the +)
# table values are parsed like a CSV file
@table(my_table_with_header, 5+)
time,pipe_section,velocity,temperature
0,1,3.13141,14.109123
1,1,3.13141,14.109123
2,1,3.13141,14.109123
3,1,3.13141,14.109123
4,1,3.13141,14.109123
```

## Parsers

The `fable` format is designed to be language agnostic and easily parsed by any language.

### Python

The following parser is built in Python and provides a familiar interface and almost identical usage to the builtin `json` library.

```python
import fable

# load and parse the example file shown in the specification
with open('example.fable', 'r') as f:
    document = fable.load(f)
    
print(document)
```
```
{'a_string': 'hello',
 'b_string': 'hello',
 'c_string': 'hello',
 'my_bool': True,
 'my_float': 3.14,
 'my_integer': 10,
 'my_string': 'hello',
 'my_table_no_header': {'header': None,
                        'values': [[0, 1, 3.13141, 14.109123],
                                   [1, 1, 3.13141, 14.109123],
                                   [2, 1, 3.13141, 14.109123],
                                   [3, 1, 3.13141, 14.109123],
                                   [4, 1, 3.13141, 14.109123]]},
 'my_table_with_header': {'header': ['time',
                                     'pipe_section',
                                     'velocity',
                                     'temperature'],
                          'values': [[4, 1, 3.13141, 14.109123],
                                     [0, 1, 3.13141, 14.109123],
                                     [1, 1, 3.13141, 14.109123],
                                     [2, 1, 3.13141, 14.109123],
                                     [3, 1, 3.13141, 14.109123],
                                     [4, 1, 3.13141, 14.109123]]}}
```
