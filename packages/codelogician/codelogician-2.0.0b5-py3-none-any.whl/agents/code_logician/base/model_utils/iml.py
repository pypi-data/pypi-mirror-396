from __future__ import annotations

import structlog
from iml_query.processing import (
    Nesting,
    decomp_capture_to_req,
    insert_decomp_req,
    insert_instance_req,
    insert_verify_req,
    instance_capture_to_req,
    resolve_nesting_definitions,
    verify_capture_to_req,
)
from iml_query.queries import (
    DECOMP_QUERY_SRC,
    INSTANCE_QUERY_SRC,
    MEASURE_QUERY_SRC,
    OPAQUE_QUERY_SRC,
    VALUE_DEFINITION_QUERY_SRC,
    VERIFY_QUERY_SRC,
    DecompCapture,
    InstanceCapture,
    MeasureCapture,
    OpaqueCapture,
    ValueDefCapture,
    VerifyCapture,
)
from iml_query.tree_sitter_utils import (
    delete_nodes,
    get_nesting_relationship,
    get_parser,
    run_queries,
    unwrap_bytes,
)

from agents.code_logician.base.region_decomp import DecomposeReqData
from agents.code_logician.base.vg import VerifyReqData

from ..iml import (
    LintingError,
    NestedMeasureError,
    NestedRecursiveFunctionError,
    TopLevelDefinition,
)

logger = structlog.get_logger(__name__)

Loc = tuple[int, int]


def captures_to_symbol_info(
    value_def_captures: list[ValueDefCapture],
    measure_captures: list[MeasureCapture],
    opaque_captures: list[OpaqueCapture],
) -> tuple[list[TopLevelDefinition], list[LintingError]]:
    # Lookup maps from function name to capture
    measure_func_map: dict[str, MeasureCapture] = {
        unwrap_bytes(capture.function_name.text).decode("utf-8"): capture
        for capture in measure_captures
    }
    opaque_func_map: dict[str, OpaqueCapture] = {
        unwrap_bytes(capture.function_name.text).decode("utf-8"): capture
        for capture in opaque_captures
    }

    top_defs: list[TopLevelDefinition] = []
    matched_measure_names: set[str] = set()
    linting_errors: list[LintingError] = []

    # Fill measure and opaque information for top-level capture to
    # obtain top-level definitions
    top_captures = [cap for cap in value_def_captures if cap.is_top_level]
    for top_caputre in top_captures:
        top_name = top_caputre.function_name
        top_def_node = top_caputre.function_definition
        top_name_str = unwrap_bytes(top_name.text).decode("utf-8")

        # Detect measure attribute
        measure: None | str = None
        if top_name_str in measure_func_map:
            m_cap = measure_func_map[top_name_str]
            measure = unwrap_bytes(m_cap.measure_attr.text).decode("utf-8")
            matched_measure_names.add(top_name_str)

        # Detect opaque attribute
        opaque = top_name_str in opaque_func_map

        top_def = TopLevelDefinition(
            name=top_name_str,
            start_byte=top_def_node.start_byte,
            end_byte=top_def_node.end_byte,
            start_point=(top_def_node.start_point[0], top_def_node.start_point[1]),
            end_point=(top_def_node.end_point[0], top_def_node.end_point[1]),
            measure=measure,
            opaque=opaque,
        )

        top_defs.append(top_def)

    # NestedMeasureError
    # find measure functions that are not top-level (these are linting errors)
    for func_name, measure_capture in measure_func_map.items():
        if func_name in matched_measure_names:
            continue
        measure_def_node = measure_capture.function_definition
        for top_capture in top_captures:
            top_def_node = top_capture.function_definition
            nesting_rel = get_nesting_relationship(
                measure_def_node,
                top_def_node,
            )
            match nesting_rel:
                case -1:
                    # Not this top-level function
                    pass
                case i if i > 0:
                    err = NestedMeasureError(
                        start_byte=measure_def_node.start_byte,
                        end_byte=measure_def_node.end_byte,
                        start_point=(
                            measure_def_node.start_point.row,
                            measure_def_node.start_point.column,
                        ),
                        end_point=(
                            measure_def_node.end_point.row,
                            measure_def_node.end_point.column,
                        ),
                        function_name=unwrap_bytes(
                            measure_capture.function_name.text
                        ).decode("utf-8"),
                        measure=unwrap_bytes(measure_capture.measure_attr.text).decode(
                            "utf-8"
                        ),
                        top_function_name=unwrap_bytes(
                            top_capture.function_name.text
                        ).decode("utf-8"),
                        nesting_level=i,
                    )
                    linting_errors.append(err)
                case 0:
                    raise AssertionError(
                        "Never: we should have ruled out top-level measures"
                    )

    # NestedRecError
    # find rec functions that are NOT top-level (these are linting errors)
    nestings: list[Nesting] = resolve_nesting_definitions(value_def_captures)
    for nesting in nestings:
        if not nesting["child"].is_rec:
            continue
        child_def_cap = nesting["child"]
        top_def_cap = nesting["parent"]
        err = NestedRecursiveFunctionError(
            start_byte=child_def_cap.function_definition.start_byte,
            end_byte=child_def_cap.function_definition.end_byte,
            start_point=(
                child_def_cap.function_definition.start_point.row,
                child_def_cap.function_definition.start_point.column,
            ),
            end_point=(
                child_def_cap.function_definition.end_point.row,
                child_def_cap.function_definition.end_point.column,
            ),
            function_name=unwrap_bytes(child_def_cap.function_name.text).decode(
                "utf-8"
            ),
            top_function_name=unwrap_bytes(top_def_cap.function_name.text).decode(
                "utf-8"
            ),
            nesting_level=nesting["nesting_level"],
        )
        linting_errors.append(err)

    return top_defs, linting_errors


