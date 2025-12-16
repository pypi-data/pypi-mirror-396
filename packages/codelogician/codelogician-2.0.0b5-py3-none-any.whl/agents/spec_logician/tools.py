import json
import os
from difflib import unified_diff
from pathlib import Path

import imandra.ipl as ipl
from langchain_core.messages import HumanMessage, SystemMessage
from parsy import ParseError
from pydantic import BaseModel, Field
from urllib3.util import parse_url

from agents.spec_logician.formal_spec.dsl.checking import check_feature
from agents.spec_logician.formal_spec.dsl.codegen import generate_base_ipl
from agents.spec_logician.formal_spec.dsl.diff import diff_features, pp_edits
from agents.spec_logician.formal_spec.dsl.feedback import pp_feedback
from agents.spec_logician.formal_spec.dsl.parser import parse_all
from agents.spec_logician.formal_spec.dsl.pretty_printing import (
    pp_feature,
    pp_fn_signature,
)
from agents.spec_logician.formal_spec.dsl.syntax import Feature, has_opaque_fns
from agents.spec_logician.formalization_state import (
    Formalization,
    FormalizationState,
)
from utils.llm import get_llm

current_dir = Path(__file__).resolve().parent
ipl_expr_101 = current_dir / "formal_spec" / "ipl-expr-101.md"
sys_prompt = current_dir / "formal_spec" / "sys-prompt.md"


def get_ipl_101_prompt() -> str:
    return ipl_expr_101.read_text()


def get_formal_spec_prompt() -> str:
    return sys_prompt.read_text()


trans_prompt_template = """
Translate this Cucumber Feature into a Formal Feature:

```
{cucumber}
```
"""

current_formal_template = """
Here's our current formal spec:

```
{formal_spec}
```

Please use it as a reference when generating the new formal spec.
"""

prev_attempt_template = """
Here's a previous version of the natural language spec:

```
{old_spec}
```

For that previous natural language spec, you generated the following formal spec:

```
{old_formal}
```

You are tasked to generate a formal spec for the current version of
the natural language spec, which differs from the previous version shown above.
I've already shown you the previous and current versions of the natural language spec,
so here's a diff of the two, for your convenience:

```
{diff}
```

When generating a formal spec corresponding to the current natural language spec,
please take into account:
- how you formalized the previous natural language spec
- how the natural language spec evolved
"""

sync_template = """
Here's our current formal spec:

```
{new_formal}
```

The current formal spec has diverged from its previous version,
which is instead the following:

```
{old_formal}
```

The previous formal spec was directly generated from this version
of the natural language spec:

```
{old_spec}
```

The previous formal spec and the current formal spec have diverged.
Here's a detailed list of what changed:

{diff}

---

Please write an updated version of the _natural language spec_ shown above,
such that the changes made to the formal spec are reflected in it,
thus bringing the natural language spec and formal spec back in sync.
"""

current_spec_template = """
Here's our current version of the natural language spec.
It's different from the version of the spec that last got synched with the formal specs.
Please use it as a reference when generating the new natural language spec.

```
{new_spec}
```
"""


feedback_template = """
There are some issues with the current Formal Spec:

{feedback_list}

Please address them when generating the new formal spec.
"""


user_feedback_template = """
Take the following instructions into account when generating the Formal Spec:

{feedback_list}
"""
#########
# UTILS #
#########


class ToolError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__()


def _get_ipl_client(imandra_api_key: str | None = None):
    imandra_u_url = os.getenv("IMANDRA_U_URL")
    imandra_api_key = imandra_api_key or os.getenv("IMANDRA_API_KEY")
    if not imandra_u_url:
        raise ValueError("IMANDRA_U_URL is None")
    if not imandra_api_key:
        raise ValueError("IMANDRA_API_KEY is None")
    url = parse_url(imandra_u_url)
    return ipl.Client(api_key=imandra_api_key, scheme=url.scheme, host=url.host)


async def invoke_llm(config, messages) -> Feature:
    model_name = config.get("configurable", {}).get("llm_model_name", None)
    llm = get_llm(model_name) if model_name else get_llm(use_case="code")
    response = await llm.with_structured_output(schema=Feature).ainvoke(messages)
    return response


class SpecResponse(BaseModel):
    spec_response: str = Field(description="Generated natural language spec")


async def invoke_llm_for_spec(config, messages) -> SpecResponse:
    model_name = config.get("configurable", {}).get("llm_model_name", None)
    llm = get_llm(model_name) if model_name else get_llm(use_case="code")
    response = await llm.with_structured_output(schema=SpecResponse).ainvoke(messages)
    return response


