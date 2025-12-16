from pathlib import Path

import duckdb
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from utils.rag.vectorstore import IUDuckDBVectorStore

# extract RAG to common utils
# find a better place to put schemas (maybe in data/)
# TODO: a consolidated IUDB class?

data_dir = Path(__file__).parent / "data"
error_schema = {
    "id": "VARCHAR",
    "reasoner": "VARCHAR",
    "input": "VARCHAR",
    "errors": "VARCHAR[]",
    "correction": "VARCHAR",
    "tags": "VARCHAR[]",
}

valid_input_schema = {
    "id": "VARCHAR",
    "reasoner": "VARCHAR",
    "input": "VARCHAR",
    "tags": "VARCHAR[]",
}

vector_schema = {
    "id": "VARCHAR",
    "text": "VARCHAR",
    "vector": "FLOAT[]",
}


def connect_duckdb(reasoner: str) -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()

    # Create tables
    con.execute(
        """
        CREATE TABLE error (
            id VARCHAR PRIMARY KEY,
            reasoner VARCHAR,
            input VARCHAR,
            errors VARCHAR[],
            correction VARCHAR,
            tags VARCHAR[]
        );
        
        CREATE TABLE valid_input (
            id VARCHAR PRIMARY KEY,
            reasoner VARCHAR,
            input VARCHAR,
            tags VARCHAR[]
        );
    """
    )

    # Load data into main tables
    con.execute(
        """
        INSERT INTO error 
        SELECT * FROM read_json_auto(?, format='array', columns=?)
        WHERE reasoner = ?
    """,
        [str(data_dir / "doc/error.json"), error_schema, reasoner],
    )

    con.execute(
        """
        INSERT INTO valid_input 
        SELECT * FROM read_json_auto(?, format='array', columns=?)
        WHERE reasoner = ?
    """,
        [str(data_dir / "doc/valid_input.json"), valid_input_schema, reasoner],
    )

    # Create vector tables with FOREIGN KEY constraints
    con.execute(
        """
        CREATE TABLE error_vector (
            id VARCHAR PRIMARY KEY,
            text VARCHAR,
            vector FLOAT[],
            FOREIGN KEY (id) REFERENCES error(id)
        );
        
        CREATE TABLE valid_input_vector (
            id VARCHAR PRIMARY KEY,
            text VARCHAR,
            vector FLOAT[],
            FOREIGN KEY (id) REFERENCES valid_input(id)
        );
    """
    )

    # Load data into vector tables
    con.execute(
        """
        INSERT INTO error_vector
        SELECT v.* FROM read_json_auto(?, format='array', columns=?) AS v
        INNER JOIN error e ON v.id = e.id
    """,
        [str(data_dir / "vector/error.json"), vector_schema],
    )

    con.execute(
        """
        INSERT INTO valid_input_vector
        SELECT v.* FROM read_json_auto(?, format='array', columns=?) AS v
        INNER JOIN valid_input vi ON v.id = vi.id
    """,
        [str(data_dir / "vector/valid_input.json"), vector_schema],
    )

    return con


def load_vector_store(
    con: duckdb.DuckDBPyConnection,
    embeddings: OpenAIEmbeddings | None = None,
) -> dict[str, IUDuckDBVectorStore]:
    if embeddings is None:
        embedding_model = "text-embedding-3-small"
        embeddings = OpenAIEmbeddings(model=embedding_model)

    error_vector_store = IUDuckDBVectorStore(
        connection=con,
        embedding=embeddings,
        vector_key="vector",
        id_key="id",
        text_key="text",
        table_name="error_vector",
    )

    valid_input_vector_store = IUDuckDBVectorStore(
        connection=con,
        embedding=embeddings,
        vector_key="vector",
        id_key="id",
        text_key="text",
        table_name="valid_input_vector",
    )

    return {
        "error_vector": error_vector_store,
        "valid_input": valid_input_vector_store,
    }


def ctxlize_errors(
    docs: list[Document],
    con: duckdb.DuckDBPyConnection,
) -> list[str]:
    """Get the context string for the error from retrieved `Document`"""
    errors: list[dict] = (
        con.execute(
            """SELECT * FROM error WHERE id IN ?""",
            [[doc.id for doc in docs]],
        )
        .df()
        .to_dict(orient="records")
    )
    return [item["correction"] for item in errors]


def ctxlize_valid_inputs(
    docs: list[Document],
    con: duckdb.DuckDBPyConnection,
) -> list[str]:
    """Get the context string for the valid input from retrieved `Document`"""
    valid_inputs: list[dict] = (
        con.execute(
            """SELECT * FROM valid_input WHERE id IN ?""",
            [[doc.id for doc in docs]],
        )
        .df()
        .to_dict(orient="records")
    )
    return [f"`{item['input']}`" for item in valid_inputs]
