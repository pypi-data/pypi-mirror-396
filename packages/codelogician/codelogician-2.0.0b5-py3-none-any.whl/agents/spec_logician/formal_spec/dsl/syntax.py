from __future__ import annotations

from pydantic import BaseModel, Field

from .ipl import IplType


class State(BaseModel):
    name: str = Field(description="Name of the state")
    is_initial: bool = Field(description="Flag indicating whether the state is initial")


class Entity(BaseModel):
    name: str = Field(description="Name of the entity")
    states: list[State] = Field(description="List of states for the entity")


class Property(BaseModel):
    name: str = Field(description="Name of the property")
    ipl_type: IplType = Field(description="IPL type of the property")


class GlobalProperty(Property):
    init_value: str = Field(description="Initialisation value for the property")


class Action(BaseModel):
    name: str = Field(description="Name of the action")
    local_properties: list[Property] = Field(
        description="List of subproperties that are local to this action"
    )


class FunDef(BaseModel):
    name: str = Field(description="Name of the function being defined")
    parameters: list[Property] = Field(
        description="List of parameters for this function definition"
    )
    return_type: IplType = Field(
        description="IPL type of the values returned by this function"
    )
    statements: list[str] = Field(
        description="List of IPL statements that constitute the body of this function"
    )


class Preamble(BaseModel):
    entities: list[Entity] = Field(description="List of entities")
    actions: list[Action] = Field(description="List of actions")
    global_properties: list[GlobalProperty] = Field(
        description="List of global properties"
    )
    fun_defs: list[FunDef] = Field(description="List of function definitions")


def entity_identifiers(preamble: Preamble) -> set[str]:
    return {e.name for e in preamble.entities}


class GivenState(BaseModel):
    entity: str = Field(
        description="Entity identifier for this Given clause of type state"
    )
    state: str = Field(
        description="State identifier for this Given clause of type state"
    )


class GivenPredicate(BaseModel):
    predicate: str = Field(
        description="String-encoded boolean IPL expression for this Given clause"
    )


class When(BaseModel):
    action: str = Field(description="Action identifier for this When clause")


class SuchThat(BaseModel):
    predicate: str = Field(
        description="String-encoded boolean IPL expression for this SuchThat clause"
    )


class ThenState(BaseModel):
    entity: str = Field(
        description="Entity identifier for this Then clause of type state"
    )
    state: str = Field(
        description="State identifier for this Then clause of type state"
    )


class ThenProperty(BaseModel):
    property: str = Field(
        description="Property identifier for this Then clause of type property"
    )
    expression: str = Field(
        description="String-encoded IPL expression for this Then clause"
    )


Clause = GivenState | GivenPredicate | When | SuchThat | ThenState | ThenProperty


class Scenario(BaseModel):
    title: str = Field(description="Title of the scenario")
    given_clauses: list[GivenState | GivenPredicate] = Field(
        description="List of `Given` clauses of this scenario"
    )
    when_clause: When = Field(description="`When` clause of this scenario")
    such_that_clauses: list[SuchThat] = Field(
        description="List of `SuchThat` clauses of this scenario"
    )
    then_clauses: list[ThenState | ThenProperty] = Field(
        description="List of `Then` clauses of this scenario"
    )


class Feature(BaseModel):
    title: str = Field(description="The title of the Formal Feature")
    preamble: Preamble = Field(description="The Formal Spec's preamble section")
    scenarios: list[Scenario] = Field(
        description="List of scenarios for this Formal Feature."
    )


# --- UTILS ---


def all_clauses(sc: Scenario) -> list[Clause]:
    result: list[Clause] = []
    for c in sc.given_clauses:
        result.append(c)
    result.append(sc.when_clause)
    for c in sc.such_that_clauses:
        result.append(c)
    for c in sc.then_clauses:
        result.append(c)
    return result


def global_property_identifiers(preamble: Preamble) -> set[str]:
    return {p.name for p in preamble.global_properties}


def subpropty_identifiers_for_action(preamble: Preamble, action_id: str) -> set[str]:
    action = next((a for a in preamble.actions if a.name == action_id), None)
    if action:
        return {p.name for p in action.local_properties}
    else:
        return set()


# Since we only care about alphanumeric tokens, this function only tries to
# properly isolate those, while other non-alphanumeric characters are lumped
# together.
#
# The function should preserve whitespace in the output, so that `str ==
# ''.join(tokenize(str))`.
def tokenize(ipl_expr: str) -> list[str]:
    tokens = []
    alphanum_mode = False
    current = ""
    for char in ipl_expr:
        if char.isalnum() or char == "_":
            if not alphanum_mode:
                alphanum_mode = True
                tokens.append(current)
                current = ""
            current += char
        else:
            if alphanum_mode:
                alphanum_mode = False
                tokens.append(current)
                current = ""
            current += char
    if current:
        tokens.append(current)
    return [t for t in tokens if t != ""]


def has_opaque_fns(preamble: Preamble) -> bool:
    return any(len(fn.statements) == 0 for fn in preamble.fun_defs)
