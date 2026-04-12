# MNEMOS-OS MCP Server
# Copyright (c) 2026 Jonathan Schoenberger
# Licensed under the GNU General Public License v3.0 (GPLv3)
# See LICENSE file for full license text.

import asyncio
import sys
import os
from mcp.server.fastmcp import FastMCP

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.engine import MnemosCore

# Initialize FastMCP server
mcp = FastMCP("MNEMOS")
core = MnemosCore()

@mcp.tool()
def add_memory(entity: str, aspect: str, text: str, salience: int = 5, file_path: str = None, related_id: int = None) -> str:
    """
    Saves a new fact to the MÍMIR-DB.
    Aspects: PREF, BUG, ARCH, DEP, LOG, ANTI
    Optional: file_path to link this memory to a specific file.
    Optional: related_id to link this memory to a previous decision or fact.
    """
    row_id = core.add_fact(entity, aspect, text, salience, file_path=file_path, related_id=related_id)
    if row_id == -1:
        return "Fact ignored by Salience Filter (too noisy)."
    msg = f"Fact successfully carved into stone (ID: {row_id})."
    if file_path: msg += f" Linked to {file_path}."
    return msg

@mcp.tool()
def get_context(entity: str, limit: int = 15) -> str:
    """
    Retrieves the active mindset, including the scratchpad and shorthand facts.
    """
    return core.get_context(entity, limit=limit)

@mcp.tool()
def get_file_memory(file_path: str) -> str:
    """
    Retrieves memories specifically linked to a file path.
    """
    return core.get_file_context(file_path)

@mcp.tool()
def get_memory_details(memory_id: int) -> str:
    """
    Retrieves the full, uncompressed content and metadata for a specific memory ID.
    Use this to 'hydrate' a shorthand fact when you need to understand the underlying reasoning or trade-offs.
    """
    details = core.get_memory_details(memory_id)
    if not details:
        return f"Memory with ID {memory_id} not found."
    
    output = f"--- MEMORY HYDRATION [ID: {memory_id}] ---\n"
    output += f"ENTITY:  {details['entity']}\n"
    output += f"ASPECT:  {details['aspect']}\n"
    output += f"CREATED: {details['created']}\n"
    output += f"SHORTHAND: {details['shorthand']}\n"
    output += f"--- RAW CONTENT ---\n"
    output += f"{details['raw']}\n"
    output += f"--- END ---"
    return output

@mcp.tool()
def update_scratchpad(plan: str) -> str:
    """
    Updates the persistent session scratchpad for multi-step task tracking.
    """
    core.update_scratchpad(plan)
    return "Scratchpad updated successfully."

@mcp.tool()
def search_memory(query: str) -> str:
    """
    Searches all memories using FTS5 keyword matching.
    """
    results = core.search(query)
    if not results:
        return "No matches found."
    
    output = "ENTITY     | TYPE  | SHORTHAND\n" + "-"*40 + "\n"
    for r in results:
        output += f"{r[0]:<10} | {r[1]:<5} | {r[2]}\n"
    return output

@mcp.tool()
def list_entities() -> str:
    """
    Returns a list of all existing projects/entities in the memory database.
    Use this to see what other knowledge bases you can query.
    """
    entities = core.list_entities()
    return "Known Entities: " + ", ".join(entities) if entities else "No entities found."

if __name__ == "__main__":
    try:
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        # Graceful exit for Ctrl+C
        sys.exit(0)