def remove_requests(
    iml: str,
    decomp_captures: list[DecompCapture],
    verify_captures: list[VerifyCapture],
    instance_captures: list[InstanceCapture],
) -> str:
    """Remove requests corresponding to the captures from IML code."""
    tree = get_parser().parse(bytes(iml, "utf-8"))
    nodes_to_remove = [
        # decomp attr nodes
        *[capture.decomp_attr for capture in decomp_captures],
        # verify nodes
        *[capture.verify for capture in verify_captures],
        # instance nodes
        *[capture.instance for capture in instance_captures],
    ]
    new_iml, _new_tree = delete_nodes(iml, tree, nodes=nodes_to_remove)
    return new_iml


def parse_iml(
    iml: str,
) -> (
    tuple[
        str,
        list[TopLevelDefinition],
        list[LintingError],
        list[DecomposeReqData],
        list[VerifyReqData],
    ]
    | None
):
    tree = get_parser().parse(bytes(iml, "utf-8"))

    if tree.root_node.type == "ERROR":
        logger.warning(
            "IML code has syntax errors and cannot be parsed by tree-sitter",
            root_node_type=tree.root_node.type,
        )
        return None

    queries = {
        "value_def_functions": VALUE_DEFINITION_QUERY_SRC,
        "measure_functions": MEASURE_QUERY_SRC,
        "opaque_functions": OPAQUE_QUERY_SRC,
        "decomp_req": DECOMP_QUERY_SRC,
        "verify_req": VERIFY_QUERY_SRC,
        "instance_req": INSTANCE_QUERY_SRC,
    }
    captures_map = run_queries(queries, tree.root_node)
    def_captures: list[ValueDefCapture] = [
        ValueDefCapture.from_ts_capture(capture)
        for capture in captures_map.get("value_def_functions", [])
    ]

    measure_captures: list[MeasureCapture] = [
        MeasureCapture.from_ts_capture(capture)
        for capture in captures_map.get("measure_functions", [])
    ]

    opaque_captures: list[OpaqueCapture] = [
        OpaqueCapture.from_ts_capture(capture)
        for capture in captures_map.get("opaque_functions", [])
    ]
    logger.info("Parsed opaque functions", opaque_captures=opaque_captures)

    decomp_captures: list[DecompCapture] = [
        DecompCapture.from_ts_capture(capture)
        for capture in captures_map.get("decomp_req", [])
    ]

    verify_captures: list[VerifyCapture] = [
        VerifyCapture.from_ts_capture(capture)
        for capture in captures_map.get("verify_req", [])
    ]

    instance_captures: list[InstanceCapture] = [
        InstanceCapture.from_ts_capture(capture)
        for capture in captures_map.get("instance_req", [])
    ]

    top_defs, linting_errors = captures_to_symbol_info(
        def_captures,
        measure_captures,
        opaque_captures,
    )
    decomp_req_dicts = [decomp_capture_to_req(i) for i in decomp_captures]
    verify_req_dicts = [verify_capture_to_req(i) for i in verify_captures]
    instance_req_dicts = [instance_capture_to_req(i) for i in instance_captures]

    decomp_req_data = [DecomposeReqData(**i) for i in decomp_req_dicts]
    verify_req_data = [
        *[VerifyReqData(predicate=i["src"], kind="verify") for i in verify_req_dicts],
        *[
            VerifyReqData(predicate=i["src"], kind="instance")
            for i in instance_req_dicts
        ],
    ]

    iml_model = remove_requests(
        iml,
        decomp_captures,
        verify_captures,
        instance_captures,
    )
    return iml_model, top_defs, linting_errors, decomp_req_data, verify_req_data


def add_requests(
    iml: str,
    decomp_req_data: list[DecomposeReqData],
    verify_req_data: list[VerifyReqData],
) -> str:
    """Add requests to IML model to get IML code."""
    tree = get_parser().parse(bytes(iml, "utf-8"))
    for decomp_req in decomp_req_data:
        iml, tree = insert_decomp_req(iml, tree, decomp_req.model_dump(by_alias=True))
    for verify_req in verify_req_data:
        match verify_req.kind:
            case "instance":
                iml, tree = insert_instance_req(iml, tree, verify_req.predicate)
            case "verify":
                iml, tree = insert_verify_req(iml, tree, verify_req.predicate)
            case _:
                raise AssertionError(f"Never: Unknown verify kind: {verify_req.kind}")
    return iml
