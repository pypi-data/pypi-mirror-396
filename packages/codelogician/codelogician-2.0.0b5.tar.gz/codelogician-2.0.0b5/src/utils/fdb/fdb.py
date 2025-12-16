from __future__ import annotations

import json
import textwrap
from dataclasses import asdict, dataclass
from functools import cache
from typing import Literal
from uuid import UUID

from asyncpg.pool import Pool
from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import OpenAIEmbeddings
from langsmith import traceable
from rapidfuzz import fuzz, process

from utils.llm import get_llm

from .data.error_corpus.agg import Item as ErrorItem, agg
from .retry import retry_fdb_operation
from .utils import extract_src_code_pattern

_fdb: FDB | None = None


def get_fdb() -> FDB:
    if _fdb is None:
        raise ValueError("FDB not initialized")
    return _fdb


def create_fdb(
    pg_pool: Pool,
    embeddings: Embeddings | None = None,
    llm: BaseChatModel | None = None,
) -> FDB:
    global _fdb
    if embeddings is None:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    if llm is None:
        llm = get_llm(use_case="code")
    fdb = FDB(pg_pool, embeddings, llm)
    _fdb = fdb
    return fdb


def process_fdb_tracing_outputs(outputs: list) -> dict:
    return {"count": len(outputs)}


@cache
def get_error_table() -> list[FDB.Error]:
    """Aggregate error data from files and build table."""
    items = agg()
    return [FDB.Error.from_corpus_item(item) for item in items]


