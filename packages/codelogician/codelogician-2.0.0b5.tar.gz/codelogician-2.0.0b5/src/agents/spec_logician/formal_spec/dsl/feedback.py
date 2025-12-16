from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class ClauseLocation:
    scenario_ix: int
    clause_ix: int


@dataclass(frozen=True)
class FunDefLocation:
    fun_def_ix: int


# When a preamble property `p` is initialised using some expression `e` which
# gives rise to an IPL error, `ProptyInitLocation.property` is used to refer to
# `p` as the origin of the error when reporting feedback to the LLM/user.
@dataclass(frozen=True)
class ProptyInitLocation:
    property: str


@dataclass(frozen=True)
class EntityNotDeclared:
    entity: str
    found_in_properties: bool
    scenario_ix: int
    clause_ix: int


@dataclass(frozen=True)
class StateNotDeclared:
    entity: str
    state: str
    scenario_ix: int
    clause_ix: int


@dataclass(frozen=True)
class ActionNotDeclared:
    action: str
    scenario_ix: int
    clause_ix: int


@dataclass(frozen=True)
class AssignedProptyNotDeclared:
    propty: str
    found_in_subpropties: bool
    scenario_ix: int
    clause_ix: int


@dataclass(frozen=True)
class IdentifierNotDeclared:
    identifier: str
    found_in_subpropties: Literal["no", "other", "local"]
    location: FunDefLocation | ClauseLocation | ProptyInitLocation


@dataclass(frozen=True)
class SubproptyNotDeclared:
    action: str
    subpropty: str
    scenario_ix: int
    clause_ix: int


@dataclass(frozen=True)
class EntityNotUsed:
    entity: str


@dataclass(frozen=True)
class StateNotUsed:
    entity: str
    state: str


@dataclass(frozen=True)
class StateNotRead:
    entity: str
    state: str


@dataclass(frozen=True)
class StateNotAssigned:
    entity: str
    state: str


@dataclass(frozen=True)
class PropertyNotUsed:
    property: str


@dataclass(frozen=True)
class SubpropertyNotUsed:
    action: str
    property: str


@dataclass(frozen=True)
class ActionNotUsed:
    action: str


@dataclass(frozen=True)
class FunctionNotUsed:
    fn_name: str


@dataclass(frozen=True)
class ProptyShadowing:
    action: str
    property: str


@dataclass(frozen=True)
class NoInitialState:
    entity: str


@dataclass(frozen=True)
class IPLDiagnostic:
    severity: int
    message: str
    category: str
    location: FunDefLocation | ClauseLocation | ProptyInitLocation


@dataclass(frozen=True)
class ClauseCountMismatch:
    clause: str
    expected_descr: str
    found_count: int
    scenario_ix: int


@dataclass(frozen=True)
class BuiltinClash:
    identifier: str
    source: str


@dataclass(frozen=True)
class ScenarioTitleClash:
    scenario_ixs: list[int]

    def __hash__(self):
        return hash(tuple(self.scenario_ixs))


Feedback = (
    EntityNotUsed
    | StateNotUsed
    | StateNotRead
    | StateNotAssigned
    | PropertyNotUsed
    | SubpropertyNotUsed
    | ActionNotUsed
    | FunctionNotUsed
    | ProptyShadowing
    | NoInitialState
    | EntityNotDeclared
    | AssignedProptyNotDeclared
    | IdentifierNotDeclared
    | SubproptyNotDeclared
    | ActionNotDeclared
    | StateNotDeclared
    | IPLDiagnostic
    | ClauseCountMismatch
    | BuiltinClash
    | ScenarioTitleClash
)

