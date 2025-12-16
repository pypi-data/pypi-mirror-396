from typing import Self

from langchain_google_vertexai import VertexAIEmbeddings
from pydantic import BaseModel, Field
from pydantic.type_adapter import TypeAdapter

from .code_splitter import Chunk, Loc, chunk_code

MAX_BATCH_SIZE = 3072
EMBEDDING_MODEL_NAME = "gemini-embedding-001"


EMBEDDING_METADATA = {
    "model": EMBEDDING_MODEL_NAME,
    "batch_size": MAX_BATCH_SIZE,
}


def create_embedding_model() -> VertexAIEmbeddings:
    em = VertexAIEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
    )
    return em


def embed_chunks(chunks: list[Chunk]) -> list[list[float]]:
    em = create_embedding_model()
    embeddings = em.embed_documents(
        [chunk.text for chunk in chunks],
        batch_size=MAX_BATCH_SIZE,
    )
    return embeddings


def embed_query(query: str) -> list[float]:
    em = create_embedding_model()
    embedding = em.embed_query(text=query)
    return embedding


class EmbedResultItem(BaseModel):
    embedding: list[float]
    start_char: int
    end_char: int = Field(description="Exclusive")
    start_loc: Loc
    end_loc: Loc = Field(description="Inclusive")

    @classmethod
    def create(cls, embeddings: list[float], chunk: Chunk) -> Self:
        return cls(
            embedding=embeddings,
            start_char=chunk.start_char,
            end_char=chunk.end_char,
            start_loc=chunk.start_loc,
            end_loc=chunk.end_loc,
        )


EmbeddingResult = TypeAdapter(list[EmbedResultItem])


def embed_code(src_code: str, src_lang: str) -> list[EmbedResultItem]:
    chunks = chunk_code(src_code, src_lang)
    embeddings = embed_chunks(chunks)
    embed_results = [
        EmbedResultItem.create(embedding, chunk)
        for (chunk, embedding) in zip(chunks, embeddings, strict=True)
    ]

    return embed_results
