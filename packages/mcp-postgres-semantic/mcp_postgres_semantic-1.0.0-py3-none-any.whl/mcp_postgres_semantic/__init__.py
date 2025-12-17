"""MCP Server for PostgreSQL Semantic Search with pgvector."""

from .server import PostgresSemanticServer, main

__version__ = "1.0.0"
__all__ = ["PostgresSemanticServer", "main"]