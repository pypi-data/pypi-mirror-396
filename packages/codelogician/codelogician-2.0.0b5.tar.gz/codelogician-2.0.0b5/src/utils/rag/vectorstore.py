import json
from typing import Any

from langchain_core.documents import Document

from .duckdb import DuckDB

DEFAULT_VECTOR_KEY = "embedding"
DEFAULT_ID_KEY = "id"
DEFAULT_TEXT_KEY = "text"
DEFAULT_TABLE_NAME = "embeddings"
SIMILARITY_ALIAS = "similarity_score"


class IUDuckDBVectorStore(DuckDB):
    """Overriding DuckDB's `similarity_search`
    Change:
        - allow non-existence of `metadata`
        - return `id`
    """

    def similarity_search(
        self, query: str, k: int = 4, **kwargs: Any
    ) -> list[Document]:
        """Performs a similarity search for a given query string.

        Args:
            query: The query string to search for.
            k: The number of similar texts to return.

        Returns:
            A list of Documents most similar to the query.
        """
        embedding = self._embedding.embed_query(query)
        list_cosine_similarity = self.duckdb.FunctionExpression(
            "list_cosine_similarity",
            self.duckdb.ColumnExpression(self._vector_key),
            self.duckdb.ConstantExpression(embedding),
        )
        docs = (
            self._table.select(
                *[
                    self.duckdb.StarExpression(exclude=[]),
                    list_cosine_similarity.alias(SIMILARITY_ALIAS),
                ]
            )
            .order(f"{SIMILARITY_ALIAS} desc")
            .limit(k)
            .fetchdf()
        )
        return [
            Document(
                page_content=docs[self._text_key][idx],
                id=docs[self._id_key][idx],
                metadata=(
                    {
                        **json.loads(docs["metadata"][idx]),
                        "similarity_score": float(docs[SIMILARITY_ALIAS][idx]),
                    }
                    if "metadata" in docs and docs["metadata"][idx]
                    else {}
                ),
            )
            for idx in range(len(docs))
        ]
