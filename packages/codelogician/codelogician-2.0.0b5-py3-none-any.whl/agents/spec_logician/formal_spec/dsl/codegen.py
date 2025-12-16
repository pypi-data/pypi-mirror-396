import textwrap

from agents.spec_logician.formal_spec.dsl.pretty_printing import pp_ipl_type

from .syntax import (
    Feature,
    FunDef,
    GivenPredicate,
    GivenState,
    IplType,
    Preamble,
    Property,
    ThenProperty,
    ThenState,
    global_property_identifiers,
    subpropty_identifiers_for_action,
    tokenize,
)

flow_template = textwrap.indent(
    textwrap.dedent(
        """\
        {flow_name} {{
          template [{template}]
        }}
        """
    ),
    "  ",
)


message_flow_template = textwrap.dedent(
    """\
messageFlows {{
  {flows}
}}
"""
)


def render_st_ctor(entity: str, state: str) -> str:
    return f"{entity}_state.{state}"


def add_propty_prefix(ipl_expr: str, global_ps: set[str], local_ps: set[str]) -> str:
    # This works because we make sure that global and local properties have
    # distinct names. This is enforced in [checking.check_shadowings].
    def process_token(s):
        if s in global_ps:
            return f"state.{s}"
        elif s in local_ps:
            return f"a.{s}"
        else:
            return s

    tokens = tokenize(ipl_expr)
    return "".join([process_token(t) for t in tokens])


def generate_state_enums(preamble: Preamble) -> list[str]:
    lines = []
    for e in preamble.entities:
        lines.append(f"enum {e.name}_state" + " {")
        for s in e.states:
            lines.append(f"  {s.name}")
        lines.append("}")
        lines.append("")
    return lines


def generate_state_def(preamble: Preamble, include_init: bool) -> list[str]:
    lines = []
    lines.append("internal state {")
    for entity in preamble.entities:
        e = entity.name
        st = next((s for s in entity.states if s.is_initial), None)
        if st:
            lines.append(f"  {e} : {e}_state = {render_st_ctor(e, st.name)};")
        else:
            lines.append(f"  {e} : {e}_state;")
    for p in preamble.global_properties:
        if include_init:
            lines.append(f"  {p.name} : {pp_ipl_type(p.ipl_type)} = {p.init_value};")
        else:
            lines.append(f"  {p.name} : {pp_ipl_type(p.ipl_type)};")
    lines.append("}")
    lines.append("")
    return lines


def generate_function_def(
    name: str,
    params: list[Property],
    return_type: IplType,
    statements: list[str],
) -> list[str]:
    params_str = ", ".join([f"{p.name}: {pp_ipl_type(p.ipl_type)}" for p in params])
    lines = []
    lines.append(f"function {name}({params_str}): {pp_ipl_type(return_type)}" + " {")
    for stmt in statements:
        lines.append(f"  {stmt}")
    lines.append("}")
    return lines


def generate_functions(fun_defs: list[FunDef]) -> list[str]:
    lines = []
    for fn in fun_defs:
        lines += generate_function_def(
            fn.name, fn.parameters, fn.return_type, fn.statements
        )
    return lines


