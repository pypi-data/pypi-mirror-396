import re
from collections.abc import Generator
from dataclasses import dataclass

import imandra.ipl as ipl
import parsy

from agents.spec_logician.formal_spec.dsl import ipl_parser

from . import feedback
from .codegen import (
    add_propty_prefix,
    generate_function_def,
    generate_state_def,
    generate_state_enums,
)
from .feedback import ClauseLocation, FunDefLocation, ProptyInitLocation
from .ipl import IplList, IplType
from .syntax import (
    Clause,
    Feature,
    GivenPredicate,
    GivenState,
    Preamble,
    Property,
    Scenario,
    SuchThat,
    ThenProperty,
    ThenState,
    When,
    all_clauses,
    global_property_identifiers,
    has_opaque_fns,
    subpropty_identifiers_for_action,
    tokenize,
)

# --- UTILS ---


def action_identifiers(preamble: Preamble) -> set[str]:
    return {a.name for a in preamble.actions}


def subpropty_identifiers(preamble: Preamble) -> set[str]:
    result = set()
    for a in preamble.actions:
        result = result.union({p.name for p in a.local_properties})
    return result


# --- IPL VALIDATION ---


ipl_builtins = [
    "length",
    "len",
    "hd",
    "tl",
    "map",
    "add",
    "delete",
    "take",
    "app",
    "filter",
    "forall",
    "exists",
    "if",
    "then",
    "else",
    "enum",
    "record",
    "type",
    "internal",
    "action",
    "receive",
    "return",
    "case",
    "send",
    "with",
    "insert",
    "remove",
    "break",
    "for",
    "None",
    "Some",
    "messageFlows",
    "template",
    "in",
    "default",
    "true",
    "false",
    "intOfString",
    "stringOfInt",
    "take",
    "delete",
    "present",
    "toFloat",
    "toInt",
    "subset",
    "get",
    "getDefault",
    "abs",
    "strLen",
    "fresh",
    "now",
    "makeUTCTimestamp",
    "toUTCTimeOnly",
    "toMonthYear",
    "toUTCDateOnly",
    "toLocalMktDate",
    "valid",
    "rev",
    "app",
    "len",
    "ofList",
    "toList",
    "forall",
    "forall2",
    "map2",
    "exists",
    "find",
    "filter",
    "map",
]


def extract_identifiers(ipl_expr: str) -> set[str]:
    return {
        token
        for token in tokenize(ipl_expr)
        if token not in ipl_builtins and token.isidentifier()
    }


@dataclass
class ClauseExpr:
    env: list[Property]
    expr: str
    expected_ty: IplType
    location: ClauseLocation
    src_scenario: Scenario


@dataclass
class FnDefBlock:
    location: FunDefLocation


@dataclass
class ProptyInitExpr:
    location: ProptyInitLocation


class Diagnostic:
    def __init__(self, start_line, end_line, message, category, severity):
        self.start_line = start_line
        self.end_line = end_line
        self.message = message
        self.category = category
        self.severity = severity

    def __repr__(self):
        return (
            f"Diagnostic(severity={self.severity}, category='{self.category}', "
            f"lines={self.start_line}-{self.end_line}, message='{self.message}')"
        )

    @staticmethod
    def from_dict(diag):
        category = diag["code"].removeprefix(
            "org.eclipse.xtext.diagnostics.Diagnostic."
        )
        severity = diag["severity"]
        message = diag["message"]
        start_line = diag["range"]["start"]["line"]
        end_line = diag["range"]["end"]["line"]
        return Diagnostic(start_line, end_line, message, category, severity)