class FDB:
    """Formalism Database"""

    @dataclass
    class IMLAPIReference:
        id: UUID
        module: str
        name: str
        signature: str
        doc: str | None = None
        pattern: str | None = None

        @classmethod
        def from_dict(cls, d: dict):
            return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

        def to_dict(self) -> dict:
            return asdict(self)

    @dataclass
    class ConversionPair:
        src_code: str
        src_lang: str
        refactored_code: list[dict[str, str]]
        src_tags: list[str]
        iml_code: str
        iml_tags: list[str]
        is_meta_eg: bool
        is_custom_eg: bool

        @classmethod
        def from_dict(cls, d: dict):
            # parse json
            if isinstance(d["refactored_code"], str):
                d["refactored_code"] = json.loads(d["refactored_code"])
            return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

        def to_dict(self) -> dict:
            return asdict(self)

    @dataclass
    class IMLCode:
        iml_code: str
        iml_tags: list[str]

        @classmethod
        def from_dict(cls, d: dict):
            return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

        def to_dict(self) -> dict:
            return asdict(self)

    @dataclass
    class Error:
        name: str
        kind: str
        msg_str: str
        tags: list[str]
        explanation: str
        repro_iml: str
        solution: str
        solution_description: str | None

        @classmethod
        def from_corpus_item(cls, item: ErrorItem):
            item_d = item.model_dump()
            item_d["tags"] = [tag.value for tag in item_d["tags"]]
            return cls(
                **{k: v for k, v in item_d.items() if k in cls.__dataclass_fields__}
            )

        def to_dict(self) -> dict:
            return asdict(self)

    @dataclass
    class MissingFunc:
        src_code: str
        src_lang: str
        opaque_func: str
        assumptions: list[str] | None
        approximation: str | None
        missing_tags: list[str]

        @classmethod
        def from_dict(cls, d: dict):
            return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

        def to_dict(self) -> dict:
            return asdict(self)

    def __init__(
        self,
        pg_pool: Pool,
        embeddings: Embeddings,
        llm: BaseChatModel,
    ):
        self.pg_pool = pg_pool
        self.embeddings = embeddings
        self.llm = llm

    @retry_fdb_operation()
    async def _fetch(self, query, *args, **kwargs):
        return await self.pg_pool.fetch(query, *args, **kwargs)

    @traceable(process_outputs=process_fdb_tracing_outputs)
    async def get_meta_conversion(self, src_lang: str) -> list[ConversionPair]:
        return [
            self.ConversionPair.from_dict(dict(row) | {"is_custom_eg": False})
            for row in await self._fetch(
                """
            SELECT
                src_code.id AS src_id,
                src_code.src_code,
                src_code.src_lang,
                src_code.refactored_code,
                src_code.src_tags,
                iml_code.id AS iml_id,
                iml_code.iml_code,
                iml_code.iml_tags,
                conversion.is_meta_eg
            FROM conversion
            INNER JOIN src_code ON conversion.src_code_id = src_code.id
            INNER JOIN iml_code ON conversion.iml_code_id = iml_code.id
            WHERE
                conversion.is_meta_eg = TRUE
                AND src_code.deleted_at IS NULL
                AND iml_code.deleted_at IS NULL
                AND src_code.src_lang = $1
            """,
                src_lang,
            )
        ]

    @traceable(process_outputs=process_fdb_tracing_outputs)
    async def get_all_missing_func(self) -> list[MissingFunc]:
        fetched = await self.pg_pool.fetch(
            """
            SELECT
                smf.id as smf_id,
                smf.src_lang as smf_src_lang,
                smf.src_code as smf_src_code,
                smf.missing_tags as smf_missing_tags,
                imf.id as imf_id,
                imf.opaque_func as imf_opaque_func,
                imf.name as imf_name,
                imf.description as imf_desc,
                imf.missing_tags as imf_missing_tags,
                imf.assumptions as imf_assumptions,
                approx.id as approx_id,
                approx.iml as approx_approximation,
                approx.name as approx_name,
                approx.type as approx_type,
                approx.description as approx_desc
            FROM src_missing_func smf
            INNER JOIN iml_missing_func imf on smf.iml_missing_func = imf.id AND imf.deleted_at IS NULL
            LEFT JOIN approximation approx ON imf.approximation = approx.id AND approx.deleted_at IS NULL
            WHERE smf.deleted_at IS NULL
            """  # noqa: E501
        )
        to_dict = map(dict, fetched)

        def _merge_tags(d: dict) -> dict:
            d["missing_tags"] = list(set(d["smf_missing_tags"] + d["imf_missing_tags"]))
            return d

        merge_tags = map(_merge_tags, to_dict)

        def _rename_keys(d: dict) -> dict:
            key_maps = {
                "smf_src_code": "src_code",
                "smf_src_lang": "src_lang",
                "imf_opaque_func": "opaque_func",
                "imf_assumptions": "assumptions",
                "approx_approximation": "approximation",
            }
            return {key_maps.get(k, k): v for k, v in d.items()}

        rename_keys = map(_rename_keys, merge_tags)

        res = list(rename_keys)
        return [self.MissingFunc.from_dict(row) for row in res]

    @traceable(process_outputs=process_fdb_tracing_outputs)
    async def search_iml_func(
        self,
        query: str,
        top_k: int = 10,
        exclude_ids: list[UUID] | None = None,
    ) -> list[IMLAPIReference]:
        query_v = self.embeddings.embed_query(query)

        where_clause = "WHERE embedding IS NOT NULL"
        fetch_sql_args = [query_v, top_k]

        if exclude_ids:
            where_clause += " AND id != ANY($3)"
            fetch_sql_args.append(exclude_ids)

        fetch_sql_template = textwrap.dedent(f"""
            SELECT
                id,
                module,
                name,
                type,
                signature,
                doc,
                pattern
            FROM iml_api_reference
            {where_clause}
            ORDER BY embedding <=> $1::vector
            LIMIT $2
        """)

        fetched = await self.pg_pool.fetch(
            fetch_sql_template,
            *fetch_sql_args,
        )
        return [self.IMLAPIReference.from_dict(dict(row)) for row in fetched]

    @traceable(process_outputs=process_fdb_tracing_outputs)
    async def search_iml_func_by_src_code(
        self,
        src_code: str,
        src_lang: str | None = None,
        top_k: int = 10,
    ) -> list[IMLAPIReference]:
        """
        Search IML API reference by source code.

        Args:
            src_code: Source code to search.
            src_lang: Source language.
            top_k: Number of results to return.

        Returns:
            IML API reference as list of dicts or a formatted string.
        """

        async def get_query(src_code: str, src_lang: str | None) -> str:
            patterns: list[str] = await extract_src_code_pattern(
                self.llm, src_code, src_lang
            )
            src_lang = src_lang if src_lang is not None else ""
            return textwrap.dedent(f"""
                <code>
                ```{src_lang}
                {src_code}
                ```
                </code>
                <patterns>
                {", ".join(patterns)}
                </patterns>
                """)

        query: str = await get_query(src_code, src_lang)
        iml_ars: list[FDB.IMLAPIReference] = await self.search_iml_func(query, top_k)
        return iml_ars

    @traceable(process_outputs=process_fdb_tracing_outputs)
    async def search_conversion_by_src_code(
        self,
        src_code: str,
        src_lang: str | None = None,
        top_k: int = 3,
    ) -> list[ConversionPair]:
        """
        Search conversion examples by source code.

        Args:
            src_code: Source code to search.
            src_lang: Source language.
            top_k: Number of results to return.
        """

        query = FDBFormatter.format_src_code(src_code, src_lang)
        query_v = self.embeddings.embed_query(query)
        return [
            self.ConversionPair.from_dict(dict(row) | {"is_custom_eg": False})
            for row in await self._fetch(
                """
            SELECT
                src_code.id AS src_id,
                src_code.src_code,
                src_code.src_lang,
                src_code.refactored_code,
                src_code.src_tags,
                iml_code.id AS iml_id,
                iml_code.iml_code,
                iml_code.iml_tags,
                conversion.is_meta_eg
            FROM src_code
            INNER JOIN conversion ON src_code.id = conversion.src_code_id
            INNER JOIN iml_code ON conversion.iml_code_id = iml_code.id
            WHERE src_code.src_lang = $1
            AND src_code.deleted_at IS NULL
            AND iml_code.deleted_at IS NULL
            AND src_code.embedding IS NOT NULL
            ORDER BY src_code.embedding <=> $2::vector
            LIMIT $3
            """,
                src_lang,
                query_v,
                top_k,
            )
        ]

    @traceable(process_outputs=process_fdb_tracing_outputs)
    async def search_iml_code_by_iml_code(
        self,
        iml_code: str,
        top_k: int = 3,
    ) -> list[IMLCode]:
        query_v = self.embeddings.embed_query(iml_code)
        return [
            self.IMLCode.from_dict(dict(row))
            for row in await self._fetch(
                """
            SELECT
                id,
                iml_code,
                iml_tags
            FROM iml_code
            WHERE embedding IS NOT NULL
            AND deleted_at IS NULL
            ORDER BY embedding <=> $1::vector
            LIMIT $2
            """,
                query_v,
                top_k,
            )
        ]

    @traceable(process_outputs=process_fdb_tracing_outputs)
    async def search_error(
        self,
        query: str,
        top_k: int = 3,
        truncate: int | None = 1000,
    ) -> list[Error]:
        if truncate:
            query = query[:truncate]

        errors = get_error_table()

        matches = process.extract(
            query,
            [e.msg_str for e in errors],
            scorer=fuzz.WRatio,
            limit=top_k,
        )

        results = []
        # TODO: add score to a part of the formated context?
        for _matched_msg, _score, index in matches:
            results.append(errors[index])

        return results

    class FDBSearchError(Exception):
        pass

    async def search(
        self,
        name: Literal[
            "formalization_examples_by_src_lang",
            "formalization_examples_by_src_code",
            "missing_functions",
            "iml_api_reference_by_pattern",
            "iml_api_reference_by_src_code",
            "iml_code_by_iml_code",
            "error_suggestion_by_error_msg",
        ],
        query: str | tuple[str, str] | None = None,
        top_k: int = 5,
        as_dict: bool = False,
    ) -> (
        list[IMLAPIReference]
        | list[ConversionPair]
        | list[IMLCode]
        | list[MissingFunc]
        | list[Error]
        | list[dict]
    ):
        def check_query_is_str(query):
            if not isinstance(query, str):
                raise self.FDBSearchError("Invalid query: expected string")

        def check_query_is_tuple(query):
            if not isinstance(query, tuple):
                raise self.FDBSearchError("Invalid query: expected tuple")

        match name:
            case "formalization_examples_by_src_lang":
                check_query_is_str(query)
                res = await self.get_meta_conversion(query)
            case "formalization_examples_by_src_code":
                check_query_is_tuple(query)
                res = await self.search_conversion_by_src_code(query, top_k)
            case "missing_functions":
                res = await self.get_all_missing_func()
            case "iml_api_reference_by_pattern":
                check_query_is_str(query)
                res = await self.search_iml_func(query, top_k)
            case "iml_api_reference_by_src_code":
                check_query_is_tuple(query)
                res = await self.search_iml_func_by_src_code(query, top_k)
            case "iml_code_by_iml_code":
                check_query_is_str(query)
                res = await self.search_iml_code_by_iml_code(query, top_k)
            case "error_suggestion_by_error_msg":
                check_query_is_str(query)
                res = await self.search_error(query, top_k)
            case _:
                raise self.FDBSearchError(f"Invalid FDB search name: {name}")

        if as_dict:
            return [obj.to_dict() for obj in res]
        else:
            return res


