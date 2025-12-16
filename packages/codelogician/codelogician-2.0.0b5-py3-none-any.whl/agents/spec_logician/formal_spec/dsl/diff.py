from collections.abc import Callable, Generator
from dataclasses import dataclass
from difflib import unified_diff
from typing import Generic, TypeVar

from agents.spec_logician.formal_spec.dsl.pretty_printing import (
    pp_action,
    pp_entity,
    pp_function,
    pp_global_property,
    pp_property,
    pp_scenario,
)
from agents.spec_logician.formal_spec.dsl.syntax import (
    Action,
    Entity,
    Feature,
    FunDef,
    GlobalProperty,
    Preamble,
    Scenario,
)

T = TypeVar("T")


@dataclass(frozen=True)
class DictDiff(Generic[T]):  # noqa: UP046
    added: list[T]
    removed: list[T]
    modified: list[tuple[T, T]]


@dataclass(frozen=True)
class Addition:
    description: str
    new_content: str


@dataclass(frozen=True)
class Deletion:
    description: str


@dataclass(frozen=True)
class Modification:
    description: str
    diff_content: str


Edit = Addition | Deletion | Modification


def do_diff(lines1: list[str], lines2: list[str]) -> list[str]:
    return list(unified_diff(lines1, lines2))[3:]


def compute_dict_diff(dict1: dict[str, T], dict2: dict[str, T]) -> DictDiff[T]:
    added: list[T] = []
    removed: list[T] = []
    modified: list[tuple[T, T]] = []

    keys1 = set(dict1.keys())
    keys2 = set(dict2.keys())

    for key in keys2 - keys1:
        added.append(dict2[key])

    for key in keys1 - keys2:
        removed.append(dict1[key])

    for key in keys1 & keys2:
        old_value = dict1[key]
        new_value = dict2[key]
        if old_value != new_value:
            modified.append((old_value, new_value))

    return DictDiff(added=added, removed=removed, modified=modified)


def mk_edits(
    diff: DictDiff[T],
    mk_addition: Callable[[T], Edit],
    mk_deletion: Callable[[T], Edit],
    mk_modification: Callable[[T, T], Edit],
) -> Generator[Edit]:
    for add in diff.added:
        yield mk_addition(add)
    for removal in diff.removed:
        yield mk_deletion(removal)
    for modif in diff.modified:
        yield mk_modification(modif[0], modif[1])


def get_entities_edits(preamble1: Preamble, preamble2: Preamble) -> Generator[Edit]:
    def mk_entity_modification(e1: Entity, e2: Entity) -> Edit:
        states1 = [s.name for s in e1.states]
        states2 = [s.name for s in e2.states]
        diff = "\n".join(do_diff(states1, states2))
        return Modification(
            description=f"states list of entity `{e1.name}`",
            diff_content=diff,
        )

    entities1 = {e.name: e for e in preamble1.entities}
    entities2 = {e.name: e for e in preamble2.entities}
    diff = compute_dict_diff(entities1, entities2)
    yield from mk_edits(
        diff,
        lambda e: Addition(description=f"entity `{e.name}`", new_content=pp_entity(e)),
        lambda e: Deletion(description=f"entity `{e.name}`"),
        mk_entity_modification,
    )


def get_actions_edits(preamble1: Preamble, preamble2: Preamble) -> Generator[Edit]:
    def mk_action_modification(a1: Action, a2: Action) -> Edit:
        props1 = [pp_property(p) for p in a1.local_properties]
        props2 = [pp_property(p) for p in a2.local_properties]
        diff = "\n".join(do_diff(props1, props2))
        return Modification(
            description=f"local properties of action `{a1.name}`",
            diff_content=diff,
        )

    actions1 = {a.name: a for a in preamble1.actions}
    actions2 = {a.name: a for a in preamble2.actions}
    diff = compute_dict_diff(actions1, actions2)
    yield from mk_edits(
        diff,
        lambda a: Addition(description=f"action `{a.name}`", new_content=pp_action(a)),
        lambda a: Deletion(description=f"action `{a.name}`"),
        mk_action_modification,
    )