ENTITY_NOT_DECLARED_MSG = "in scenario #{scenario_ix}, clause #{clause_ix}: \
entity '{entity}' not declared in preamble."
STATE_NOT_DECLARED_MSG = "in scenario #{scenario_ix}, clause #{clause_ix}: \
state '{state}' of entity '{entity}' not declared in the preamble."
ACTION_NOT_DECLARED_MSG = "in scenario #{scenario_ix}, clause #{clause_ix}: \
action '{action}' not declared in preamble."
ASSIGNED_PROPTY_NOT_DECLARED_MSG = "in scenario #{scenario_ix}, clause #{clause_ix}: \
property '{propty}' not declared in preamble."
SCENARIO_ID_NOT_DECLARED_MSG = "in {location}: identifier '{id}' not declared \
in preamble."
ID_NOT_DECLARED_MSG = "in {location}: identifier '{id}' not in scope."
SUBPROPTY_NOT_DECLARED_MSG = "in scenario #{scenario_ix}, clause #{clause_ix}: \
subproperty '{subpropty}' of action '{action}' not declared in preamble."
ENTITY_NOT_USED_MSG = "entity '{entity}' is declared in the preamble \
but not used anywhere."
STATE_NOT_USED_MSG = "state '{state}' of entity '{entity}' is declared in the preamble \
but not used anywhere in a scenario."
STATE_NOT_USED_HINT = "Consider whether you forgot to use this state in some scenario. \
If not, consider using other states and removing `{state}` altogether."
STATE_NOT_READ_MSG = "state '{state}' of entity '{entity}' is declared initial \
in the preamble, but it's not used in a `Given` clause of type state anywhere."
STATE_NOT_READ_HINT = "Consider using other states and removing `{state}` altogether."
STATE_NOT_ASSIGNED_MSG = "state '{state}' of entity '{entity}' is not initial, \
but it's never assigned in a `Then` clause of type state."
STATE_NOT_ASSIGNED_HINT = "Consider whether you forgot to use this state \
in some scenario. If not, consider using other states and removing \
`{state}` altogether."
PROPERTY_NOT_USED_MSG = "property '{property}' is declared in the preamble \
but not used anywhere in a scenario."
PROPERTY_NOT_USED_HINT = "Consider whether you forgot to use this state \
in some scenario. If not, consider using other properties and removing \
`{property}` altogether."
SUBPROPERTY_NOT_USED_MSG = "subproperty '{property}' of action '{action}' \
is declared in the preamble but not used anywhere in a scenario."
SUBPROPERTY_NOT_USED_HINT = "Consider using other subproperties and removing \
`{property}` altogether."
ACTION_NOT_USED_MSG = "action '{action}' is declared in the preamble \
but not used in a `When` clause anywhere."
FUNCTION_NOT_USED_MSG = "function `{name}` is declared in the preamble \
but not used in a Scenario anywhere."
PROPTY_SHADOWING_MSG = "subproperty '{property}' of action '{action}' \
is shadowing a global property with the same name."
PROPTY_SHADOWING_HINT = "Consider whether you actually need this subproperty. \
If you do, then choose a different name."
NO_INITIAL_STATE_MSG = "no initial state declared for entity '{entity}'."
IPL_DIAGNOSTIC_MSG = "in {location}: IPL {diag_ty}: {message}"
ENTITY_IN_PROPTIES_MSG = "`{entity}` is declared as a property in the preamble."
ENTITY_IN_PROPTIES_HINT = "Should this be a `Given` clause of type predicate?"
ASSIGNED_P_IN_SUBP_MSG = "`{propty}` is declared as a subproperty of an \
action in the preamble."
ASSIGNED_P_IN_SUBP_HINT = "Should it be declared as a property instead?"
ID_IN_OTHER_SUBP_MSG = "in scenario #{scenario_ix}, clause #{clause_ix}: \
identifier `{id}` cannot be used here, because it is declared in the preamble \
as a subproperty of an action that is not mentioned in this scenario"
ID_IN_LOCAL_SUBP_MSG = "in scenario #{scenario_ix}, clause #{clause_ix}: \
identifier `{id}` cannot be used here, because it is declared in the preamble \
as a subproperty of this scenario's action."
ID_IN_LOCAL_SUBP_HINT = "Should this be a `SuchThat` clause instead?"
CLAUSE_COUNT_MISMATCH_MSG = "in scenario #{scenario_ix}: \
wrong number of {clause}. Expected {expected} but found {found}"
BUILTIN_CLASH_MSG = "Identifier `{identifier}` of {source} clashes with \
builtin IPL identifier of the same name."
BUILTIN_CLASH_HINT = "Use a different name."
SCENARIO_CLASH_MSG = "scenarios at indices {ixs} have the same title."
SCENARIO_CLASH_HINT = "Use a different, unique title for all of them."


