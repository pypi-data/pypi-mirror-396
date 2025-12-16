"""
By 2025 Oct 24th, langchain-neo4j has not been fully migrated to v1.
Since we are only using the Neo4jGraph class, we copy it here.
"""

from .neo4j_graph import Neo4jGraph

__all__ = ["Neo4jGraph"]
