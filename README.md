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

# a table with 10 rows of values, and no headers
# table values are parsed like a CSV file
@table(my_table_no_header, 10)
0,1,93,0.04,7149,37
0,2,94,0.01,7440,34
0,3,89,0.02,6307,39
0,4,98,0.02,6031,39
0,5,82,0.03,6991,35
1,1,81,0.03,6217,37
1,2,84,0.03,6903,36
1,3,89,0.05,7982,37
1,4,80,0.01,6328,40
1,5,90,0.02,7677,38

# table declaration with 10 rows of values, with headers (using the +)
# table values are parsed like a CSV file
@table(my_table_with_header, 10+)
time,pipe_section,velocity,mass,pressure,temperature
0,1,83,0.01,7136,36
0,2,96,0.01,7579,39
0,3,95,0.02,7469,34
0,4,98,0.02,6227,38
0,5,96,0.04,7769,40
1,1,99,0.05,6219,36
1,2,89,0.01,6891,38
1,3,96,0.05,6926,39
1,4,80,0.05,7082,35
1,5,98,0.03,6200,39
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
                        'values': [[0, 1, 93, 0.04, 7149, 37],
                                   [0, 2, 94, 0.01, 7440, 34],
                                   [0, 3, 89, 0.02, 6307, 39],
                                   [0, 4, 98, 0.02, 6031, 39],
                                   [0, 5, 82, 0.03, 6991, 35],
                                   [1, 1, 81, 0.03, 6217, 37],
                                   [1, 2, 84, 0.03, 6903, 36],
                                   [1, 3, 89, 0.05, 7982, 37],
                                   [1, 4, 80, 0.01, 6328, 40],
                                   [1, 5, 90, 0.02, 7677, 38]]},
 'my_table_with_header': {'header': ['time',
                                     'pipe_section',
                                     'velocity',
                                     'mass',
                                     'pressure',
                                     'temperature'],
                          'values': [[0, 1, 83, 0.01, 7136, 36],
                                     [0, 2, 96, 0.01, 7579, 39],
                                     [0, 3, 95, 0.02, 7469, 34],
                                     [0, 4, 98, 0.02, 6227, 38],
                                     [0, 5, 96, 0.04, 7769, 40],
                                     [1, 1, 99, 0.05, 6219, 36],
                                     [1, 2, 89, 0.01, 6891, 38],
                                     [1, 3, 96, 0.05, 6926, 39],
                                     [1, 4, 80, 0.05, 7082, 35],
                                     [1, 5, 98, 0.03, 6200, 39]]}}
```