def generate_base_ipl(feature: Feature) -> str:
    """
    We generate common IPL from the `feature`.

    However, the IPL needed for unsat analysis and for
    region decomposition is slightly different. We consolidate the
    common components here. Then we can specialize to unsat and to
    decomp in separate functions.

    Because this is the common bit, it contains _no_ message flows.
    """
    lines = []
    global_ps = global_property_identifiers(feature.preamble)

    lines += generate_state_enums(feature.preamble)
    lines += generate_state_def(feature.preamble, include_init=True)
    lines += generate_functions(feature.preamble.fun_defs)

    # Generate actions and their validation/receive statements
    transitions = {}
    for sc in feature.scenarios:
        when_clause = sc.when_clause
        act = when_clause.action
        local_ps = subpropty_identifiers_for_action(feature.preamble, act)
        preconds = []
        for c in (c for c in sc.given_clauses if isinstance(c, GivenState)):
            preconds.append(f"state.{c.entity} == {render_st_ctor(c.entity, c.state)}")
        for c in (c for c in sc.given_clauses if isinstance(c, GivenPredicate)):
            preconds.append(add_propty_prefix(c.predicate, global_ps, set()))
        for c in sc.such_that_clauses:
            preconds.append(add_propty_prefix(c.predicate, global_ps, set()))

        recv = []
        for c in (c for c in sc.then_clauses if isinstance(c, ThenState)):
            recv.append(f"state.{c.entity} = {render_st_ctor(c.entity, c.state)}")
        for c in (c for c in sc.then_clauses if isinstance(c, ThenProperty)):
            expr = add_propty_prefix(c.expression, global_ps, local_ps)
            recv.append(f"state.{c.property} = {expr}")

        precond = " && ".join([f"({x})" for x in preconds])
        t = {"pre": precond, "recv": recv}
        if act in transitions:
            transitions[act].append(t)
        else:
            transitions[act] = [t]

    # Generate receive blocks
    for action in feature.preamble.actions:
        a = action.name
        a_props = action.local_properties
        a_transitions = transitions[a]
        for i, t in enumerate(a_transitions):
            fn_lines = generate_function_def(
                f"{a}_precond_{i}", a_props, "bool", [f"return {t['pre']}"]
            )
            lines += fn_lines
            lines.append("")
        lines.append(f"action {a}" + " {")
        lines += [f"  {x.name}: {pp_ipl_type(x.ipl_type)}" for x in a_props]
        lines.append("  validate {")
        idxs = list(range(len(a_transitions)))
        args = ", ".join([f"this.{x.name}" for x in a_props])
        preconds: list[str] = [f"{a}_precond_{i}({args})" for i in idxs]
        lines.append("    " + " || ".join(preconds))
        lines.append("  }")
        lines.append("}")
        lines.append("")
        lines.append(f"receive (a: {a})" + "{")
        args = ", ".join([f"a.{x.name}" for x in a_props])
        for i, t in enumerate(a_transitions):
            lines.append(f"  if ({a}_precond_{i}({args})) then " + "{")
            lines += ["    " + x for x in t["recv"]]
            lines.append("  }")
        lines.append("}")
        lines.append("")

    return "\n".join(lines)


def generate_decomp_ipl(feature: Feature, decomp_length: int = 3) -> str:
    """
    Extend the above IPL decomp for decomp analysis.

    This is done simply by adding a single generic message flow of wildcard
    pattens for decomp to eagerly explore all paths.
    """
    base_ipl = generate_base_ipl(feature)
    flow = flow_template.format(
        flow_name="general", template=", ".join(["_"] * decomp_length)
    )
    message_flow = message_flow_template.format(flows=flow)
    return base_ipl + "\n" + message_flow


def generate_unsat_ipl(feature: Feature, decomp_length: int = 3) -> str:
    """
    Extend the above IPL decomp for unsat analysis.

    This is done by adding actions which look like e.g.:
    ```python
    action is_A {
      validate {
        state.state == A
      }
    }
    ```
    and message flows like:
    ```
    A_reachable {{
      template [_, _, _, is_A]
    }}
    ```
    This enables unsat analysis to test if a state is reachable.
    """
    base_ipl = generate_base_ipl(feature)
    extra_lines = []
    check_state_action_template = textwrap.dedent(
        """\
    action is_{value} {{
      validate {{
        state.{state} == {value}
      }}
    }}"""
    )

    # Generate state validators
    for e in feature.preamble.entities:
        for s in e.states:
            extra_lines.append(
                check_state_action_template.format(state=e.name, value=s.name)
            )
    flows = []
    for e in feature.preamble.entities:
        for s in e.states:
            template = ", ".join(["_"] * decomp_length + ["is_" + s.name])
            flows.append(
                flow_template.format(flow_name=s.name + "_reachable", template=template)
            )
    extra_lines.append(message_flow_template.format(flows="\n".join(flows)))

    return base_ipl + "\n" + "\n".join(extra_lines)
