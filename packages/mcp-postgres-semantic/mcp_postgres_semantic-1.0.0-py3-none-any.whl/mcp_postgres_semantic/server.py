#!/usr/bin/env python3
"""
MCP Server for PostgreSQL Semantic Search with pgvector and OpenAI embeddings.
Generic server that works with any PostgreSQL database containing vector embeddings.
"""

import asyncio
import json
import logging
import os
from typing import Any, Optional
from contextlib import asynccontextmanager

import psycopg2
from psycopg2.extras import RealDictCursor
import openai
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, CallToolResult

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mcp-postgres-semantic")


class PostgresSemanticServer:
    """MCP Server for semantic search on PostgreSQL with pgvector."""
    
    def __init__(
        self,
        database_url: str,
        openai_api_key: str,
        embedding_model: str = "text-embedding-3-small",
        embedding_dimension: int = 1536
    ):
        self.database_url = database_url
        self.embedding_model = embedding_model
        self.embedding_dimension = embedding_dimension
        
        # Initialize OpenAI client
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        
        # Initialize MCP server
        self.server = Server("postgres-semantic-search")
        
        # Setup request handlers
        self._setup_handlers()
        
        logger.info(f"Initialized PostgreSQL Semantic Search MCP Server")
        logger.info(f"Embedding model: {embedding_model}")
    
    def _setup_handlers(self):
        """Setup MCP request handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """List available semantic search tools."""
            return [
                Tool(
                    name="semantic_search",
                    description=(
                        "Perform semantic search on any table with vector embeddings. "
                        "Finds records conceptually similar to the query text."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "table_name": {
                                "type": "string",
                                "description": "Name of the table to search"
                            },
                            "embedding_column": {
                                "type": "string",
                                "description": "Name of the vector embedding column",
                                "default": "embedding"
                            },
                            "query": {
                                "type": "string",
                                "description": "Natural language search query"
                            },
                            "columns": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Columns to return (default: all)",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results",
                                "default": 20,
                                "minimum": 1,
                                "maximum": 100
                            },
                            "min_similarity": {
                                "type": "number",
                                "description": "Minimum similarity score (0-1)",
                                "default": 0.0,
                                "minimum": 0.0,
                                "maximum": 1.0
                            }
                        },
                        "required": ["table_name", "query"]
                    }
                ),
                Tool(
                    name="semantic_search_filtered",
                    description=(
                        "Semantic search with additional WHERE conditions. "
                        "Supports complex filtering with SQL WHERE clause."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "table_name": {"type": "string"},
                            "embedding_column": {
                                "type": "string",
                                "default": "embedding"
                            },
                            "query": {"type": "string"},
                            "columns": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "where_clause": {
                                "type": "string",
                                "description": "SQL WHERE clause (without 'WHERE' keyword)"
                            },
                            "where_params": {
                                "type": "array",
                                "description": "Parameters for WHERE clause placeholders"
                            },
                            "limit": {
                                "type": "integer",
                                "default": 20,
                                "minimum": 1,
                                "maximum": 100
                            },
                            "min_similarity": {
                                "type": "number",
                                "default": 0.0
                            }
                        },
                        "required": ["table_name", "query"]
                    }
                ),
                Tool(
                    name="list_vector_tables",
                    description="List all tables that contain vector embedding columns",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="get_table_schema",
                    description="Get schema information for a table",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "table_name": {
                                "type": "string",
                                "description": "Name of the table"
                            }
                        },
                        "required": ["table_name"]
                    }
                ),
                Tool(
                    name="generate_embedding",
                    description="Generate embedding vector for text",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "Text to generate embedding for"
                            }
                        },
                        "required": ["text"]
                    }
                ),
                Tool(
                    name="create_vector_index",
                    description=(
                        "Create IVFFLAT index on embedding column for faster searches. "
                        "Recommended for tables with >10,000 rows."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "table_name": {"type": "string"},
                            "embedding_column": {
                                "type": "string",
                                "default": "embedding"
                            },
                            "lists": {
                                "type": "integer",
                                "description": "Number of lists for IVF (default: 100)",
                                "default": 100
                            }
                        },
                        "required": ["table_name"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(
            name: str,
            arguments: dict[str, Any]
        ) -> list[TextContent]:
            """Handle tool execution requests."""
            try:
                if name == "semantic_search":
                    result = await self.semantic_search(arguments)
                elif name == "semantic_search_filtered":
                    result = await self.semantic_search_filtered(arguments)
                elif name == "list_vector_tables":
                    result = await self.list_vector_tables()
                elif name == "get_table_schema":
                    result = await self.get_table_schema(arguments)
                elif name == "generate_embedding":
                    result = await self.generate_embedding_tool(arguments)
                elif name == "create_vector_index":
                    result = await self.create_vector_index(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                
                return [TextContent(type="text", text=result)]
                
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}", exc_info=True)
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
    
    def _get_connection(self):
        """Get database connection."""
        return psycopg2.connect(self.database_url)
    
    async def _generate_embedding(self, text: str) -> list[float]:
        """Generate embedding for text using OpenAI."""
        try:
            response = self.openai_client.embeddings.create(
                input=text,
                model=self.embedding_model
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    async def semantic_search(self, args: dict[str, Any]) -> str:
        """Perform semantic search on a table."""
        table_name = args["table_name"]
        embedding_column = args.get("embedding_column", "embedding")
        query = args["query"]
        columns = args.get("columns", ["*"])
        limit = args.get("limit", 20)
        min_similarity = args.get("min_similarity", 0.0)
        
        logger.info(f"Semantic search on {table_name} for: {query[:50]}...")
        
        # Generate query embedding
        query_embedding = await self._generate_embedding(query)
        embedding_str = f"[{','.join(map(str, query_embedding))}]"
        
        # Build column list
        column_list = ", ".join(columns) if columns != ["*"] else "*"
        
        # Execute search
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                sql = f"""
                    SELECT 
                        {column_list},
                        1 - ({embedding_column} <=> %s::vector) as similarity
                    FROM {table_name}
                    WHERE 1 - ({embedding_column} <=> %s::vector) >= %s
                    ORDER BY {embedding_column} <=> %s::vector
                    LIMIT %s
                """
                cur.execute(sql, (embedding_str, embedding_str, min_similarity, embedding_str, limit))
                results = cur.fetchall()
                
                # Format results
                output = {
                    "query": query,
                    "table": table_name,
                    "count": len(results),
                    "results": [dict(row) for row in results]
                }
                
                return json.dumps(output, indent=2, default=str)
        finally:
            conn.close()
    
    async def semantic_search_filtered(self, args: dict[str, Any]) -> str:
        """Semantic search with WHERE clause filtering."""
        table_name = args["table_name"]
        embedding_column = args.get("embedding_column", "embedding")
        query = args["query"]
        columns = args.get("columns", ["*"])
        where_clause = args.get("where_clause", "")
        where_params = args.get("where_params", [])
        limit = args.get("limit", 20)
        min_similarity = args.get("min_similarity", 0.0)
        
        logger.info(f"Filtered semantic search on {table_name}")
        
        # Generate query embedding
        query_embedding = await self._generate_embedding(query)
        embedding_str = f"[{','.join(map(str, query_embedding))}]"
        
        # Build column list
        column_list = ", ".join(columns) if columns != ["*"] else "*"
        
        # Build WHERE clause
        where_sql = f"AND ({where_clause})" if where_clause else ""
        
        # Execute search
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                sql = f"""
                    SELECT 
                        {column_list},
                        1 - ({embedding_column} <=> %s::vector) as similarity
                    FROM {table_name}
                    WHERE 1 - ({embedding_column} <=> %s::vector) >= %s
                        {where_sql}
                    ORDER BY {embedding_column} <=> %s::vector
                    LIMIT %s
                """
                params = [embedding_str, embedding_str, min_similarity] + where_params + [embedding_str, limit]
                cur.execute(sql, params)
                results = cur.fetchall()
                
                output = {
                    "query": query,
                    "table": table_name,
                    "filters": where_clause,
                    "count": len(results),
                    "results": [dict(row) for row in results]
                }
                
                return json.dumps(output, indent=2, default=str)
        finally:
            conn.close()
    
    async def list_vector_tables(self) -> str:
        """List all tables with vector columns."""
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        t.table_name,
                        c.column_name,
                        c.data_type,
                        c.udt_name
                    FROM information_schema.tables t
                    JOIN information_schema.columns c 
                        ON t.table_name = c.table_name
                    WHERE c.udt_name = 'vector'
                        AND t.table_schema = 'public'
                    ORDER BY t.table_name, c.column_name
                """)
                results = cur.fetchall()
                
                # Group by table
                tables = {}
                for row in results:
                    table = row['table_name']
                    if table not in tables:
                        tables[table] = []
                    tables[table].append(row['column_name'])
                
                output = {
                    "vector_tables": [
                        {"table": table, "vector_columns": cols}
                        for table, cols in tables.items()
                    ]
                }
                
                return json.dumps(output, indent=2)
        finally:
            conn.close()
    
    async def get_table_schema(self, args: dict[str, Any]) -> str:
        """Get schema information for a table."""
        table_name = args["table_name"]
        
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        column_name,
                        data_type,
                        udt_name,
                        is_nullable,
                        column_default
                    FROM information_schema.columns
                    WHERE table_name = %s
                        AND table_schema = 'public'
                    ORDER BY ordinal_position
                """, (table_name,))
                results = cur.fetchall()
                
                output = {
                    "table": table_name,
                    "columns": [dict(row) for row in results]
                }
                
                return json.dumps(output, indent=2)
        finally:
            conn.close()
    
    async def generate_embedding_tool(self, args: dict[str, Any]) -> str:
        """Generate embedding for text."""
        text = args["text"]
        embedding = await self._generate_embedding(text)
        
        output = {
            "text": text[:100] + "..." if len(text) > 100 else text,
            "model": self.embedding_model,
            "dimension": len(embedding),
            "embedding": embedding
        }
        
        return json.dumps(output, indent=2)
    
    async def create_vector_index(self, args: dict[str, Any]) -> str:
        """Create IVFFLAT index on embedding column."""
        table_name = args["table_name"]
        embedding_column = args.get("embedding_column", "embedding")
        lists = args.get("lists", 100)
        
        index_name = f"{table_name}_{embedding_column}_idx"
        
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                # Check if index exists
                cur.execute("""
                    SELECT indexname 
                    FROM pg_indexes 
                    WHERE tablename = %s AND indexname = %s
                """, (table_name, index_name))
                
                if cur.fetchone():
                    return json.dumps({
                        "status": "exists",
                        "message": f"Index {index_name} already exists"
                    })
                
                # Create index
                cur.execute(f"""
                    CREATE INDEX {index_name}
                    ON {table_name}
                    USING ivfflat ({embedding_column} vector_cosine_ops)
                    WITH (lists = {lists})
                """)
                conn.commit()
                
                return json.dumps({
                    "status": "created",
                    "index_name": index_name,
                    "table": table_name,
                    "column": embedding_column,
                    "lists": lists
                })
        finally:
            conn.close()
    
    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="postgres-semantic-search",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )


def main():
    """Main entry point."""
    # Get configuration from environment
    database_url = os.getenv("DATABASE_URL")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    
    if not database_url:
        logger.error("DATABASE_URL environment variable is required")
        return 1
    
    if not openai_api_key:
        logger.error("OPENAI_API_KEY environment variable is required")
        return 1
    
    # Create and run server
    server = PostgresSemanticServer(
        database_url=database_url,
        openai_api_key=openai_api_key,
        embedding_model=embedding_model
    )
    
    asyncio.run(server.run())
    return 0


if __name__ == "__main__":
    exit(main())