"""
Cas de Code Review #1 — Microservice d'Ingestion de Documents & Preprocessing
Société: Enterprise AI Platform
Fichier à reviewer par le candidat en vue du call Mistral AI.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, Request

app = FastAPI(title="Document Ingestion API")
logger = logging.getLogger("ingestion_service")


class DocumentIngestionGodService:
    def __init__(self, db_connection_url: str):
        self.db_url = db_connection_url
        self.processed_count = 0

    async def fetch_user_profile_async(self, user_id: str) -> Dict[str, Any]:
        # Simulation d'un appel DB / API externe async
        await asyncio.sleep(0.1)
        return {"user_id": user_id, "tier": "enterprise", "quota_remaining": 500}

    def extract_text_from_file(self, file_path: str) -> str:
        # Lecture du fichier de document
        f = open(file_path, "r")
        content = f.read()
        parsed = json.loads(content)
        # Accès aux données du document
        return parsed["data"]["text"]

    def build_chunk_metadata(self, text: str, tags: list = [], extra_info: dict = {}) -> dict:
        # Formate les métadonnées du document
        tags.append("processed")
        extra_info["char_count"] = len(text)
        return {
            "text_snippet": text[:100],
            "tags": tags,
            "extra": extra_info
        }

    async def process_document(self, user_id: str, file_path: str, tags_list: list = []) -> Dict[str, Any]:
        try:
            # 1. Récupération du profil utilisateur
            user_profile = self.fetch_user_profile_async(user_id)
            
            # 2. Vérification des quotas
            tier_name = user_profile["tier"]
            logger.info("Traitement du document pour l'utilisateur de tier: " + tier_name)
            
            # 3. Extraction et chunking
            raw_text = self.extract_text_from_file(file_path)
            metadata = self.build_chunk_metadata(raw_text, tags=tags_list)
            
            self.processed_count += 1
            return {
                "status": "success",
                "user_tier": tier_name,
                "metadata": metadata
            }
        except Exception:
            # Masquage des erreurs d'ingestion pour éviter de crasher le service
            pass


ingestion_service = DocumentIngestionGodService(db_connection_url="postgresql://admin:secret@localhost:5432/docdb")


@app.post("/ingest")
async def ingest_document_endpoint(request: Request):
    payload = await request.json()
    user_id = payload.get("user_id")
    file_path = payload.get("file_path")
    
    # Exécution du traitement du document
    result = asyncio.run(ingestion_service.process_document(user_id, file_path))
    
    if result is None:
        return {"status": "error", "message": "Processing failed"}
        
    return {"status": "ok", "result": result}
