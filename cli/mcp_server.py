# MNEMOS-OS MCP Server
# Copyright (c) 2026 Jonathan Schoenberger
# Licensed under the GNU General Public License v3.0 (GPLv3)
# See LICENSE file for full license text.

import asyncio
import sys
import os
import json
from mcp.server.fastmcp import FastMCP

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.engine import MnemosCore
from cli.mnemos import GhostBridge, get_active_branch

# Initialize FastMCP server
mcp = FastMCP("MNEMOS-OS")

# MnemosCore and GhostBridge initialization can emit prints that corrupt the MCP stdout stream.
# We redirect stdout to stderr during this phase.
_real_stdout = sys.stdout
sys.stdout = sys.stderr

try:
    # MnemosCore now uses persistent connection pooling for speed & stability
    core = MnemosCore()
finally:
    # Restore stdout for MCP transport
    sys.stdout = _real_stdout

def get_bridge():
    """Helper to get a fresh bridge connection for every request (Stateless)."""
    return GhostBridge(silent=True)

@mcp.tool()
def add_memory(entity: str, aspect: str, text: str, salience: int = 5, file_path: str = None, related_id: int = None) -> str:
    """
    Saves a new fact to the MÍMIR-DB.
    Aspects: PREF, BUG, ARCH, DEP, LOG, ANTI
    Optional: file_path to link this memory to a specific file.
    Optional: related_id to link this memory to a previous decision or fact.
    """
    branch = get_active_branch()
    ghost = get_bridge()
    
    if ghost.is_connected:
        res = ghost.send("add", {
            "entity": entity, "aspect": aspect, "raw_text": text,
            "salience": salience, "file_path": file_path, "related_id": related_id
        }, branch=branch)
        row_id = res.get("id", -1) if res else -1
    else:
        row_id = core.add_fact(entity, aspect, text, salience, file_path=file_path, related_id=related_id, branch_name=branch)
        
    if row_id == -1:
        return "Fact ignored by Salience Filter (too noisy)."
    msg = f"Fact successfully carved into stone (ID: {row_id})."
    if file_path: msg += f" Linked to {file_path}."
    return msg

@mcp.tool()
def get_context(entity: str, limit: int = 15, auto_hydrate: bool = True, relevant_to: str = None, file_path: str = None, last_hash: str = None) -> str:
    """
    Retrieves the active mindset, including the scratchpad and shorthand facts.
    Set auto_hydrate=False for "Low-Power" mode to save tokens.
    Use relevant_to for "Surgical Pre-Filtering."
    Provide file_path to trigger "Active Guardrails" and "Implicit Dependency Mapping."
    Provide last_hash to enable "Context Debouncing" (returns [CONTEXT_UNCHANGED] if identical).
    """
    branch = get_active_branch()
    ghost = get_bridge()
    
    if ghost.is_connected:
        res = ghost.send("context", {
            "entity": entity, "limit": limit, "auto_hydrate": auto_hydrate, 
            "relevant_to": relevant_to, "file_path": file_path, "last_hash": last_hash
        }, branch=branch)
        return res.get("context", "Error retrieving context via Ghost.") if res else "Ghost connection failed."
    
    return core.get_context(entity, limit=limit, branch_name=branch, auto_hydrate=auto_hydrate, relevant_to=relevant_to, file_path=file_path, last_hash=last_hash)

@mcp.tool()
def update_task(task_id: str, status: str) -> str:
    """
    Granularly updates a specific task status in the structured scratchpad JSON.
    Statuses: pending, in_progress, done, failed, validated
    """
    branch = get_active_branch()
    ghost = get_bridge()
    
    if ghost.is_connected:
        res = ghost.send("update_task", {"task_id": task_id, "status": status}, branch=branch)
        success = res.get("success", False) if res else False
    else:
        success = core.update_task(task_id, status, branch_name=branch)
        
    return "Task updated successfully." if success else "Failed to update task. Ensure scratchpad contains a JSON task list."

@mcp.tool()
def get_file_memory(file_path: str) -> str:
    """
    Retrieves memories specifically linked to a file path.
    """
    branch = get_active_branch()
    # Note: engine.get_file_context already traverses parents
    return core.get_file_context(file_path, branch_name=branch)

@mcp.tool()
def get_memory_details(memory_id: int) -> str:
    """
    Retrieves the full, uncompressed content and metadata for a specific memory ID.
    Use this to 'hydrate' a shorthand fact when you need to understand the underlying reasoning or trade-offs.
    """
    ghost = get_bridge()
    if ghost.is_connected:
        res = ghost.send("details", {"memory_id": memory_id})
        details = res.get("details") if res else None
    else:
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
    branch = get_active_branch()
    ghost = get_bridge()
    
    if ghost.is_connected:
        ghost.send("update_scratchpad", {"content": plan}, branch=branch)
    else:
        core.update_scratchpad(plan, branch_name=branch)
        
    return "Scratchpad updated successfully."

@mcp.tool()
def search_memory(query: str) -> str:
    """
    Searches all memories using FTS5 keyword matching.
    """
    branch = get_active_branch()
    ghost = get_bridge()
    
    if ghost.is_connected:
        res = ghost.send("search", {"query": query}, branch=branch)
        results = res.get("results", []) if res else []
    else:
        results = core.search(query, branch_name=branch)
        
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
    ghost = get_bridge()
    if ghost.is_connected:
        res = ghost.send("list_entities")
        entities = res.get("entities", []) if res else []
    else:
        entities = core.list_entities()
        
    return "Known Entities: " + ", ".join(entities) if entities else "No entities found."

if __name__ == "__main__":
    try:
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        # Graceful exit for Ctrl+C
        sys.exit(0)

