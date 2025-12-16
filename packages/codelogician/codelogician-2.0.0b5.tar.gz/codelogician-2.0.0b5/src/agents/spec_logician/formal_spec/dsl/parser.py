from dataclasses import dataclass

from parsy import Parser, regex, seq, string

from agents.spec_logician.formal_spec.dsl import ipl_parser
from agents.spec_logician.formal_spec.dsl.pretty_printing import pp_ipl_stmt

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
    State,
    SuchThat,
    ThenProperty,
    ThenState,
    When,
)


@dataclass
class SourceFile:
    preamble_content: str
    feature_content: str


def extract_preamble_and_feature(content: str) -> SourceFile:
    lines = content.strip().splitlines()

    preamble_lines = []
    feature_lines = []

    in_feature = False
    for line in lines:
        if in_feature:
            if line == "" or line.startswith(" "):
                feature_lines.append(line)
            else:
                preamble_lines.append(line)
                in_feature = False
        else:
            if line.strip().startswith("Feature"):
                feature_lines.append(line)
                in_feature = True
            else:
                preamble_lines.append(line)

    preamble_content = "\n".join(preamble_lines)
    feature_content = "\n".join(feature_lines)

    return SourceFile(
        preamble_content=preamble_content,
        feature_content=feature_content,
    )


def make_scenario(title: str, clauses: list[Clause]) -> Scenario:
    given_clauses = []
    when_clause = None
    such_that_clauses = []
    then_clauses = []

    for clause in clauses:
        if isinstance(clause, GivenState | GivenPredicate):
            given_clauses.append(clause)
        elif isinstance(clause, When):
            when_clause = clause
        elif isinstance(clause, SuchThat):
            such_that_clauses.append(clause)
        elif isinstance(clause, ThenState | ThenProperty):
            then_clauses.append(clause)

    if when_clause is None:
        raise ValueError("Scenario must have a When clause")

    return Scenario(
        title=title,
        given_clauses=given_clauses,
        when_clause=when_clause,
        such_that_clauses=such_that_clauses,
        then_clauses=then_clauses,
    )


# Parsers


def lexeme(p: Parser):
    return p << whitespace


identifier = regex("[a-zA-Z][a-zA-Z0-9_]*")
any_but_nl = regex(r"[^\n]+")
any_but_nl_opt = regex(r"[^\n]*")
newline = string("\n")
space = regex(r"\s+")  # non-optional whitespace
padding = regex(r"\s*")  # optional whitespace
whitespace = regex(r"\s*")
lparen = lexeme(string("("))
rparen = lexeme(string(")"))
lbrace = lexeme(string("{"))
rbrace = lexeme(string("}"))
colon = lexeme(string(":"))
semicolon = lexeme(string(";"))
comma = lexeme(string(","))
equal_sign = lexeme(string("="))
entity_keyword = lexeme(string("entity"))
action_keyword = lexeme(string("action"))

entity = seq(
    name=entity_keyword >> identifier << padding << lbrace,
    states=(identifier << space)
    .many()
    .map(lambda xs: [State(name=x, is_initial=i == 0) for i, x in enumerate(xs)])
    << rbrace,
).combine_dict(Entity)

property = seq(
    name=identifier << padding << colon, ipl_type=ipl_parser.ipl_type
).combine_dict(Property)

action = seq(
    name=action_keyword >> identifier << padding << lbrace,
    local_properties=property.many() << rbrace,
).combine_dict(Action)

global_property = seq(
    name=identifier << padding << colon,
    ipl_type=ipl_parser.ipl_type << equal_sign,
    init_value=(regex(r"[^;]*")).map(lambda s: s.rstrip()) << semicolon,
).combine_dict(GlobalProperty)

internal_keyword = lexeme(string("internal"))
state_keyword = lexeme(string("state"))
state = internal_keyword >> state_keyword >> lbrace >> global_property.many() << rbrace

function_keyword = lexeme(string("function"))
fn_stmt = ipl_parser.stmt.map(lambda s: pp_ipl_stmt(s))
function = seq(
    name=function_keyword >> lexeme(identifier),
    parameters=lparen >> property.sep_by(comma) << rparen,
    return_type=colon >> ipl_parser.ipl_type,
    statements=lbrace >> fn_stmt.many() << rbrace,
).combine_dict(FunDef)

preamble = (entity | action | state | function).many()

non_nl_ws = regex(r"[^\S\n]*")
feature_keyword = lexeme(string("Feature"))
scenario_keyword = lexeme(string("Scenario"))
given_keyword = lexeme(string("Given"))
on_keyword = lexeme(string("on"))
is_keyword = lexeme(string("is"))
when_keyword = lexeme(string("When"))
then_keyword = lexeme(string("Then"))
suchthat_keyword = lexeme(string("SuchThat"))

given_state_clause = seq(
    entity=given_keyword >> lexeme(identifier),
    state=on_keyword >> lexeme(identifier),
).combine_dict(GivenState)
given_predicate_clause = seq(
    predicate=given_keyword >> any_but_nl << padding
).combine_dict(GivenPredicate)
when_clause = seq(action=when_keyword >> lexeme(identifier)).combine_dict(When)
suchthat_clause = seq(predicate=suchthat_keyword >> any_but_nl << padding).combine_dict(
    SuchThat
)
then_state_clause = seq(
    entity=then_keyword >> lexeme(identifier),
    state=on_keyword >> lexeme(identifier),
).combine_dict(ThenState)
then_property_clause = seq(
    property=then_keyword >> lexeme(identifier),
    expression=is_keyword >> any_but_nl << padding,
).combine_dict(ThenProperty)
clause = (
    given_state_clause
    | given_predicate_clause
    | when_clause
    | suchthat_clause
    | then_state_clause
    | then_property_clause
)
scenario = seq(
    title=scenario_keyword >> string(":") >> any_but_nl_opt << padding,
    clauses=clause.at_least(1),
).map(lambda d: make_scenario(d["title"].strip(), d["clauses"]))

feature = seq(
    title=feature_keyword >> colon >> any_but_nl << newline << space,
    scenarios=scenario.many(),
)


def parse_all(content: str):
    extr = extract_preamble_and_feature(content)
    pr_raw = preamble.parse(extr.preamble_content.strip())
    ft = feature.parse(extr.feature_content.strip())

    entities = []
    actions = []
    global_properties = []
    fun_defs = []

    for x in pr_raw:
        if isinstance(x, Entity):
            entities.append(x)
        elif isinstance(x, Action):
            actions.append(x)
        elif isinstance(x, list):
            global_properties = x
        elif isinstance(x, FunDef):
            fun_defs.append(x)

    pr = Preamble(
        entities=entities,
        actions=actions,
        global_properties=global_properties,
        fun_defs=fun_defs,
    )

    return Feature(title=ft["title"], preamble=pr, scenarios=ft["scenarios"])