def collect_ipl_exprs(feature: Feature) -> list[ClauseExpr]:
    result = []
    preamble = feature.preamble
    for s_ix, sc in enumerate(feature.scenarios):
        when_clause = sc.when_clause
        when_action = next(
            (a for a in preamble.actions if a.name == when_clause.action), None
        )
        if when_action is None:
            continue
        subproperties = when_action.local_properties
        for c_ix, c in enumerate(all_clauses(sc)):
            location = ClauseLocation(scenario_ix=s_ix, clause_ix=c_ix)
            if isinstance(c, GivenPredicate):
                result.append(ClauseExpr([], c.predicate, "bool", location, sc))
            elif isinstance(c, SuchThat) and c.predicate:
                result.append(
                    ClauseExpr(subproperties, c.predicate, "bool", location, sc)
                )
            elif isinstance(c, ThenProperty):
                assigned_p = next(
                    (p for p in preamble.global_properties if p.name == c.property),
                    None,
                )
                if assigned_p:
                    result.append(
                        ClauseExpr(
                            subproperties,
                            c.expression,
                            assigned_p.ipl_type,
                            location,
                            sc,
                        )
                    )
    return result


ValidationBlock = ClauseExpr | FnDefBlock | ProptyInitExpr


def default_term_of_ty(ty: IplType) -> str:
    """
    Returns a default value for a given IPL type.
    This is used when generating validation code for opaque functions (i.e.
    function definitions that don't yet have an implementation).
    """
    if ty == "int":
        return "0"
    elif ty == "string":
        return "''"
    elif ty == "bool":
        return "false"
    elif isinstance(ty, IplList):
        return "[]"


# Bulk-validate a list of IPL expressions by generating a single IPL source
# string containing those expressions concatenated in sequence (and embedded
# into a function body so that it's syntactically correct), and sending the
# string source to the IPL validation API.
def generate_validation_model(
    preamble: Preamble, scenario_exprs: list[ClauseExpr]
) -> tuple[list[str], list[ValidationBlock], list[tuple[int, int]]] | None:
    fun_defs = preamble.fun_defs
    if len(scenario_exprs) == 0 and len(fun_defs) == 0:
        return None

    exprs = []
    ranges: list[tuple[int, int]] = []
    lines = []
    start = 0

    for i, fn in enumerate(fun_defs):
        if fn.statements == []:
            tm = default_term_of_ty(fn.return_type)
            statements = [f"return {tm}"]
        else:
            statements = fn.statements
        fn_lines = generate_function_def(
            fn.name, fn.parameters, fn.return_type, statements
        )
        ranges.append((start, start + len(fn_lines) - 1))
        fn_lines.append("")
        lines += fn_lines
        start = start + len(fn_lines)
        exprs.append(FnDefBlock(FunDefLocation(i)))

    if len(scenario_exprs) > 0:
        global_ps = global_property_identifiers(preamble)
        pre_lines = []
        pre_lines += generate_state_enums(preamble)
        pre_lines += generate_state_def(preamble, include_init=False)
        start += len(pre_lines)
        lines += pre_lines

        for i, e in enumerate(scenario_exprs):
            adjusted_expr = add_propty_prefix(e.expr, global_ps, set())
            fn_lines = generate_function_def(
                f"check_{i}", e.env, e.expected_ty, [f"return {adjusted_expr}"]
            )
            ranges.append((start, start + len(fn_lines) - 1))
            fn_lines.append("")
            lines += fn_lines
            start = start + len(fn_lines)
            exprs.append(e)

    for i, p in enumerate(preamble.global_properties):
        fn_lines = generate_function_def(
            f"check_init_val_{i}", [], p.ipl_type, [f"return {p.init_value}"]
        )
        ranges.append((start, start + len(fn_lines) - 1))
        fn_lines.append("")
        lines += fn_lines
        start = start + len(fn_lines)
        exprs.append(ProptyInitExpr(ProptyInitLocation(p.name)))

    return (lines, exprs, ranges)


