from functools import reduce

from parsy import Parser, forward_declaration, regex, seq, string

from . import ipl

forbidden_ids = string("let") | string("return")

identifier = forbidden_ids.should_fail("reserved keyword") >> regex(
    "[a-zA-Z][a-zA-Z0-9_]*"
)
space = regex(r"\s+")  # non-optional whitespace
padding = regex(r"\s*")  # optional whitespace


def lexeme(p: Parser):
    return p << padding


# Expression parsers

lparen = lexeme(string("("))
rparen = lexeme(string(")"))
lbrace = lexeme(string("{"))
rbrace = lexeme(string("}"))
lbracket = lexeme(string("["))
rbracket = lexeme(string("]"))
comma = lexeme(string(","))
colon = lexeme(string(":"))
excl_mark = lexeme(string("!"))

integer = lexeme(regex(r"-?\d+")).map(int)
string_literal = lexeme(regex(r"'([^'\\]|\\.)*'"))
boolean_true = lexeme(string("true")).result(True)
boolean_false = lexeme(string("false")).result(False)
boolean = boolean_true | boolean_false
literal_val = (
    (integer | string_literal | boolean)
    .map(lambda x: ipl.LiteralVal(val=x))
    .desc("literal value")
)

add_op = lexeme(string("+"))
sub_op = lexeme(string("-"))
mul_op = lexeme(string("*"))
div_op = lexeme(string("/"))

eq_op = lexeme(string("=="))
neq_op = lexeme(string("!="))
le_op = lexeme(string("<="))
lt_op = lexeme(string("<"))
ge_op = lexeme(string(">="))
gt_op = lexeme(string(">"))

and_op = lexeme(string("&&"))
or_op = lexeme(string("||"))
in_op = lexeme(string("in"))


expr = forward_declaration()

pipe = lexeme(string("|"))
lambda_expr = seq(
    param=lbrace >> lexeme(identifier), body=pipe >> expr << rbrace
).combine_dict(ipl.LambdaExpr)

list_literal = (lbracket >> expr.sep_by(comma) << rbracket).map(
    lambda es: ipl.ListLiteral(elements=es)
)

function_arg = lambda_expr | expr
function_call = (
    seq(name=lexeme(identifier), args=lparen >> function_arg.sep_by(comma) << rparen)
    .combine_dict(ipl.FunctionApp)
    .desc("function call")
)

identifier_expr = (
    lexeme(identifier).map(lambda x: ipl.Identifier(id=x)).desc("identifier")
)

atom = forward_declaration()

subscription = (
    seq(
        operand=lexeme(identifier),
        subscript=lbracket >> expr << rbracket,
    )
    .combine_dict(ipl.Subscription)
    .desc("subscription operator")
)

unary_not = excl_mark >> atom.map(lambda e: ipl.UnaryNot(operand=e))

atom.become(
    literal_val
    | list_literal
    | function_call
    | subscription
    | unary_not
    | identifier_expr
    | (lparen >> expr << rparen)
)


# Parse left-associative operators with proper precedence
def make_binary_op_parser(operand_parser, operator_parser):
    rest_parser = seq(
        op=operator_parser,
        operand=operand_parser,
    )
    return seq(first=operand_parser, rest=rest_parser.many()).map(
        lambda d: reduce(
            lambda acc, op_val: ipl.BinOp(
                left=acc, op=op_val["op"], right=op_val["operand"]
            ),
            d["rest"],
            d["first"],
        )
        if d["rest"] != []
        else d["first"]
    )


# Operator precedence (from highest to lowest):
# 1. Multiplication and Division (*, /)
# 2. Addition and Subtraction (+, -)
# 3. Comparison and Equality (==, !=, <, <=, >, >=)
# 4. Logical AND (&&)
# 5. Logical OR (||)

mul_div_expr = make_binary_op_parser(atom, mul_op | div_op)
add_sub_expr = make_binary_op_parser(mul_div_expr, add_op | sub_op)
comparison_expr = make_binary_op_parser(
    add_sub_expr, eq_op | neq_op | le_op | lt_op | ge_op | gt_op
)
and_expr = make_binary_op_parser(comparison_expr, and_op)
or_expr = make_binary_op_parser(and_expr, or_op)
in_expr = make_binary_op_parser(or_expr, in_op)

if_keyword = lexeme(string("if"))
then_keyword = lexeme(string("then"))
else_keyword = lexeme(string("else"))

if_expr = seq(
    guard=if_keyword >> expr,
    then_branch=then_keyword >> expr,
    else_branch=else_keyword >> expr,
).combine_dict(ipl.IfThenElse)

expr.become(if_expr | in_expr)

# Statement parsers

let_keyword = lexeme(string("let"))
assign_op = lexeme(string("="))
return_keyword = lexeme(string("return"))


list_keyword = lexeme(string("list"))
ipl_type = forward_declaration()
int_type = lexeme(string("int"))
string_type = lexeme(string("string"))
bool_type = lexeme(string("bool"))
paren_type = lparen >> ipl_type << rparen
atomic_type = int_type | string_type | bool_type | paren_type
list_type_ = seq(
    base_type=atomic_type,
    type_ctor=list_keyword,
)
list_type = (
    list_type_ << regex("[a-zA-Z0-9_]+").should_fail("no more input")
).combine_dict(ipl.IplList)
ipl_type.become(list_type | atomic_type)

let_stmt = seq(
    identifier=let_keyword >> lexeme(identifier),
    ipl_type=colon >> ipl_type,
    expr=assign_op >> expr,
).combine_dict(ipl.LetStmt)

assignment_stmt = seq(
    identifier=lexeme(identifier), expr=assign_op >> expr
).combine_dict(ipl.AssignmentStmt)

return_stmt = seq(expr=return_keyword >> expr).combine_dict(ipl.ReturnStmt)

stmt = let_stmt | assignment_stmt | return_stmt
