"""
Cas de Code Review #4 — System Design, Async Web APIs & Data Batching
Société: Scale AI Infrastructure Platform
Fichier à reviewer par le candidat en vue du call Mistral AI.
"""

import time
import requests
import logging
from typing import List, Dict, Any
from fastapi import FastAPI, Request

app = FastAPI(title="Scale Data Processing API")
logger = logging.getLogger("system_design_service")


class DocumentBatchRepository:
    def __init__(self, db_connection: Any):
        self.db = db_connection

    def fetch_documents_by_ids(self, document_ids: List[str]) -> List[dict]:
        # Récupération des documents en BDD
        results = []
        for doc_id in document_ids:
            cursor = self.db.execute("SELECT id, title, content FROM documents WHERE id = %s", (doc_id,))
            row = cursor.fetchone()
            if row:
                results.append({"id": row[0], "title": row[1], "content": row[2]})
        return results


class ExternalIndexingClient:
    def sync_to_search_engine_with_retry(self, payload: dict, max_retries: int = 3) -> bool:
        # Envoie des données vers un moteur de recherche externe avec retry
        url = "https://search-engine.internal/api/v1/index"
        
        for attempt in range(max_retries):
            response = requests.post(url, json=payload, timeout=5)
            if response.status_code == 200:
                return True
            logger.warning(f"Tentative {attempt + 1} échouée. Re-tentative...")
            time.sleep(1)
            
        return False


def execute_heavy_ocr_processing(file_bytes: bytes) -> str:
    # Traitement lourd simulé
    time.sleep(25)
    return "Contenu extrait du PDF"


repo = DocumentBatchRepository(db_connection=None)
indexing_client = ExternalIndexingClient()


@app.post("/batch_process")
async def batch_process_endpoint(request: Request):
    payload = await request.json()
    document_ids = payload.get("document_ids")
    
    if not document_ids:
        return {"status": "error", "message": "document_ids is required"}
    
    # Récupération des documents
    docs = repo.fetch_documents_by_ids(document_ids)
    
    # Indexation externe
    success = indexing_client.sync_to_search_engine_with_retry({"count": len(docs)})
    
    if not success:
        return {"status": "error", "message": "Indexing failed after retries"}
        
    return {"status": "success", "processed_count": len(docs)}


@app.post("/process_ocr_pdf")
def process_ocr_pdf_endpoint(request: Request):
    # Traitement du fichier PDF
    file_bytes = b"PDF_CONTENT"
    extracted_text = execute_heavy_ocr_processing(file_bytes)
    
    return {"status": "completed", "extracted_text": extracted_text}
