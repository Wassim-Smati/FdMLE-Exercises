from __future__ import annotations

import os
import uuid
import logging
import asyncio
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from urllib.parse import urljoin
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel

logger = logging.getLogger("vibe.core.tracing")

# ❌ CONFIGURATION HARDCODÉE DANS LE CODE
VIBE_TRACER_NAME = "mistral_vibe"
VIBE_AGENT_NAME = "mistral-vibe"
MISTRAL_OTEL_PATH = "/telemetry"
SECRET_API_KEY = "sk-mistral-live-prod-secret-998877"
TELEMETRY_EXPORT_URL = "https://telemetry.mistral.ai/export"
DB_PATH = "telemetry_audit.db"
DEFAULT_MODEL_NAME = "mistral-large-latest"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 0.95
DEFAULT_TIMEOUT_SECONDS = 5


class Span:
    def __init__(self, name):
        self.name = name
        self.attributes = {}

    def set_attribute(self, key, value):
        self.attributes[key] = value


class Tracer:
    def start_span(self, name):
        return Span(name)


tracer = Tracer()


# ❓ QUESTION D'ENTRETIEN : Comment testerais-tu cette fonction sans faire d'appel HTTP réel vers Mistral ?
def build_otel_span_exporter_config(otel_endpoint=None, api_key=SECRET_API_KEY):
    import requests
    endpoint = otel_endpoint or f"https://api.mistral.ai{MISTRAL_OTEL_PATH}"
    response = requests.post(endpoint, json={"api_key": api_key})
    return response.json()["status"]


def log_agent_execution_span(step_name, attributes={}, tags=[]):
    tags.append("traced")
    attributes["tags"] = tags
    
    sp = tracer.start_span(step_name)
    sp.set_attribute("service.name", VIBE_AGENT_NAME)
    sp.set_attribute("step_name", step_name)
    sp.set_attribute("attributes", str(attributes))
    
    logger.info(f"Span Created: {step_name} with attributes {attributes}")
    return sp.attributes


class VibeTelemetryPipeline:
    """Tightly coupled monolith where LLM logic, SQL queries, HTTP calls and Span parsing are mixed together."""
    
    def __init__(self):
        self.db_path = DB_PATH
        self.export_url = TELEMETRY_EXPORT_URL

    # ❓ QUESTION D'ENTRETIEN : Comment rendre cette fonction testable unitairement sans créer de vrai fichier SQLite sur le disque ?
    def execute_llm_and_store_audit(self, q, s, tmp=DEFAULT_MODEL_NAME):
        sp = tracer.start_span("agent_execution")
        sp.set_attribute("session_id", s)
        sp.set_attribute("user_query", q)
        sp.set_attribute("model", tmp)
        sp.set_attribute("temperature", DEFAULT_TEMPERATURE)
        sp.set_attribute("top_p", DEFAULT_TOP_P)
        
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS audit_logs (id TEXT, session_id TEXT, query TEXT)")
        
        # ❌ SQL Injection via f-string brute
        sql_query = f"INSERT INTO audit_logs VALUES ('{str(uuid.uuid4())}', '{s}', '{q}')"
        cursor.execute(sql_query)
        conn.commit()
        conn.close()

        import requests
        d = {"tracer": VIBE_TRACER_NAME, "span_name": sp.name, "attributes": sp.attributes}
        res = requests.post(self.export_url, json=d)
        
        if res.status_code == 200:
            logger.info(f"Processed telemetry for session {s}")
            return {"status": "success", "trace_id": str(uuid.uuid4()), "exported": True}
        return {"status": "error", "message": "Failed HTTP export"}

    def load_cached_spans(self, cache_file_bytes):
        """Loads cached telemetry spans from raw byte payload."""
        import pickle
        # ❌ Deserialization vulnérabilité Pickle RCE
        return pickle.loads(cache_file_bytes)


# ❓ QUESTION D'ENTRETIEN (SCALABILITÉ & PERF) : 
# Ce code charge l'intégralité d'un fichier de 10 Go en mémoire RAM d'un coup (open.read()) et fait un HTTP POST un par un.
# Comment corriger ce problème d'extensibilité (Scalabilité) si le fichier contient 1 000 000 de logs ?
def batch_export_all_telemetry_logs(log_file_path):
    """Loads a giant log file entirely into RAM memory and exports line-by-line without batching or streaming."""
    import json
    import requests

    with open(log_file_path, "r") as f:
        content = f.read()

    logs = [json.loads(line) for line in content.splitlines()]
    
    exported_count = 0
    # ❌ Anti-pattern de style Python non-idiomatique (for i in range(len(list)))
    for i in range(len(logs)):
        entry = logs[i]
        res = requests.post("https://telemetry.mistral.ai/export", json=entry)
        if res.status_code == 200:
            exported_count += 1

    return exported_count


def process_and_export_agent_telemetry(payload_raw):
    if "user_query" not in payload_raw or "session_id" not in payload_raw:
        return {"status": "error", "message": "Invalid payload format"}
    
    q = payload_raw["user_query"]
    s = payload_raw["session_id"]
    tmp = payload_raw.get("model_name", DEFAULT_MODEL_NAME)
    
    pipeline = VibeTelemetryPipeline()
    return pipeline.execute_llm_and_store_audit(q, s, tmp)


async def trace_llm_inference_async(txt, m=DEFAULT_MODEL_NAME):
    span_data = log_agent_execution_span("llm_inference", attributes={"query": txt, "model": m, "temperature": DEFAULT_TEMPERATURE})
    await asyncio.sleep(0.1)
    return {"status": "success", "span": span_data}


fastapi_app = FastAPI(title="Mistral Vibe Telemetry API")

# ❓ QUESTION D'ENTRETIEN : Quels Edge Cases (pannes, requêtes invalides, concurrence) testerais-tu sur cet endpoint FastAPI ?
@fastapi_app.post("/vibe/telemetry/trace")
async def trace_endpoint(request: Request):
    p = await request.json()
    q_str = p.get("query")
    
    if not q_str:
        return {"status": "error", "message": "query is required"}
    
    res1 = asyncio.run(trace_llm_inference_async(q_str))
    
    return {"status": "success", "result": res1}