class FDBFormatter:
    """Formatter for FDB"""

    @staticmethod
    def flat_str_dict_to_xml(d: dict[str, str]) -> str:
        """
        Flatten a dictionary of strings to a string of XML.
        """
        return "\n".join([f"<{k}>{v}</{k}>" for k, v in d.items()])

    @staticmethod
    def format_src_code(src_code: str, src_lang: str | None = None) -> str:
        """
        Format source code.
        """
        return f"```{src_lang if src_lang else ''}\n{src_code}\n```"

    @staticmethod
    def format_iml_api_reference(
        iml_api_reference: dict
        | FDB.IMLAPIReference
        | list[dict]
        | list[FDB.IMLAPIReference],
    ) -> str:
        """
        Post-retrieval formatting for IML API reference.

        Examples:
            >>> iml_ar = {
            ...     "module": "math",
            ...     "name": "add",
            ...     "signature": "(x: int, y: int) -> int",
            ...     "doc": "Add two numbers",
            ...     "pattern": "x + y"
            ... }
            >>> print(FDB.format_iml_api_reference(iml_ar))
            <module>math</module>
            <name>add</name>
            <signature>(x: int, y: int) -> int</signature>
            <doc>Add two numbers</doc>
            <pattern>x + y</pattern>

            >>> iml_ars = [
            ...     {
            ...         "module": "math",
            ...         "name": "add",
            ...         "signature": "(x: int, y: int) -> int",
            ...         "doc": "Add two numbers",
            ...         "pattern": "x + y"
            ...     },
            ...     {
            ...         "module": "math",
            ...         "name": "sub",
            ...         "signature": "(x: int, y: int) -> int",
            ...         "doc": "Subtract two numbers",
            ...         "pattern": "x - y"
            ...     }
            ... ]
            >>> print(FDB.format_iml_api_reference(iml_ars))
            <1.>
            <module>math</module>
            <name>add</name>
            <signature>(x: int, y: int) -> int</signature>
            <doc>Add two numbers</doc>
            <pattern>x + y</pattern>
            </1.>
            <2.>
            <module>math</module>
            <name>sub</name>
            <signature>(x: int, y: int) -> int</signature>
            <doc>Subtract two numbers</doc>
            <pattern>x - y</pattern>
            </2.>
        """

        def subset(iml_ar: dict) -> dict:
            out_k = ["module", "name", "signature", "doc", "pattern"]
            return {k: iml_ar[k] for k in out_k}

        if isinstance(iml_api_reference, FDB.IMLAPIReference):
            return FDBFormatter.format_iml_api_reference(asdict(iml_api_reference))

        elif isinstance(iml_api_reference, dict):
            return FDBFormatter.flat_str_dict_to_xml(subset(iml_api_reference))

        elif isinstance(iml_api_reference, list):
            if len(iml_api_reference) == 0:
                raise ValueError("Empty list")

            elif isinstance(iml_api_reference[0], FDB.IMLAPIReference):
                # Convert to list of dicts and call recursively
                dcts = [iml_ar.to_dict() for iml_ar in iml_api_reference]
                return FDBFormatter.format_iml_api_reference(dcts)

            elif isinstance(iml_api_reference[0], dict):
                lst_str = [
                    FDBFormatter.flat_str_dict_to_xml(subset(iml_ar))
                    for iml_ar in iml_api_reference
                ]
                res = ""
                for i, s in enumerate(lst_str, 1):
                    res += f"<{i}.>\n{s}\n</{i}.>\n"
                return res
            else:
                raise ValueError(
                    f"Invalid list element type: {type(iml_api_reference[0])}"
                )
        else:
            raise ValueError(f"Invalid IML API reference: {iml_api_reference}")

    @staticmethod
    def format_missing_func(
        missing_func: dict | list[dict] | FDB.MissingFunc | list[FDB.MissingFunc],
    ) -> str:
        """
        Format missing function.
        """
        if isinstance(missing_func, FDB.MissingFunc):
            return FDBFormatter.format_missing_func(asdict(missing_func))
        elif isinstance(missing_func, list):
            if len(missing_func) == 0:
                raise ValueError("Empty list")
            else:
                s = ""
                for i, mf in enumerate(missing_func, 1):
                    s += f"<{i}.>\n"
                    s += FDBFormatter.format_missing_func(mf)
                    s += f"</{i}.>\n"
                return s
        elif isinstance(missing_func, dict):
            s = ""
            s += f"<missing_func>\n{missing_func['src_code']}\n</missing_func>\n"
            # s += f"<missing_reason>\n{', '.join(mf['missing_tags'])}\n</missing_reason>\n"  # noqa: E501
            s += f"<iml_func>\n{missing_func['opaque_func']}\n</iml_func>\n"
            if missing_func["approximation"]:
                s += (
                    f"<approximation>\n{missing_func['approximation']}"
                    "\n</approximation>\n"
                )
            return s
        else:
            raise ValueError(f"Invalid missing function: {missing_func}")

    @staticmethod
    def format_conversion_pair(
        pair: FDB.ConversionPair | list[FDB.ConversionPair],
    ) -> str:
        """
        Format conversion pair.
        """
        match pair:
            case FDB.ConversionPair():
                s = ""
                s += FDBFormatter.format_src_code(pair.src_code, pair.src_lang)
                s += "\n"
                s += FDBFormatter.format_src_code(pair.iml_code, "iml")
                s += "\n"
                return s
            case [p]:
                return FDBFormatter.format_conversion_pair(p)
            case [_p, *_ps]:
                s = ""
                for i, p in enumerate(pair, 1):
                    s += f"Example {i}:\n"
                    s += FDBFormatter.format_conversion_pair(p)
                return s
            case _:
                raise ValueError(f"Invalid conversion pair: {pair}")

    @staticmethod
    def format_iml_code(iml_code: FDB.IMLCode | list[FDB.IMLCode]) -> str:
        """
        Format IML code.
        """
        match iml_code:
            case FDB.IMLCode():
                s = ""
                s += FDBFormatter.format_src_code(iml_code.iml_code, "iml")
                s += "\n"
                if iml_code.iml_tags:
                    s += f"Tags: {', '.join(iml_code.iml_tags)}\n"
                return s
            case [c]:
                return FDBFormatter.format_iml_code(c)
            case [_c, *_cs]:
                s = ""
                for i, c in enumerate(iml_code, 1):
                    s += f"Example {i}:\n"
                    s += FDBFormatter.format_iml_code(c)
                return s
            case _:
                raise ValueError(f"Invalid IML code: {iml_code}")

    @staticmethod
    def format_error(error: FDB.Error | list[FDB.Error]) -> str:
        """
        Format error.
        """
        match error:
            case FDB.Error() as e:
                s = ""
                s += f"<error>\n{e.msg_str}\n<error/>\n"
                s += f"<explanation>\n{e.explanation}\n<explanation/>\n"
                if e.solution:
                    s += "<solution>"
                    s += f"<before>\n{e.repro_iml}\n<before/>\n"
                    s += "\n"
                    s += f"<after>\n{e.solution}\n<after/>\n"
                    s += "<solution/>"
                return s
            case [e]:
                return FDBFormatter.format_error(e)
            case [_e, *_es] as es:
                s = ""
                for i, e in enumerate(es, 1):
                    s += f"Error {i} {e.name}:\n"
                    s += FDBFormatter.format_error(e)
                return s
            case _:
                raise ValueError(f"Invalid error: {error}")