def validate_parsing(
    preamble: Preamble, scenario_exprs: list[ClauseExpr]
) -> Generator[feedback.Feedback]:
    for expr in scenario_exprs:
        try:
            ipl_parser.expr.parse(expr.expr)
        except parsy.ParseError as e:
            yield feedback.IPLDiagnostic(
                severity=1,
                message=str(e),
                category="ParseError",
                location=expr.location,
            )

    for i, fn in enumerate(preamble.fun_defs):
        for stmt in fn.statements:
            try:
                ipl_parser.stmt.parse(stmt)
            except parsy.ParseError as e:
                yield feedback.IPLDiagnostic(
                    severity=1,
                    message=str(e),
                    category="ParseError",
                    location=FunDefLocation(fun_def_ix=i),
                )


def validate_ipl_exprs(
    client: ipl.Client, preamble: Preamble, scenario_exprs: list[ClauseExpr]
) -> Generator[feedback.Feedback]:
    parse_errors = list(validate_parsing(preamble, scenario_exprs))
    if len(parse_errors) > 0:
        yield from parse_errors
        return

    vm = generate_validation_model(preamble, scenario_exprs)
    if vm:
        (lines, exprs, ranges) = vm
        ipl_code = "\n".join(lines)
    else:
        return

    lsp_diagnostics = client.validate(model=ipl_code)
    diagnostics = [Diagnostic.from_dict(diag) for diag in lsp_diagnostics]
    linking_diagnostics = [d for d in diagnostics if d.category == "Linking"]
    for diag in diagnostics:
        start_line = diag.start_line
        end_line = diag.end_line
        expr_ix = next(
            (i for i, (x, y) in enumerate(ranges) if x <= start_line and end_line <= y),
            -1,
        )
        src_expr = exprs[expr_ix] if expr_ix > -1 else None
        src_location = src_expr.location if src_expr else None
        if src_location is not None:
            if start_line == end_line:
                # Since IPL errors generated by the LSP can sometimes can be
                # pretty vague, here we try to turn them into more specific,
                # fine-tuned feedback that is more relevant to the FormalSpec
                # feature being analyzed, as well as less confusing to the LLM
                # receiving the feedback.
                pattern = r"Couldn't resolve reference to Identifiable '([^']+)'"
                match = re.search(pattern, diag.message)
                if match:
                    identifier = match.group(1)
                    if isinstance(src_expr, ClauseExpr):
                        action = src_expr.src_scenario.when_clause.action
                        act_ids = subpropty_identifiers_for_action(preamble, action)
                        all_act_ids = subpropty_identifiers(preamble)
                        if identifier in act_ids:
                            found_in_subpropties = "local"
                        elif identifier in all_act_ids:
                            found_in_subpropties = "other"
                        else:
                            found_in_subpropties = "no"
                    else:
                        found_in_subpropties = "no"
                    yield feedback.IdentifierNotDeclared(
                        identifier,
                        found_in_subpropties,
                        src_location,
                    )
                else:
                    # The root origin of IPL's 'unknown type' type errors is
                    # usually some kind of parse error/unresolved identifier.
                    # We avoid reporting these diagnostics when possible, as
                    # they are pretty hard to decipher, and instead try to
                    # infer the actual issue with some heuristics.

                    handled = False

                    # checks if there are any "Linking" diagnostics on the same
                    # source line, pointing to scoping errors that are most
                    # likely the actual cause of the "unknown type" error.
                    if (
                        'expected "unknown type"' in diag.message
                        or 'was "unknown type"' in diag.message
                    ) and any(
                        diag
                        for diag in linking_diagnostics
                        if diag.start_line == start_line and diag.end_line == end_line
                    ):
                        handled = True

                    # checks if the referenced line contains bracket notation,
                    # which is likely the cause of the "unknown type" error.
                    if ('expected "unknown type"' in diag.message) and (
                        re.search(r"\w+\[\w+\]", lines[start_line]) is not None
                    ):
                        handled = True
                        yield feedback.IPLDiagnostic(
                            severity=1,
                            message="bracket syntax is not supported for this type",
                            category="TypeError",
                            location=src_location,
                        )

                    if handled:
                        print(f"Skipped IPL diagnostic: {diag}")
                    else:
                        yield feedback.IPLDiagnostic(
                            severity=diag.severity,
                            message=diag.message,
                            category=diag.category,
                            location=src_location,
                        )
            else:
                yield feedback.IPLDiagnostic(
                    severity=1,
                    message="Parse error",
                    category="Parsing",
                    location=src_location,
                )
        else:
            # IPL diagnostics originating from LLM-generated IPL code should
            # have been handled in the other branch. If we get here, it means
            # there's a critical bug in the IPL codegen functions.
            raise Exception(f"IPL diagnostic at unexpected location: {diag}")


