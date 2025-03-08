"""
A memory server example using SQLite to store and retrieve memories.
This example demonstrates how to create a persistent memory store with ezmcp.
"""

import json
import os
import sqlite3
from datetime import datetime
from typing import Dict, Optional

from ezmcp import TextContent, ezmcp

# Create an ezmcp application
app = ezmcp("memory-server", debug=True)

# SQLite database setup
DB_PATH = "memory.db"


def init_db():
    """Initialize the SQLite database with the required tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create memories table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS memories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT NOT NULL,
        value TEXT NOT NULL,
        metadata TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)

    # Create index on key for faster lookups
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_key ON memories(key)")

    conn.commit()
    conn.close()


@app.tool(description="Store a memory with a key")
async def store_memory(key: str, value: str, metadata: Optional[Dict] = None):
    """
    Store a memory with the given key and value.

    Args:
        key: The key to store the memory under
        value: The value to store
        metadata: Optional metadata to store with the memory

    Returns:
        A confirmation message
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if memory with this key already exists
    cursor.execute("SELECT id FROM memories WHERE key = ?", (key,))
    existing = cursor.fetchone()

    now = datetime.now().isoformat()
    metadata_json = json.dumps(metadata) if metadata else None

    if existing:
        # Update existing memory
        cursor.execute(
            "UPDATE memories SET value = ?, metadata = ?, updated_at = ? WHERE key = ?",
            (value, metadata_json, now, key),
        )
        message = f"Memory with key '{key}' updated successfully"
    else:
        # Insert new memory
        cursor.execute(
            "INSERT INTO memories (key, value, metadata, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (key, value, metadata_json, now, now),
        )
        message = f"Memory with key '{key}' stored successfully"

    conn.commit()
    conn.close()

    return [TextContent(type="text", text=message)]


@app.tool(description="Retrieve a memory by key")
async def retrieve_memory(key: str):
    """
    Retrieve a memory by its key.

    Args:
        key: The key of the memory to retrieve

    Returns:
        The memory value and metadata if found, otherwise a not found message
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT value, metadata, created_at, updated_at FROM memories WHERE key = ?",
        (key,),
    )
    result = cursor.fetchone()
    conn.close()

    if result:
        value, metadata_json, created_at, updated_at = result
        metadata = json.loads(metadata_json) if metadata_json else None

        response = {
            "key": key,
            "value": value,
            "metadata": metadata,
            "created_at": created_at,
            "updated_at": updated_at,
        }

        return [TextContent(type="text", text=json.dumps(response, indent=2))]
    else:
        return [TextContent(type="text", text=f"No memory found with key '{key}'")]


@app.tool(description="List all stored memories")
async def list_memories(limit: int = 10, offset: int = 0):
    """
    List all stored memories with pagination.

    Args:
        limit: Maximum number of memories to return
        offset: Number of memories to skip

    Returns:
        A list of stored memories
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get total count
    cursor.execute("SELECT COUNT(*) FROM memories")
    total = cursor.fetchone()[0]

    # Get paginated results
    cursor.execute(
        "SELECT key, value, metadata, created_at, updated_at FROM memories ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (limit, offset),
    )
    results = cursor.fetchall()
    conn.close()

    memories = []
    for key, value, metadata_json, created_at, updated_at in results:
        metadata = json.loads(metadata_json) if metadata_json else None
        memories.append(
            {
                "key": key,
                "value": value,
                "metadata": metadata,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )

    response = {"total": total, "limit": limit, "offset": offset, "memories": memories}

    return [TextContent(type="text", text=json.dumps(response, indent=2))]


@app.tool(description="Delete a memory by key")
async def delete_memory(key: str):
    """
    Delete a memory by its key.

    Args:
        key: The key of the memory to delete

    Returns:
        A confirmation message
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM memories WHERE key = ?", (key,))
    deleted = cursor.rowcount > 0

    conn.commit()
    conn.close()

    if deleted:
        return [
            TextContent(
                type="text", text=f"Memory with key '{key}' deleted successfully"
            )
        ]
    else:
        return [TextContent(type="text", text=f"No memory found with key '{key}'")]


@app.tool(description="Search memories by value")
async def search_memories(query: str, limit: int = 10):
    """
    Search memories by value containing the query string.

    Args:
        query: The search query
        limit: Maximum number of results to return

    Returns:
        A list of matching memories
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT key, value, metadata, created_at, updated_at FROM memories WHERE value LIKE ? ORDER BY created_at DESC LIMIT ?",
        (f"%{query}%", limit),
    )
    results = cursor.fetchall()
    conn.close()

    if not results:
        return [TextContent(type="text", text=f"No memories found matching '{query}'")]

    memories = []
    for key, value, metadata_json, created_at, updated_at in results:
        metadata = json.loads(metadata_json) if metadata_json else None
        memories.append(
            {
                "key": key,
                "value": value,
                "metadata": metadata,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )

    response = {"query": query, "count": len(memories), "memories": memories}

    return [TextContent(type="text", text=json.dumps(response, indent=2))]


if __name__ == "__main__":
    # Initialize the database
    init_db()

    print("Starting memory server on http://localhost:8000")
    print("SQLite database initialized at:", os.path.abspath(DB_PATH))
    print("\nAvailable tools:")
    for name, tool_info in app.tools.items():
        print(f"  - {name}: {tool_info['schema'].description}")
    print("\nDocumentation available at: http://localhost:8000/docs")
    print("SSE endpoint available at: http://localhost:8000/sse")
    print("\nPress Ctrl+C to stop the server")

    # Run the application
    app.run(host="0.0.0.0", port=8000)
