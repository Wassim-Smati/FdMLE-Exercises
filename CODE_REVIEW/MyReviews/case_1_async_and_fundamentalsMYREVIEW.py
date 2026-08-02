"""
Cas de Code Review #1 — Microservice d'Ingestion de Documents & Preprocessing
Société: Enterprise AI Platform
Fichier à reviewer par le candidat en vue du call Mistral AI.
"""
import os 
import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, Request

app = FastAPI(title="Document Ingestion API")
logger = logging.getLogger("ingestion_service")

class ParsedText(BaseModel):
    data: dict

async def fetch_user_profile_async(user_id: str) -> Dict[str, Any]:
    # Simulation d'un appel DB / API externe async
    await asyncio.sleep(0.1)
    return {"user_id": user_id, "tier": "enterprise", "quota_remaining": 500}

def extract_text_from_file(file_path: str) -> str:
        # Lecture du fichier de document
        with open(file_path, "r") as f:
            content = f.read()
            parsed = ParsedText.model_validate(json.loads(content))
            # Accès aux données du document
            return parsed.data["text"]

def build_chunk_metadata(text: str, tags: list = None, extra_info: dict = None) -> dict:
    if not tags:
        tags = []
    if not extra_info: 
        extra_info = {}

    # Formate les métadonnées du document
    tags.append("processed")
    extra_info["char_count"] = len(text)
    return {
        "text_snippet": text[:100],
        "tags": tags,
        "extra": extra_info
    }

class DocumentIngestionService:
    def __init__(self, db_connection_url: str):
        self.db_url = db_connection_url
        self.processed_count = 0

    async def process_document(self, user_id: str, file_path: str, tags_list: list = None) -> Dict[str, Any]:
        try:
            if not tags_list: 
                tags_list = []

            # 1. Récupération du profil utilisateur
            user_profile = await fetch_user_profile_async(user_id)
            
            # 2. Vérification des quotas
            tier_name = user_profile["tier"]
            logger.info("Traitement du document pour l'utilisateur de tier: " + tier_name)
            
            # 3. Extraction et chunking
            raw_text = extract_text_from_file(file_path)
            metadata = build_chunk_metadata(raw_text, tags=tags_list)
            
            self.processed_count += 1
            return {
                "status": "success",
                "user_tier": tier_name,
                "metadata": metadata
            }
        except Exception:
            logger.exception(
                "Unexpected error while processing document for user_id=%s, file_path=%s",
                user_id, 
                file_path)
            raise


ingestion_service = DocumentIngestionService(db_connection_url=os.environ["DATABASE_URL"])

class IngestPayload(BaseModel): 
    user_id : str
    file_path : str

@app.post("/ingest")
async def ingest_document_endpoint(payload: IngestPayload):

    user_id = payload.user_id
    file_path = payload.file_path
    
    # Exécution du traitement du document
    result = await ingestion_service.process_document(user_id, file_path)
    
    if result is None:
        return {"status": "error", "message": "Processing failed"}
        
    return {"status": "ok", "result": result}