# --- CHECKING FUNCTIONS ---

# -- Preamble --


# Check that there are no name overlaps between (global) properties and action
# subproperties.
def check_shadowings(preamble: Preamble) -> Generator[feedback.Feedback]:
    global_properties = global_property_identifiers(preamble)
    for a in preamble.actions:
        for p in a.local_properties:
            if p.name in global_properties:
                yield feedback.ProptyShadowing(a.name, p.name)


# Check that every entity declares an initial state.
def check_initial_states(preamble: Preamble) -> Generator[feedback.Feedback]:
    for e in preamble.entities:
        states = e.states
        if not any(s.is_initial for s in states):
            yield feedback.NoInitialState(e.name)


# Check that no identifiers declared in the preamble clash with IPL builtins
def check_builtin_clashes(preamble: Preamble) -> Generator[feedback.Feedback]:
    # TODO: do the same for entity names

    # Check state/builtin clashes
    for e in preamble.entities:
        for s in e.states:
            if s.name in ipl_builtins:
                err_source = f"states of entity `{e.name}`"
                yield feedback.BuiltinClash(identifier=s.name, source=err_source)

    # Check global property/builtin clashes
    for p in preamble.global_properties:
        if p.name in ipl_builtins:
            err_source = "global properties"
            yield feedback.BuiltinClash(identifier=p.name, source=err_source)

    # Check action subproperty/builtin clashes
    for a in preamble.actions:
        for p in a.local_properties:
            if p.name in ipl_builtins:
                err_source = f"subproperties of action `{a.name}`"
                yield feedback.BuiltinClash(identifier=p.name, source=err_source)


def check_preamble(preamble: Preamble) -> Generator[feedback.Feedback]:
    yield from check_shadowings(preamble)
    yield from check_initial_states(preamble)
    yield from check_builtin_clashes(preamble)


# -- Scenarios --


# Check that the provided entity and state are declared in the preamble.
def check_state_for_entity(
    scenario_ix: int, clause_ix: int, preamble: Preamble, entity: str, state: str
) -> Generator[feedback.Feedback]:
    propties = global_property_identifiers(preamble)
    e = next((e for e in preamble.entities if e.name == entity), None)
    if e:
        states = [s.name for s in e.states]
        if state not in states:
            yield feedback.StateNotDeclared(entity, state, scenario_ix, clause_ix)
    else:
        found_in_propties = entity in propties
        yield feedback.EntityNotDeclared(
            entity, found_in_propties, scenario_ix, clause_ix
        )


# Run clause-specific checks.
def check_clause(
    scenario_ix: int, clause_ix: int, preamble: Preamble, clause: Clause
) -> Generator[feedback.Feedback]:
    match clause:
        case GivenState(entity=entity, state=state):
            yield from check_state_for_entity(
                scenario_ix, clause_ix, preamble, entity, state
            )
        case When(action=action):
            # Check that the clause's action is declared in the preamble.
            actions = action_identifiers(preamble)
            if action not in actions:
                yield feedback.ActionNotDeclared(action, scenario_ix, clause_ix)
        case ThenState(entity=entity, state=state):
            yield from check_state_for_entity(
                scenario_ix, clause_ix, preamble, entity, state
            )
        case ThenProperty(property=propty):
            # Check that the clause's property is declared in the preamble.
            declared_propties = global_property_identifiers(preamble)
            declared_subpropties = subpropty_identifiers(preamble)
            if propty not in declared_propties:
                found_in_subpropties = propty in declared_subpropties
                yield feedback.AssignedProptyNotDeclared(
                    propty, found_in_subpropties, scenario_ix, clause_ix
                )


