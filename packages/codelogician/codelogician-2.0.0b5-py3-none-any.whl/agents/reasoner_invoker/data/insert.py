import json
import uuid

import duckdb
from cogito.agent.reasoner_invoker.data.format import (
    format_error_before_embedding,
    format_valid_input_before_embedding,
)
from cogito.agent.reasoner_invoker.rag import connect_duckdb
from langchain_openai import OpenAIEmbeddings


def dump_db(
    con: duckdb.DuckDBPyConnection,
    data_dir: str,
):
    for table in ["error", "valid_input"]:
        with open(f"{data_dir}/doc/{table}.json", "w") as f:
            js = con.table(table).df().to_json(orient="records")
            json.dump(json.loads(js), f, indent=4)

        with open(f"{data_dir}/vector/{table}.json", "w") as f:
            js = con.table(table + "_vector").df().to_json(orient="records")
            json.dump(json.loads(js), f, indent=4)


def insert_error(
    reasoner: str,
    input: str,
    errors: list[str],
    correction: str,
    tags: list[str],
    embeddings: OpenAIEmbeddings,
    con: duckdb.DuckDBPyConnection | None = None,
):
    if con is None:
        con = connect_duckdb(reasoner)

    # error record
    id = str(uuid.uuid4())
    error_record = {
        "id": id,
        "reasoner": reasoner,
        "input": input,
        "errors": errors,
        "correction": correction,
        "tags": tags,
    }

    # error vector record
    text = format_error_before_embedding(error_record)
    vector = embeddings.embed_query(text)
    error_vector_record = {
        "id": id,
        "text": text,
        "vector": vector,
    }

    # Insert
    con.execute(
        """
    INSERT INTO error (id, reasoner, input, errors, correction, tags)
    VALUES (?, ?, ?, ?, ?, ?)
    """,
        [
            error_record["id"],
            error_record["reasoner"],
            error_record["input"],
            error_record["errors"],
            error_record["correction"],
            error_record["tags"],
        ],
    )

    con.execute(
        """
    INSERT INTO error_vector (id, text, vector)
    VALUES (?, ?, ?)
    """,
        [
            error_vector_record["id"],
            error_vector_record["text"],
            error_vector_record["vector"],
        ],
    )
    return con, id


def insert_valid_input(
    reasoner: str,
    input: str,
    tags: list[str],
    embeddings: OpenAIEmbeddings,
    con: duckdb.DuckDBPyConnection | None = None,
):
    if con is None:
        con = connect_duckdb(reasoner)

    # valid input record
    id = str(uuid.uuid4())
    valid_input_record = {
        "id": id,
        "reasoner": reasoner,
        "input": input,
        "tags": tags,
    }

    # valid input vector record
    text = format_valid_input_before_embedding(valid_input_record)
    vector = embeddings.embed_query(text)
    valid_input_vector_record = {
        "id": id,
        "text": text,
        "vector": vector,
    }

    # Insert
    con.execute(
        """
    INSERT INTO valid_input (id, reasoner, input, tags)
    VALUES (?, ?, ?, ?)
    """,
        [
            valid_input_record["id"],
            valid_input_record["reasoner"],
            valid_input_record["input"],
            valid_input_record["tags"],
        ],
    )

    con.execute(
        """
    INSERT INTO valid_input_vector (id, text, vector)
    VALUES (?, ?, ?)
    """,
        [
            valid_input_vector_record["id"],
            valid_input_vector_record["text"],
            valid_input_vector_record["vector"],
        ],
    )
    return con, id


if __name__ == "__main__":
    con, id = insert_error(
        reasoner="imandrax",
        input="test input",
        errors=["test error 1", "test error 2"],
        correction="test correction",
        tags=["test insert"],
        embeddings=OpenAIEmbeddings(model="text-embedding-3-small"),
        con=None,
    )
    con, id = insert_valid_input(
        reasoner="imandrax",
        input="test input",
        tags=["test insert"],
        embeddings=OpenAIEmbeddings(model="text-embedding-3-small"),
        con=con,
    )

    dump_db(con, ".")
