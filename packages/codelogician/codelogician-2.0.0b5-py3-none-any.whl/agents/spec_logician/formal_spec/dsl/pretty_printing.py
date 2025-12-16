from .ipl import (
    AssignmentStmt,
    BinOp,
    Expr,
    FnArg,
    FunctionApp,
    Identifier,
    IfThenElse,
    IplList,
    IplType,
    LambdaExpr,
    LetStmt,
    ListLiteral,
    LiteralVal,
    ReturnStmt,
    Stmt,
    Subscription,
    UnaryNot,
)
from .syntax import (
    Action,
    Clause,
    Entity,
    Feature,
    FunDef,
    GivenPredicate,
    GivenState,
    GlobalProperty,
    Preamble,
    Property,
    Scenario,
    SuchThat,
    ThenProperty,
    ThenState,
    When,
    all_clauses,
)


def pp_ipl_type(ipl_type: IplType) -> str:
    if isinstance(ipl_type, str):
        return ipl_type
    elif isinstance(ipl_type, IplList):
        pp_base_ty = pp_ipl_type(ipl_type.base_type)
        if " " in pp_base_ty:
            return f"({pp_base_ty}) list"
        else:
            return f"{pp_base_ty} list"


def pp_entity(entity: Entity) -> str:
    states = sorted(entity.states, key=lambda x: not x.is_initial)
    pprinted_states = "".join([f"{s.name} " for s in states])
    return f"entity {entity.name}" + " { " + pprinted_states + "}"


def pp_property(p: Property) -> str:
    return f"{p.name}: {pp_ipl_type(p.ipl_type)}"


def pp_action(action: Action) -> str:
    if len(action.local_properties) == 0:
        return f"action {action.name}" + " { }"

    pprinted = []
    pprinted.append(f"action {action.name}" + " {")
    for p in action.local_properties:
        pprinted.append(f"  {pp_property(p)}")
    pprinted.append("}")
    return "\n".join(pprinted)


def pp_global_property(p: GlobalProperty) -> str:
    return f"{pp_property(p)} = {p.init_value}"


def pp_state(properties: list[GlobalProperty]) -> str:
    if len(properties) == 0:
        return "internal state { }"

    pprinted = []
    pprinted.append("internal state {")
    for p in properties:
        pprinted.append(f"  {pp_global_property(p)};")
    pprinted.append("}")
    return "\n".join(pprinted)


def pp_fn_signature(fn: FunDef) -> str:
    fn_params = ", ".join(f"{p.name}: {pp_ipl_type(p.ipl_type)}" for p in fn.parameters)
    fn_return_ty = pp_ipl_type(fn.return_type)
    return f"{fn.name}({fn_params}): {fn_return_ty}"


def pp_function(fn: FunDef) -> str:
    pprinted = []
    sig = f"function {pp_fn_signature(fn)}"

    if len(fn.statements) == 0:
        return f"{sig}" + " { }"

    pprinted.append(f"{sig}" + " {")
    for stmt in fn.statements:
        pprinted.append(f"  {stmt}")
    pprinted.append("}")

    return "\n".join(pprinted)


def pp_preamble(preamble: Preamble) -> str:
    pprinted = []
    for e in preamble.entities:
        pprinted.append(pp_entity(e))
    if len(preamble.entities) > 0:
        pprinted.append("")
    for a in preamble.actions:
        pprinted.append(pp_action(a))
    if len(preamble.actions) > 0:
        pprinted.append("")
    pprinted.append(pp_state(preamble.global_properties))
    pprinted.append("")
    for fn in preamble.fun_defs:
        pprinted.append(pp_function(fn))
    return "\n".join(pprinted)


