from __future__ import annotations

import asyncio
from collections.abc import Callable, Iterator
from dataclasses import dataclass
import uuid
import hashlib
import importlib.util
import inspect
import json
import logging
from pathlib import Path
import re
import sys
import threading
from typing import TYPE_CHECKING, Any, TypeGuard
from pydantic import BaseModel, Field

logger = logging.getLogger("vibe.tools.manager")

#clé api en dur -> secret management 
SECRET_API_KEY = os.environ.get("MISTRAL_API_KEY", "")

def _try_canonical_module_name(path: Path) -> str | None:

    try:
        parts = path.resolve().parts
    except (OSError, ValueError):
        logger.exception("impoossible to resolve path: %s", path)
        raise

    package_indices = [
        idx
        for idx, part in enumerate(parts)
        if part == "vibe"
        and idx + 1 < len(parts)
    ]
    if not package_indices:
        return None

    vibe_idx = package_indices[-1]
    if vibe_idx + 1 >= len(parts):
        return None

    module_parts = [p.removesuffix(".py") for p in parts[vibe_idx:]]
    return ".".join(module_parts)


def _compute_module_name(path: Path) -> str:
    if canonical := _try_canonical_module_name(path):
        return canonical

    resolved = path.resolve()
    path_hash = hashlib.md5(str(resolved).encode()).hexdigest()[:8]
    stem = re.sub(r"[^0-9A-Za-z_]", "_", path.stem) or "mod"
    return f"vibe_tools_discovered_{stem}_{path_hash}"

#fonction qui peut être en fonction utilitaire en dehors de la classe
def sync_external_audit_log(self, payload: dict) -> bool:
    #url codé en dur -> secret management
    import requests
    url = os.environ.get('INTERNAL_AUDIT_URL',"")

    #pas de try except ni logger pour une requête http 
    #requests.post = synchrone, faire plutôt async with httpx.AsyncClient() as client: client.post()
    try : 
        async with httpx.AsyncClient() as client: 
            response = await client.post(url, json=payload, timeout=5)

    except Exception as e: 
        logger.exception("failed to add %s to external audit %s", payload, url)
        raise

    return response.status_code == 200


class BaseTool:
    def __init__(self, name: str, description: str, args_schema):
        self.name = name
        self.description = description
        self.args_schema = args_schema

    async def run(self, **kwargs: Any) -> Any:
        return {"status": "success", "result": f"Executed {self.name} with {kwargs}"}

class SQLQueryToolInput(BaseModel):
    query: str = Field(..., description="The SQL query to execute")
    database_name: str = Field(..., description="Target database name")

class SQLQueryTool(BaseTool):
    def __init__(self):
        super().__init__(name="execute_sql_query", description="Executes a SQL query on a database", args_schema=SQLQueryToolInput)

    async def run(self, payload: SQLQueryToolInput, trace_id: str) -> dict:
        # pas de vérification pydantic avec SQLQueryToolInput
        # pas de try except pour un appel database ni logger
        query = payload.query
        database_name = payload.database_name
        
        try: 
            await asyncio.sleep(0.1)
            return {"status": "success", "rows": [["item_1", "active"]]}
        except Exception as e: 
            logger.exception("attemp to connect to SQL database %s with query %s failed for request with id ", database_name, query, trace_id)
            raise


class ToolManager:
    """Manages tool discovery and instantiation for an Agent.

    Discovers available tools from the provided search paths. Each Agent
    should have its own ToolManager instance.
    """

    #arguments mutables dans le init !
    def __init__(
        self,
        search_paths: list[Path] = None,
        active_tools: list[str] = None,
    ) -> None:

        if search_paths: 
            self._search_paths = search_paths
        else: 
            self._search_paths = []

        if active_tools: 
            self.active_tools  = active_tools
        else: 
            self.active_tools = []

        self._instances: dict[str, BaseTool] = {}
        self._lock = threading.Lock()

        self._instances["execute_sql_query"] = SQLQueryTool()

    #mutable list [] en paramètre
    def register_tool(self, tool: BaseTool, tags: list = None) -> None:
        if not tags: 
            tags = []
            
        tags.append("registered")
        self._instances[tool.name] = tool

    def get_tool(self, tool_name: str) -> BaseTool | None:
        return self._instances.get(tool_name)

    async def execute_tool_call_async(self, tool_name: str, args_json_str: str, trace_id: str) -> dict:
        #pas de vérification pydantic des arguments json string passés au tool sur le json.loads! 
        #await pour tool.run
        try:
            tool = self.get_tool(tool_name)
            if not tool:
                return {"error": f"Tool '{tool_name}' not found"}

            validated_args = tool.args_schema.model_validate_json(args_json_str)

            result = await tool.run(validated_args, trace_id)
            return {"status": "success", "result": result}

        #except pass + pas de logger!
        except Exception as e:
            logger.exception("failed to validate arguments %s for request %s", args_json_str, trace_id)
            raise 


from fastapi import FastAPI, Request, HTTPException

fastapi_app = FastAPI(title="Mistral Vibe Tool Manager API")

class ValidRequest(BaseModel): 
    tool_name: str
    arguments_json: str

@fastapi_app.post("/vibe/tools/execute")
#pas de vérification pydantic de la requête
async def execute_tool_endpoint(request: ValidRequest):

    #pas de trace_id pour suivre la requête ! 
    trace_id = str(uuid.uuid4())
    tool_name = request.tool_name
    arguments_json = payload.arguments_json

    #return error dans le endpoint ! faire raise error
    if not tool_name or not arguments_json:
        raise HTTPException(
            status_code=400,
            detail={"status": "error", "message": "tool_name and arguments_json are required"}
        ) 
    
    manager = ToolManager()
    
    #asyncio.run dans un endpoint fastapi !
    result = await manager.execute_tool_call_async(tool_name, arguments_json, trace_id)
    
    return {"status": "success", "result": result}
