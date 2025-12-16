import asyncio

from agents.code_logician.base.model_utils.iml import add_requests
from agents.code_logician.base.vg import VG
from utils.imandra.imandrax.async_client import (
    eval_src,
    get_imandrax_client,
)
from utils.imandra.imandrax.proto_models import VerifyRes
from utils.llm import get_llm

from ..base import (
    FormalizationState,
    FormalizationStateUpdate,
    RawVerifyReq,
)
from ..base.model_utils import verify_req_data_post
from ..tools.gen_vgs import code_to_raw_verify_req, raw_to_verify_req


async def gen_vgs_trans(
    state: FormalizationState,
    config: dict,
    description: str | None,
) -> FormalizationStateUpdate:
    src_lang = state.src_lang
    src_code = state.src_code
    iml_code = state.iml_code
    iml_model = state.iml_model

    if iml_code is None:
        raise ValueError("IML code is required")
    if iml_model is None:
        raise ValueError("IML model is required")

    llm = get_llm(use_case="code")

    # source code + IML code -> list of raw verify reqs
    raw_verify_reqs: list[RawVerifyReq] = await code_to_raw_verify_req(
        src_lang=src_lang,
        src_code=src_code,
        iml_code=iml_code,
        description=description,
        llm=llm,
    )
    vgs: list[VG] = [
        VG(raw=raw_verify_req, data=None, res=None)
        for raw_verify_req in raw_verify_reqs
    ]

    # list of verify req datas -> list of vgs
    verify_req_data_tasks = [raw_to_verify_req(llm, vg.raw, iml_code) for vg in vgs]
    verify_req_datas = await asyncio.gather(*verify_req_data_tasks)
    for i, verify_req_data in enumerate(verify_req_datas):
        vgs[i].data = verify_req_data

    # list of verify req datas -> list of vgs
    async with get_imandrax_client(
        config.get("configurable", {})
        .get("langgraph_auth_user", {})
        .get("imandra_api_key")
    ) as imx_client:
        # Parallelize eval_src + verify for each VG
        async def verify_single_vg(vg: VG) -> VerifyRes | None:
            # TODO: do we need to call eval_src before every vg? or just once?
            await eval_src(imx_client, iml_model)
            if vg.data is None:
                return None
            return await verify_req_data_post(vg.data, imx_client)

        verify_results = await asyncio.gather(*[verify_single_vg(vg) for vg in vgs])

        # Assign results
        for i, verify_res in enumerate(verify_results):
            if verify_res is not None:
                vgs[i].res = verify_res

    updated_vgs = state.vgs + vgs
    region_decomps = state.region_decomps
    iml_code = add_requests(
        iml_model,
        [rd.data for rd in region_decomps if rd.data is not None],
        [vg.data for vg in updated_vgs if vg.data is not None],
    )

    return FormalizationStateUpdate(iml_code=iml_code, vgs=updated_vgs)