def pp_clause(clause: Clause) -> str:
    match clause:
        case GivenState(entity=entity, state=state):
            return f"Given {entity} on {state}"
        case GivenPredicate(predicate=predicate):
            return f"Given {predicate}"
        case When(action=action):
            pp_when = []
            pp_when.append(f"When {action}")
            return "\n".join(pp_when)
        case SuchThat(predicate=predicate):
            return f"SuchThat {predicate}"
        case ThenState(entity=entity, state=state):
            return f"Then {entity} on {state}"
        case ThenProperty(property=propty, expression=expr):
            return f"Then {propty} is {expr}"


def pp_scenario(scenario: Scenario) -> str:
    return "\n".join(
        [f"  Scenario: {scenario.title}"]
        + [f"    {pp_clause(c)}" for c in all_clauses(scenario)]
    )


def pp_feature(feature: Feature) -> str:
    pp = []
    pp.append(pp_preamble(feature.preamble))
    pp.append("")
    pp.append(f"Feature: {feature.title}")
    pp.append("")
    for sc in feature.scenarios:
        pp.append(pp_scenario(sc))
        pp.append("")
    return "\n".join(pp)


# Pretty printing functions for IPL expressions and statements


def pp_ipl_expr(expr: Expr) -> str:
    def needs_parens(inner_op: str, outer_op: str, is_left: bool) -> bool:
        precedence = {
            "||": 1,
            "&&": 2,
            "==": 3,
            "!=": 3,
            "<=": 3,
            "<": 3,
            ">=": 3,
            ">": 3,
            "+": 4,
            "-": 4,
            "*": 5,
            "/": 5,
        }

        inner_prec = precedence.get(inner_op, 0)
        outer_prec = precedence.get(outer_op, 0)

        if inner_prec < outer_prec:
            return True

        return inner_prec == outer_prec and not is_left

    match expr:
        case LiteralVal(val=val):
            if isinstance(val, bool):
                return "true" if val else "false"
            else:
                return str(val)

        case Identifier(id=name):
            return name

        case ListLiteral(elements=elements):
            if not elements:
                return "[]"
            element_strs = [pp_ipl_expr(elem) for elem in elements]
            return f"[{', '.join(element_strs)}]"

        case FunctionApp(name=name, args=args):
            if not args:
                return f"{name}()"
            arg_strs = [pp_ipl_fn_arg(arg) for arg in args]
            return f"{name}({', '.join(arg_strs)})"

        case BinOp(left=left, op=op, right=right):
            left_str = pp_ipl_expr(left)
            right_str = pp_ipl_expr(right)

            if isinstance(left, BinOp) and needs_parens(left.op, op, is_left=True):
                left_str = f"({left_str})"
            if isinstance(right, BinOp) and needs_parens(right.op, op, is_left=False):
                right_str = f"({right_str})"

            return f"{left_str} {op} {right_str}"

        case IfThenElse(guard=guard, then_branch=then_branch, else_branch=else_branch):
            pp_guard = pp_ipl_expr(guard)
            pp_then = pp_ipl_expr(then_branch)
            pp_else = pp_ipl_expr(else_branch)
            return f"if {pp_guard} then {pp_then} else {pp_else}"

        case Subscription(operand=operand, subscript=subscript):
            pp_subscript = pp_ipl_expr(subscript)
            return f"{operand}[{pp_subscript}]"

        case UnaryNot(operand=operand):
            pp_operand = pp_ipl_expr(operand)
            return f"!{pp_operand}"


def pp_ipl_fn_arg(arg: FnArg) -> str:
    match arg:
        case LambdaExpr(param=param, body=body):
            return f"{{{param}|{pp_ipl_expr(body)}}}"
        case _:
            return pp_ipl_expr(arg)


def pp_ipl_stmt(stmt: Stmt) -> str:
    match stmt:
        case LetStmt(identifier=name, ipl_type=typ, expr=expr):
            return f"let {name}: {pp_ipl_type(typ)} = {pp_ipl_expr(expr)}"

        case AssignmentStmt(identifier=name, expr=expr):
            return f"{name} = {pp_ipl_expr(expr)}"

        case ReturnStmt(expr=expr):
            return f"return {pp_ipl_expr(expr)}"