def get_global_properties_edits(
    preamble1: Preamble, preamble2: Preamble
) -> Generator[Edit]:
    def mk_gp_modification(p1: GlobalProperty, p2: GlobalProperty) -> Edit:
        diff = "\n".join(
            do_diff(
                pp_global_property(p1).splitlines(), pp_global_property(p2).splitlines()
            )
        )
        return Modification(
            description=f"global property `{p1.name}`",
            diff_content=diff,
        )

    props1 = {gp.name: gp for gp in preamble1.global_properties}
    props2 = {gp.name: gp for gp in preamble2.global_properties}
    diff = compute_dict_diff(props1, props2)
    yield from mk_edits(
        diff,
        lambda p: Addition(
            description=f"global property `{p.name}`", new_content=pp_global_property(p)
        ),
        lambda p: Deletion(description=f"global property `{p.name}`"),
        mk_gp_modification,
    )


def get_functions_edits(preamble1: Preamble, preamble2: Preamble) -> Generator[Edit]:
    def mk_fn_modification(fn1: FunDef, fn2: FunDef) -> Edit:
        diff = "\n".join(
            do_diff(pp_function(fn1).splitlines(), pp_function(fn2).splitlines())
        )
        return Modification(
            description=f"function definition `{fn1.name}`",
            diff_content=diff,
        )

    fns1 = {fn.name: fn for fn in preamble1.fun_defs}
    fns2 = {fn.name: fn for fn in preamble2.fun_defs}
    diff = compute_dict_diff(fns1, fns2)
    yield from mk_edits(
        diff,
        lambda fn: Addition(
            description=f"function definition `{fn.name}`",
            new_content=pp_function(fn),
        ),
        lambda fn: Deletion(description=f"function definition `{fn.name}`"),
        mk_fn_modification,
    )


def get_preamble_edits(preamble1: Preamble, preamble2: Preamble) -> Generator[Edit]:
    yield from get_entities_edits(preamble1, preamble2)
    yield from get_actions_edits(preamble1, preamble2)
    yield from get_global_properties_edits(preamble1, preamble2)
    yield from get_functions_edits(preamble1, preamble2)


def get_scenarios_edits(
    scenarios1: list[Scenario], scenarios2: list[Scenario]
) -> Generator[Edit]:
    def mk_scenario_modification(s1: Scenario, s2: Scenario) -> Edit:
        diff = "\n".join(
            do_diff(pp_scenario(s1).splitlines(), pp_scenario(s2).splitlines())
        )
        return Modification(
            description=f"scenario titled `{s1.title}`",
            diff_content=diff,
        )

    scs1 = {s.title: s for s in scenarios1}
    scs2 = {s.title: s for s in scenarios2}
    diff = compute_dict_diff(scs1, scs2)
    yield from mk_edits(
        diff,
        lambda s: Addition(
            description=f"scenario titled `{s.title}`",
            new_content=pp_scenario(s),
        ),
        lambda s: Deletion(description=f"scenario titled `{s.title}`"),
        mk_scenario_modification,
    )


def diff_features(feature1: Feature, feature2: Feature) -> list[Edit]:
    preamble_edits = list(get_preamble_edits(feature1.preamble, feature2.preamble))
    scenario_edits = list(get_scenarios_edits(feature1.scenarios, feature2.scenarios))
    return preamble_edits + scenario_edits


# Pretty-printing

addition_template = """
* ADDED: {description}

```
{content}
```
"""

modification_template = """
* MODIFIED: {description}

Diff details:

```
{content}
```
"""


def pp_edit(e: Edit) -> str:
    match e:
        case Addition(description, new_content):
            return addition_template.format(
                description=description, content=new_content
            ).strip()
        case Deletion(description):
            return f"* REMOVED: {description}"

        case Modification(description, diff_content):
            return modification_template.format(
                description=description, content=diff_content
            ).strip()


def pp_edits(es: list[Edit]) -> str:
    return "\n\n".join([pp_edit(e) for e in es])
