# fable
A simple, linear, non-recursive data-interchange format designed to be easily emitted, and parsed by any language.

## Specification

The primary purpose of the `fable` format is to provide an easy way to store and transport multiple variables, and tables (in a more hygienic, CSV-like format) with required type declarations, and optional header name declarations. The goal was to create a format that could be emitted from any language as simply as possible (originally designed to be emitted from a Fortran95 codebase).

The current specification version is `0.2.0`. (The `%%` directive is provided for forward compatibility with future versions of the specification/parser.)

`example.fable`
```
%% 0.2.0
# ^specification version - can be used by parser for
# backward/forward compatability

# comments work, empty lines are ignored, extra space between
# variables and delimiters is also ignored

# key-value declaration and supported types
integer my_int 10
float my_float 3.14
boolean my_bool true
boolean my_other_bool false
string my_string "hello world"

# there are also "nullable" types as modifiers of the
# "primitive" types that can accept `null`
integer? age null
boolean? is_present null
string? name null

# these cause a parsing error, for example
# integer years null   # requires integer? declaration
# float salary null    # requires float? declaration

# float types support scientific notation, infinity, and "not a number" values
float a_num 1.4151426
float b_num +1.4151426
float c_num -1.4151426

# scientific notation
float d_num 5.61e+13
float e_num 1e06
float f_num -8.71E-4

# separators work too
float g_num 218_411.897_871

# infinity
float h_num inf
float i_num +inf
float j_num -inf

# not a number
float k_num nan
float l_num +nan
float m_num -nan

# note, this is different than nullability!
# nan and null are two different concepts
float ok_float_1 nan
float ok_float_2 14.51
# float bad_float null   # error, need to use: float?
float? ok_float_3 null   # this is the correct way
float? ok_float_4 nan    # also ok

# table declarations are similar but entries
# span over multiple rows and types are *required*
# each header name is delimited by a comma and requires quotes
# each column type follows the same rules as variables above

# table without a header
table example_table_no_header
integer,integer,integer,float,float,integer
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

# table with a header row
table+ example_table_with_header
integer,integer,integer,float,float,integer
"time","pipe_section","velocity","mass","pressure","temperature"
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

# table with some nullable columns and header
table+ students
integer,string,integer,float?
"id","name","grade","test_score"
0,"Jane Doe",2,98.1
1,"John Doe",3,null
2,"Other Doe",1,nan
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
```python
{'a_num': 1.4151426,
 'age': None,
 'b_num': 1.4151426,
 'c_num': -1.4151426,
 'd_num': 56100000000000.0,
 'e_num': 1000000.0,
 'example_table_no_header': {'header': None,
                             'values': [[0, 1, 83, 0.01, 7136.0, 36],
                                        [0, 2, 96, 0.01, 7579.0, 39],
                                        [0, 3, 95, 0.02, 7469.0, 34],
                                        [0, 4, 98, 0.02, 6227.0, 38],
                                        [0, 5, 96, 0.04, 7769.0, 40],
                                        [1, 1, 99, 0.05, 6219.0, 36],
                                        [1, 2, 89, 0.01, 6891.0, 38],
                                        [1, 3, 96, 0.05, 6926.0, 39],
                                        [1, 4, 80, 0.05, 7082.0, 35],
                                        [1, 5, 98, 0.03, 6200.0, 39]]},
 'example_table_with_header': {'header': ['time',
                                          'pipe_section',
                                          'velocity',
                                          'mass',
                                          'pressure',
                                          'temperature'],
                               'values': [[0, 1, 83, 0.01, 7136.0, 36],
                                          [0, 2, 96, 0.01, 7579.0, 39],
                                          [0, 3, 95, 0.02, 7469.0, 34],
                                          [0, 4, 98, 0.02, 6227.0, 38],
                                          [0, 5, 96, 0.04, 7769.0, 40],
                                          [1, 1, 99, 0.05, 6219.0, 36],
                                          [1, 2, 89, 0.01, 6891.0, 38],
                                          [1, 3, 96, 0.05, 6926.0, 39],
                                          [1, 4, 80, 0.05, 7082.0, 35],
                                          [1, 5, 98, 0.03, 6200.0, 39]]},
 'f_num': -0.000871,
 'g_num': 218411.897871,
 'h_num': inf,
 'i_num': inf,
 'is_present': None,
 'j_num': inf,
 'k_num': nan,
 'l_num': nan,
 'm_num': nan,
 'my_bool': True,
 'my_float': 3.14,
 'my_int': 10,
 'my_other_bool': False,
 'my_string': 'hello world',
 'name': None,
 'ok_float_1': nan,
 'ok_float_2': 14.51,
 'ok_float_3': None,
 'ok_float_4': nan,
 'students': {'header': ['id', 'name', 'grade', 'test_score'],
              'values': [[0, 'Jane Doe', 2, 98.1],
                         [1, 'John Doe', 3, None],
                         [2, 'Other Doe', 1, nan]]}}
```
