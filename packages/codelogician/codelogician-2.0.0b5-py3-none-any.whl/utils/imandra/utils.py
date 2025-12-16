import os

from cachetools import TTLCache, cached
from neo4j import GraphDatabase


@cached(cache=TTLCache(maxsize=1, ttl=3600))
def available_reasoners() -> list[str]:
    with GraphDatabase.driver(
        os.environ["NEO4J_URI"],
        auth=(os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"]),
    ) as driver:
        reasoners, _, _ = driver.execute_query("MATCH (r:Reasoner) RETURN r.id as id")
    return [reasoner.data()["id"] for reasoner in reasoners]