def compose_gen_msgs(nl_feature: str):
    ipl_expr_101_content = get_ipl_101_prompt()
    sys_prompt_content = get_formal_spec_prompt()
    trans_request = trans_prompt_template.format(cucumber=nl_feature)
    return [
        SystemMessage(ipl_expr_101_content),
        SystemMessage(sys_prompt_content),
        HumanMessage(trans_request),
    ]


def compose_validation_feedback(validation_result: list[str]) -> HumanMessage:
    feedback_list = "\n".join([f"* {fb}" for fb in validation_result])
    feedback_text = feedback_template.format(feedback_list=feedback_list)
    return HumanMessage(feedback_text)


def compose_user_feedback(user_feedback: list[str]) -> HumanMessage:
    feedback_list = "\n".join([f"* {fb}" for fb in user_feedback])
    feedback_text = user_feedback_template.format(feedback_list=feedback_list)
    return HumanMessage(feedback_text)


#########
# TOOLS #
#########


def set_natural_language_spec(
    state: FormalizationState, src_spec: str
) -> FormalizationState:
    return FormalizationState(
        src_spec=src_spec,
        formalization=state.formalization,
        user_feedback=state.user_feedback,
    )


def set_formal_spec(
    state: FormalizationState, formal_spec: str
) -> FormalizationState | ToolError:
    try:
        parsed = parse_all(formal_spec)
        if state.formalization:
            formalization = state.formalization.model_copy(
                update={"formal_spec": parsed}
            )
        else:
            formalization = Formalization(
                formal_spec=parsed,
                last_synced_nl_spec=state.src_spec,
                last_synced_formal_spec=parsed,
                validation_result=None,
                decomp_result=None,
                reachability_result=None,
            )
        return FormalizationState(
            src_spec=state.src_spec,
            formalization=formalization,
            user_feedback=state.user_feedback,
        )
    except ParseError as e:
        return ToolError(str(e))


async def generate_formal_spec(state: FormalizationState, config) -> FormalizationState:
    """
    Generate the FormalSpec version of the specification.

    Takes into account contents and validation results of the previous attempt,
    including diffs between old and new versions of the natural language spec.
    """

    def mk_prev_attempt_txt(state: FormalizationState) -> str | None:
        if not state.formalization:
            return None

        old_spec = state.formalization.last_synced_nl_spec
        new_spec = state.src_spec
        old_formal = state.formalization.last_synced_formal_spec

        if old_spec == new_spec:
            return None

        old_lines = old_spec.splitlines()
        new_lines = new_spec.splitlines()
        diff = "\n".join(list(unified_diff(old_lines, new_lines))[3:])

        txt = prev_attempt_template.format(
            old_spec=old_spec,
            old_formal=old_formal.model_dump_json(),
            diff=diff,
        )
        return txt

    gen_msgs = compose_gen_msgs(state.src_spec)
    if state.formalization:
        current_formal_txt = current_formal_template.format(
            formal_spec=state.formalization.formal_spec.model_dump_json()
        )
        current_formal_msg = HumanMessage(current_formal_txt)
        gen_msgs = [*gen_msgs, current_formal_msg]
        validation_result = state.formalization.validation_result
        if validation_result is not None and len(validation_result) > 0:
            validation_feedback_msg = compose_validation_feedback(validation_result)
            gen_msgs = [*gen_msgs, validation_feedback_msg]
    prev_attempt_txt = mk_prev_attempt_txt(state)
    if prev_attempt_txt:
        prev_attempt_msg = HumanMessage(prev_attempt_txt)
        gen_msgs = [*gen_msgs, prev_attempt_msg]
    if len(state.user_feedback) > 0:
        user_feedback_msg = compose_user_feedback(state.user_feedback)
        gen_msgs = [*gen_msgs, user_feedback_msg]

    response = await invoke_llm(config, gen_msgs)

    return FormalizationState(
        src_spec=state.src_spec,
        formalization=Formalization(
            last_synced_nl_spec=state.src_spec,
            formal_spec=response,
            last_synced_formal_spec=response,
            validation_result=None,
            decomp_result=None,
            reachability_result=None,
        ),
        user_feedback=state.user_feedback,
    )


