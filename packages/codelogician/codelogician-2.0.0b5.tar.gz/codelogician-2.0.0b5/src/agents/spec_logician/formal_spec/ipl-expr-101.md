# Imandra Protocol Language (IPL)

IPL is a formal language that supports creation and manipulation of expressions
of various types, including strings, integers, booleans, lists, and so on. It
also supports function application. IPL expressions are constructed by
combining literal values, operators, and functions, to create more complex
expressions.

An IPL expression can be of the following _types_:

- integer: `int`
- string: `string`
- boolean: `bool`
- linked list: `T list` for some type `T`

A string literal is any set of characters surrounded by a matching pair of
single quotes.

An integer literal is any set of consecutive digits (from 0 to 9).

A boolean literal is either `true` or `false`.

An IPL expression can also include variables, represented by identifiers. An
identifier is any string that:

- only contains alphanumeric characters or the underscore `_` symbol
- starts with an alphabetic character
- does not overlap with any IPL reserved keyword or builtin identifier

## Logical operators

Logical operators can be used to construct boolean expressions from other
boolean expressions.

The supported logical operators are:

- binary and: `&&`
- binary or: `||`
- unary not: `!`

Their use is shown below:

```
true && false

!false

(a && b) || true

!(x || y)
```

## Relational operators

Relational operators can be used to construct boolean expressions from other
expressions of any type.

The relational binary operators that are supported are:

- equality: `==`
- inequality: `!=`
- greater-than: `>`
- less-than: `<`
- greater-or-equal-than: `>=`
- less-or-equal-than: `<=`

For example:

```
"foo" == "foo"

"foo" != "bar"

2 < 3
```

## Mathematical operations

IPL expressions supports various binary mathematical operators between integer
expressions:

- addition: `+`
- subtraction: `-`
- multiplication: `*`
- division: `/`

For example:

```
1 + 2

4 / 2

5 * 5
```

### Ternary operator (if-then-else)

We can use `if-then-else` syntax to construct expressions whose value depends
on a boolean guard:

```ipl
if b then x else y
```

where `b` is an IPL expression of type `bool`, and `x` and `y` are two IPL
expressions of arbitrary but equal type. The if-then-else expression evaluates
to `x` if `b` is `true`, otherwise it evaluates to `y`.

## Function invocation

IPL expressions support function invocation, using standard function
invocation syntax:

```
func(arg1, arg2, ...)
```

The IPL expression language specifies some builtin functions. We will see some
of them in the next section about lists.

## Statements

IPL also supports _statements_, in addition to expressions. The difference
between expressions and statements is the following:

- expressions can be assigned a type and evaluate to a value of that type
- statements don't have a type, and are merely executed to produce a
  side-effect

The simplest statement is `return`, which has the side-effect of returning to
the called the value of the expression written after it:

```ipl
return <expression>
```

We also have the `let` binding statement, which has the following structure:

```ipl
let var : T = expr
```

for an identifier `var`, type `T`, and expression `expr` of type `T`. The
side-effect of a the statement above is to evaluate `expr` to a value, and bind
that value to a new variable `var`. Note that `let` bindings introduce new
variables in scope, and therefore any previous identifiers with the same name
will be shadowed.

In addition to `return` and `let`, another useful statement is _assignments_:

```ipl
var = expr
```

The side-effect of the statement above is to evaluate `expr` to a value, and
assign that value to an existing variable `var` that is present in scope. The
difference between `let` bindings and assignments is that assignments cannot
introduce new identifiers into the current scope, but only modify existing
ones.

## Lists

The IPL expression language supports linked lists. Given a type `T`, the type
of lists of elements of `T` is written as `X list`.

List types can be nested, however parentheses _MUST_ be used around the inner
list components of the full type. In particular, one must _NOT_ wrap a single
list type with parentheses.

For example:

- to express the type of lists of strings: `string list`
- to express the type of lists of lists of strings: `(string list) list`
- to express a three-dimensional integer matrix as nested lists: `((int list) list) list`