def check_then_clause_duplicates(
    scenario_ix: int, clauses: list[ThenState | ThenProperty]
) -> Generator[feedback.Feedback]:
    assigned_entities: dict[str, int] = {}
    assigned_properties: dict[str, int] = {}

    for c in clauses:
        match c:
            case ThenState(entity=e):
                if e in assigned_entities:
                    assigned_entities[e] += 1
                else:
                    assigned_entities[e] = 1
            case ThenProperty(property=p):
                if p in assigned_properties:
                    assigned_properties[p] += 1
                else:
                    assigned_properties[p] = 1

    for k, v in assigned_entities.items():
        if v > 1:
            msg = f"`Then` clause setting entity `{k}`"
            yield feedback.ClauseCountMismatch(msg, "at most 1", v, scenario_ix)
    for k, v in assigned_properties.items():
        if v > 1:
            msg = f"`Then` clause setting property `{k}`"
            yield feedback.ClauseCountMismatch(msg, "at most 1", v, scenario_ix)


def check_scenario(
    scenario_ix: int, preamble: Preamble, scenario: Scenario
) -> Generator[feedback.Feedback]:
    for i, c in enumerate(all_clauses(scenario)):
        yield from check_clause(scenario_ix, i, preamble, c)

    given_state_clauses = [
        c for c in scenario.given_clauses if isinstance(c, GivenState)
    ]

    # Check that the scenario as the correct number of Given/Then clauses,
    # as specified in the prompt.
    # TODO: consider dropping this requirement.
    if len(given_state_clauses) != 1:
        yield feedback.ClauseCountMismatch(
            "`Given` clause of type state", "1", len(given_state_clauses), scenario_ix
        )
    if len(scenario.then_clauses) < 1:
        yield feedback.ClauseCountMismatch(
            "`Then` clause", "at least 1", 0, scenario_ix
        )

    yield from check_then_clause_duplicates(scenario_ix, scenario.then_clauses)


# -- Feature --


# Checks that all scenarios passed as arguments have unique titles. This is
# because we use scenario titles to uniquely identify scenarios (and to link
# them back to the original natural language source).
def check_scenario_titles(scenarios: list[Scenario]) -> Generator[feedback.Feedback]:
    titles = {}

    for i, s in enumerate(scenarios):
        if s.title not in titles:
            titles[s.title] = []
        titles[s.title] = titles[s.title] + [i]

    for v in titles.values():
        if len(v) > 1:
            yield feedback.ScenarioTitleClash(scenario_ixs=v)


# This function checks:
# * whether an entity's states are used in the scenarios at all
# * whether every state declared in the preamble is referenced at least
#   once somewhere in the scenarios.
def check_states(feature: Feature) -> Generator[feedback.Feedback]:
    read_states: dict[str, set[str]] = {}
    assigned_states: dict[str, set[str]] = {}
    for sc in feature.scenarios:
        for c in (c for c in sc.given_clauses if isinstance(c, GivenState)):
            if c.entity not in read_states:
                read_states[c.entity] = set()
            read_states[c.entity].add(c.state)
        for c in (c for c in sc.then_clauses if isinstance(c, ThenState)):
            if c.entity not in assigned_states:
                assigned_states[c.entity] = set()
            assigned_states[c.entity].add(c.state)

    for entity in feature.preamble.entities:
        e = entity.name
        if e not in read_states and e not in assigned_states:
            yield feedback.EntityNotUsed(e)
        else:
            for s in entity.states:
                s_not_read = e not in read_states or s.name not in read_states[e]
                s_not_assigned = not s.is_initial and (
                    e not in assigned_states or s.name not in assigned_states[e]
                )
                match (s.is_initial, s_not_read, s_not_assigned):
                    case (_, True, True):
                        yield feedback.StateNotUsed(e, s.name)
                    # case (True, True, False):
                    #     yield feedback.StateNotRead(e, s.name)
                    # case (False, False, True):
                    #     yield feedback.StateNotAssigned(e, s.name)