async def sync_nl_spec(
    state: FormalizationState, config
) -> FormalizationState | ToolError:
    if not state.formalization:
        return ToolError("Formalization state does not contain a spec to synchronize")

    old_spec = state.formalization.last_synced_nl_spec
    new_spec = state.src_spec
    old_formal = state.formalization.last_synced_formal_spec
    new_formal = state.formalization.formal_spec

    edits = diff_features(old_formal, new_formal)
    sync_txt = sync_template.format(
        new_formal=new_formal.model_dump_json(),
        old_formal=old_formal.model_dump_json(),
        old_spec=old_spec,
        diff=pp_edits(edits),
    )
    msgs = [HumanMessage(sync_txt)]

    if old_spec != new_spec:
        current_spec_txt = current_spec_template.format(new_spec=new_spec)
        current_spec_msg = HumanMessage(current_spec_txt)
        msgs = [*msgs, current_spec_msg]

    res: SpecResponse = await invoke_llm_for_spec(config, msgs)
    formalization = state.formalization.model_copy(
        update={
            "last_synced_nl_spec": res.spec_response,
            "last_synced_formal_spec": new_formal,
        }
    )
    return state.model_copy(
        update={
            "src_spec": res.spec_response,
            "formalization": formalization,
        }
    )


async def sync_formal(state: FormalizationState, config) -> FormalizationState:
    if not state.formalization:
        return await generate_formal_spec(state, config)

    old_spec = state.formalization.last_synced_nl_spec
    new_spec = state.src_spec

    if old_spec == new_spec:
        # Old and new natural language specs are already synced. Nothing to do.
        return state
    else:
        return await generate_formal_spec(state, config)


def validate_formal_spec(
    state: FormalizationState, config
) -> FormalizationState | ToolError:
    imandra_api_key: str = (
        config.get("configurable", {})
        .get("langgraph_auth_user", {})
        .get("imandra_api_key")
    )
    ipl_client = _get_ipl_client(imandra_api_key)
    if state.formalization:
        check_results = check_feature(ipl_client, state.formalization.formal_spec)
        validation_result = [pp_feedback(fb) for fb in check_results]
        formalization = state.formalization.model_copy(
            update={"validation_result": validation_result}
        )
        return FormalizationState(
            src_spec=state.src_spec,
            formalization=formalization,
            user_feedback=state.user_feedback,
        )
    else:
        return ToolError("No formal spec")


def get_pprinted_formal_spec(fstate: FormalizationState) -> str | ToolError:
    if not fstate.formalization:
        return ToolError("There is no formal spec to pretty-print")

    return pp_feature(fstate.formalization.formal_spec)


def get_ipl_spec(fstate: FormalizationState) -> str | ToolError:
    if not fstate.formalization:
        return ToolError("There is no formal spec from which to generate IPL code")

    if has_opaque_fns(fstate.formalization.formal_spec.preamble):
        return ToolError(
            "Cannot generate IPL model, "
            "because the formal spec contains opaque functions"
        )

    validations = fstate.formalization.validation_result
    if validations is None:
        return ToolError("Formal spec needs to be validated prior to IPL generation")
    if len(validations) > 0:
        return ToolError("Formal spec is invalid")

    return generate_base_ipl(fstate.formalization.formal_spec)


def get_validation_result(fstate: FormalizationState) -> str | ToolError:
    if not fstate.formalization:
        return ToolError("No formalization has been run yet")

    validations = fstate.formalization.validation_result
    if validations is None:
        return ToolError("Formal spec has not been validated yet")

    return json.dumps(validations)


def get_opaque_functions(fstate: FormalizationState) -> str | ToolError:
    if not fstate.formalization:
        return ToolError("No formalization has been run yet")

    fn_defs = fstate.formalization.formal_spec.preamble.fun_defs
    opaques = [pp_fn_signature(fn) for fn in fn_defs]
    return json.dumps(opaques)


def submit_fn_implementation(
    fstate: FormalizationState, fn_name: str, fn_statements: list[str]
) -> FormalizationState | ToolError:
    if not fstate.formalization:
        return ToolError("No formalization has been run yet")

    fn_defs = fstate.formalization.formal_spec.preamble.fun_defs
    idx = next((i for i, fn in enumerate(fn_defs) if fn.name == fn_name), None)

    if idx is None:
        return ToolError(f"No function with name `{fn_name}` found in the formal spec")

    new_fn_def = fn_defs[idx].model_copy(update={"statements": fn_statements})
    new_fn_defs = [fn.model_copy() for fn in fn_defs]
    new_fn_defs[idx] = new_fn_def

    new_fstate = fstate.model_copy()
    new_fstate.formalization.formal_spec.preamble.fun_defs = new_fn_defs
    new_fstate.formalization.validation_result = None

    return new_fstate


def get_user_instructions(fstate: FormalizationState) -> str:
    return json.dumps(fstate.user_feedback)


def set_user_instructions(
    fstate: FormalizationState, instructions: list[str]
) -> FormalizationState:
    return fstate.model_copy(update={"user_feedback": instructions})