etc.

### List literals

List literals can be expressed via the `[]` notation. For example, here's a
list of integers:

```ipl
[1,2,3]
```

### List membership

We can test for list membership with the infix operator `in`:

```ipl
x in xs
```

Given a term `x` of type `T` and a list `xs` of type `T list`, then `x in xs`
is a boolean expression that is `true` if and only if `x` is contained in the
list `xs`.

### Adding elements to lists

We can construct new lists by adding an element to the head of another list,
using the builtin function `add`:

```ipl
add(x, xs)
```

Given a term `x` of type `T` and a list `xs` of type `T list`, then `add(x, xs)`
returns a new list with `x` as the head, and `xs` as the tail.

We can also concatenate two lists of the same type together, with the builtin
function `app` (for "append"):

```ipl
app(xs, ys)
```

Given two lists `xs`, `ys`, the expression above returns a new list which is
obtained by concatenating `xs` and `ys`.

### Extracting elements from lists

Lists can be deconstructed with the builtin functions `hd` and `tl`, which
extract the head and the tails of a list, respectively.

```ipl
hd(xs)
lt(xs)
```

We can also extract the prefix of a list with the builtin function `take`,
which takes an integer `n` and a list `xs` as arguments, and returns a new list
containing the first `n` elements of `xs`:

```ipl
take(n, xs)
```

### Deleting elements from lists

The builtin function `delete` can be used to remove elements from a given list,
by providing the exact element to remove.

```ipl
delete(x, xs)
```

Given a term `x` of type `T` and a list `xs` of type `T list`, then `delete(x, xs)`
returns a new list which is like `xs` but with all occurrences of `x` removed (if any).

### Length of a list

The builtin function `len` returns the integer length of a list:

```ipl
len(["foo", "bar", "baz"]) == 3
```

### Map operation on lists

We can map elements of a linked list using the builtin `map` operator, which
takes two inputs:

- a list
- an _anonymous function expression_ which indicates how to map each element of
  the list into a new one

We write anonymous function expressions as `{x | ... }`, where `x` is a
variable binder, and `...` is the _body_ of the anonymous function, that is, an
IPL expression that can contain `x` as a free variable.

Thus, we can express a map operation as follows:

```ipl
map(xs, {x|...})
```

For example, to map a list of integers to a new list where each element is
increased by one:

```ipl
map([1,2,3], {x|x + 1})
```

We can map over lists of any type. Moreover, a map operation can be used to
produce a list with a different type from the input list. For example, the
following map operation takes a list of integers and produces a list of
booleans:

```ipl
map([1,2,3], {x|x == 2})
```

### Filter operation on lists

We can filter elements from linked lists with the builtin `filter` operator, which
takes two inputs:

- a list
- a predicate, in the form of an anonymous function expression with body of type `bool`

```ipl
filter(xs, { x | ... })
```

The `filter` operation returns a new list, containing all and only the elements
of the input list that satisfy the predicate provided.

For example, to extract from an integer list `xs` all the numbers below 5:

```ipl
filter(xs, { x | x >= 5 })
```

### Quantifier predicates on lists

The IPL expression language includes the builtin operators `forall` and `exists`:

- `forall`: test whether a given boolean predicate holds for all elements of a list
- `exists` test whether a given boolean predicate holds for at least one element of a list

Both `forall` and `exists` take two arguments, with a list as the first
argument and a boolean predicate as the second, and return a boolean value. We
write the boolean predicate as an anonymous function expression with a body of
type `bool`.

```ipl
forall(xs, {x | ... })
exists(xs, {x | ... })
```

For example, the following IPL expression is `true` if and only if the integer
list `xs` contains only numbers greater than 5:

```ipl
forall(xs, {x | x > 5})
```

This following expression is `true` if and only if the string list `xs`
contains at least one string `"foo"`:

```ipl
exists(xs, {x | x == "foo"})
```