# Check whether every property (global and local to an action) declared in the
# preamble is referenced at least once in some scenario.
def check_properties(feature: Feature) -> Generator[feedback.Feedback]:
    read_other_properties: set[str] = set()
    read_given_properties: set[str] = set()
    assigned_properties: set[str] = set()
    for sc in feature.scenarios:
        for clause in all_clauses(sc):
            if isinstance(clause, GivenPredicate):
                given_ids = extract_identifiers(clause.predicate)
                read_given_properties = read_given_properties.union(given_ids)
            elif isinstance(clause, SuchThat):
                given_ids = extract_identifiers(clause.predicate)
                read_other_properties = read_other_properties.union(given_ids)
            elif isinstance(clause, ThenProperty):
                then_ids = extract_identifiers(clause.expression)
                read_other_properties = read_other_properties.union(then_ids)
                assigned_properties.add(clause.property)

    read_properties = read_given_properties | read_other_properties

    no_opaques = not has_opaque_fns(feature.preamble)
    if no_opaques:
        for p in global_property_identifiers(feature.preamble):
            if p not in (read_properties | assigned_properties):
                yield feedback.PropertyNotUsed(p)
        for a in feature.preamble.actions:
            for p in a.local_properties:
                if p.name not in read_other_properties:
                    yield feedback.SubpropertyNotUsed(a.name, p.name)


# Check whether every action declared in the preamble is referenced at least
# once in some scenario.
def check_actions(feature: Feature) -> Generator[feedback.Feedback]:
    action_refs: set[str] = set()
    for sc in feature.scenarios:
        action_refs.add(sc.when_clause.action)

    for a in action_identifiers(feature.preamble):
        if a not in action_refs:
            yield feedback.ActionNotUsed(a)


# Check whether every function declared in the preamble is referenced at least
# once in some scenario.
def check_functions(feature: Feature) -> Generator[feedback.Feedback]:
    refd_identifiers: set[str] = set()
    for sc in feature.scenarios:
        for clause in all_clauses(sc):
            if isinstance(clause, GivenPredicate | SuchThat):
                given_ids = extract_identifiers(clause.predicate)
                refd_identifiers = refd_identifiers.union(given_ids)
            elif isinstance(clause, ThenProperty):
                then_ids = extract_identifiers(clause.expression)
                refd_identifiers = refd_identifiers.union(then_ids)
    for fn in reversed(feature.preamble.fun_defs):
        if fn.name not in refd_identifiers:
            yield feedback.FunctionNotUsed(fn.name)
        fn_ids = {id for stmt in fn.statements for id in extract_identifiers(stmt)}
        refd_identifiers = refd_identifiers.union(fn_ids)


def check_feature(client: ipl.Client, feature: Feature) -> Generator[feedback.Feedback]:
    # Run checks on preamble.
    preamble_feedback = list(check_preamble(feature.preamble))
    yield from preamble_feedback

    for i, s in enumerate(feature.scenarios):
        yield from check_scenario(i, feature.preamble, s)

    # Run whole-feature checks.
    yield from check_scenario_titles(feature.scenarios)
    yield from check_states(feature)
    yield from check_properties(feature)
    yield from check_actions(feature)
    yield from check_functions(feature)

    # Since IPL checks rely on generating valid IPL code from the preamble, we
    # only proceed if the preamble is well-formed, otherwise the codegen'd
    # preamble's validity cannot be guaranteed.
    if len(preamble_feedback) == 0:
        # Run validation checks on all embedded IPL expressions.
        scenario_exprs = collect_ipl_exprs(feature)
        yield from validate_ipl_exprs(client, feature.preamble, scenario_exprs)
    else:
        # Only run validation checks on function definitions in the preamble.
        # It's fine to do so, because those functions do not depend on other
        # preamble declarations in any way.
        yield from validate_ipl_exprs(client, feature.preamble, [])