def pp_location(location: FunDefLocation | ClauseLocation | ProptyInitLocation) -> str:
    match location:
        case FunDefLocation(fun_def_ix):
            ix = fun_def_ix + 1
            return f"function definition #{ix}"
        case ClauseLocation(scenario_ix, clause_ix):
            s_ix = scenario_ix + 1
            c_ix = clause_ix + 1
            return f"scenario #{s_ix}, clause #{c_ix}"
        case ProptyInitLocation(p):
            return f"initialization of property '{p}'"


def with_hint(msg: str, hint: str, for_llm: bool) -> str:
    if for_llm:
        return msg + " " + hint
    else:
        return msg


def pp_feedback(feedback: Feedback, for_llm=True) -> str:
    match feedback:
        case EntityNotDeclared(entity, found_in_properties, scenario_ix, clause_ix):
            scenario_ix = scenario_ix + 1
            clause_ix = clause_ix + 1
            msg = ENTITY_NOT_DECLARED_MSG.format(
                scenario_ix=scenario_ix, clause_ix=clause_ix, entity=entity
            )
            if found_in_properties:
                msg2 = with_hint(
                    ENTITY_IN_PROPTIES_MSG.format(entity=entity),
                    ENTITY_IN_PROPTIES_HINT,
                    for_llm,
                )
                msg = msg + " " + msg2
            return msg
        case StateNotDeclared(entity, state, scenario_ix, clause_ix):
            scenario_ix = scenario_ix + 1
            clause_ix = clause_ix + 1
            return STATE_NOT_DECLARED_MSG.format(
                state=state, entity=entity, scenario_ix=scenario_ix, clause_ix=clause_ix
            )
        case ActionNotDeclared(action, scenario_ix, clause_ix):
            scenario_ix = scenario_ix + 1
            clause_ix = clause_ix + 1
            return ACTION_NOT_DECLARED_MSG.format(
                action=action, scenario_ix=scenario_ix, clause_ix=clause_ix
            )
        case AssignedProptyNotDeclared(
            propty, found_in_subpropties, scenario_ix, clause_ix
        ):
            scenario_ix = scenario_ix + 1
            clause_ix = clause_ix + 1
            msg = ASSIGNED_PROPTY_NOT_DECLARED_MSG.format(
                propty=propty, scenario_ix=scenario_ix, clause_ix=clause_ix
            )
            if found_in_subpropties:
                msg2 = with_hint(
                    ASSIGNED_P_IN_SUBP_MSG.format(propty=propty),
                    ASSIGNED_P_IN_SUBP_HINT,
                    for_llm,
                )
                msg = msg + " " + msg2
            return msg
        case IdentifierNotDeclared(
            identifier, "local", ClauseLocation(scenario_ix, clause_ix)
        ):
            scenario_ix = scenario_ix + 1
            clause_ix = clause_ix + 1
            return with_hint(
                ID_IN_LOCAL_SUBP_MSG.format(
                    id=identifier,
                    scenario_ix=scenario_ix,
                    clause_ix=clause_ix,
                ),
                ID_IN_LOCAL_SUBP_HINT,
                for_llm,
            )
        case IdentifierNotDeclared(
            identifier, "other", ClauseLocation(scenario_ix, clause_ix)
        ):
            scenario_ix = scenario_ix + 1
            clause_ix = clause_ix + 1
            return ID_IN_OTHER_SUBP_MSG.format(
                id=identifier,
                scenario_ix=scenario_ix,
                clause_ix=clause_ix,
            )
        case IdentifierNotDeclared(identifier, _, location):
            pp_loc = pp_location(location)
            if isinstance(location, ClauseLocation):
                return SCENARIO_ID_NOT_DECLARED_MSG.format(
                    id=identifier, location=pp_loc
                )
            else:
                return ID_NOT_DECLARED_MSG.format(id=identifier, location=pp_loc)
        case SubproptyNotDeclared(action, subpropty, scenario_ix, clause_ix):
            scenario_ix = scenario_ix + 1
            clause_ix = clause_ix + 1
            return SUBPROPTY_NOT_DECLARED_MSG.format(
                subpropty=subpropty,
                action=action,
                scenario_ix=scenario_ix,
                clause_ix=clause_ix,
            )
        case EntityNotUsed(entity):
            return ENTITY_NOT_USED_MSG.format(entity=entity)
        case StateNotUsed(entity, state):
            return with_hint(
                STATE_NOT_USED_MSG.format(state=state, entity=entity),
                STATE_NOT_USED_HINT.format(state=state),
                for_llm,
            )
        case StateNotRead(entity, state):
            return with_hint(
                STATE_NOT_READ_MSG.format(state=state, entity=entity),
                STATE_NOT_READ_HINT.format(state=state),
                for_llm,
            )
        case StateNotAssigned(entity, state):
            return with_hint(
                STATE_NOT_ASSIGNED_MSG.format(state=state, entity=entity),
                STATE_NOT_ASSIGNED_HINT.format(state=state),
                for_llm,
            )
        case PropertyNotUsed(property):
            return with_hint(
                PROPERTY_NOT_USED_MSG.format(property=property),
                PROPERTY_NOT_USED_HINT.format(property=property),
                for_llm,
            )
        case SubpropertyNotUsed(action, property):
            return with_hint(
                SUBPROPERTY_NOT_USED_MSG.format(property=property, action=action),
                SUBPROPERTY_NOT_USED_HINT.format(property=property, action=action),
                for_llm,
            )
        case ActionNotUsed(action):
            return ACTION_NOT_USED_MSG.format(action=action)
        case FunctionNotUsed(fn_name):
            return FUNCTION_NOT_USED_MSG.format(name=fn_name)
        case ProptyShadowing(action, property):
            return with_hint(
                PROPTY_SHADOWING_MSG.format(property=property, action=action),
                PROPTY_SHADOWING_HINT,
                for_llm,
            )
        case NoInitialState(entity):
            return NO_INITIAL_STATE_MSG.format(entity=entity)
        case IPLDiagnostic(severity, message, _, location):
            diag_ty = "error" if severity == 1 else "warning"
            return IPL_DIAGNOSTIC_MSG.format(
                diag_ty=diag_ty,
                message=message,
                location=pp_location(location),
            )
        case ClauseCountMismatch(clause, expected, found, scenario_ix):
            scenario_ix = scenario_ix + 1
            return CLAUSE_COUNT_MISMATCH_MSG.format(
                clause=clause, expected=expected, found=found, scenario_ix=scenario_ix
            )
        case BuiltinClash(identifier, source):
            return with_hint(
                BUILTIN_CLASH_MSG.format(identifier=identifier, source=source),
                BUILTIN_CLASH_HINT,
                for_llm,
            )
        case ScenarioTitleClash(scenario_ixs):
            ixs = ", ".join([str(i) for i in scenario_ixs])
            return with_hint(
                SCENARIO_CLASH_MSG.format(ixs=ixs),
                SCENARIO_CLASH_HINT,
                for_llm,
            )
