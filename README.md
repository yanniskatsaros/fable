# fable
A simple linear, non-recursive data-interchange format designed to be easily emitted, and parsed by any language.

## Specification

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
@var(my_float) = 3.14          # float
@var(my_bool) = true           # boolean

# the following are all valid strings
@var(a_string) = hello world
@var(b_string) = "hello world"
@var(c_string) = 'hello world'

# table declarations

# a table with 5 rows of values, and no headers
# table values are parsed like a CSV file
@table(my_table, 5)
0,1,3.13141,14.109123
1,1,3.13141,14.109123
2,1,3.13141,14.109123
3,1,3.13141,14.109123
4,1,3.13141,14.109123

# table declaration with 5 rows of values, with headers (using the +)
# table values are parsed like a CSV file
@table(my_table, 5+)
time,pipe_section,velocity,temperature
0,1,3.13141,14.109123
1,1,3.13141,14.109123
2,1,3.13141,14.109123
3,1,3.13141,14.109123
4,1,3.13141,14.109123
```
