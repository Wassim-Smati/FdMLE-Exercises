"""
Cas de Code Review #4 — System Design, Async Web APIs & Data Batching
Société: Scale AI Infrastructure Platform
Fichier à reviewer par le candidat en vue du call Mistral AI.
"""

import time
import httpx
import logging
import uuid
from typing import List, Dict, Any
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
import os

app = FastAPI(title="Scale Data Processing API")
logger = logging.getLogger("system_design_service")


class DocumentBatchRepository:
    def __init__(self, db_connection: Any):
        self.db = db_connection

    async def fetch_documents_by_ids(self, document_ids: List[str]) -> List[dict]:
        # Récupération des documents en BDD
        try: 

            placeholders = ", ".join(["%s"] * len(document_ids))
            query = f"SELECT id, title, content FROM documents WHERE id IN ({placeholders})"

            cursor = await self.db.execute(query, tuple(document_ids))
            rows = cursor.fetchall()
            
            return [{"id": row[0], "title": row[1], "content": row[2]} for row in rows]
        
        except Exception as e: 
            logger.info(f'Impossible de récupérer les documents de la BDD, erreur {e}')
            return []


class ExternalIndexingClient:
    async def sync_to_search_engine_with_retry(self, payload: dict, max_retries: int = 3) -> bool:
        # Envoie des données vers un moteur de recherche externe avec retry
        url = os.environ["DB_LINK"]
        idem_id = str(uuid.uuid4())
        headers = {"idempotency_key": idem_id}

        async with httpx.AsyncClient() as client: 
        
            for attempt in range(max_retries):
                try:   
                    response = await client.post(url, json=payload, headers=headers, timeout=5)
                    if response.status_code == 200:
                        return True
                except httpx.RequestError as e: 
                    logger.warning(f"Tentative {attempt + 1} échouée. Information : {e}. Re-tentative...")
                    await asyncio.sleep(2 ** attempt)
                
        return False


def execute_heavy_ocr_processing(file_bytes: bytes, job_id: str) -> str:
    # Traitement lourd simulé
    print(f'Avancement de la tâche {job_id}')
    time.sleep(25)
    return "Contenu extrait du PDF"


repo = DocumentBatchRepository(db_connection=None)
indexing_client = ExternalIndexingClient()

class ValidRequest(BaseModel): 
    document_ids: List[str]

@app.post("/batch_process")
async def batch_process_endpoint(request: ValidRequest):
    document_ids = request.document_ids
    
    # Récupération des documents
    docs = await repo.fetch_documents_by_ids(document_ids)
    
    # Indexation externe
    success = await indexing_client.sync_to_search_engine_with_retry({"count": len(docs)})
    
    if not success:
        raise HTTPException(
            status_code = 502,
            detail="L'indexation externe a échoué après plusieurs tentatives"
        )
        
    return {"status": "success", "processed_count": len(docs)}


@app.post("/process_ocr_pdf")
def process_ocr_pdf_endpoint(request: Request, background_tasks: BackgroundTasks):
    # Traitement du fichier PDF
    file_bytes = b"PDF_CONTENT"
    job_id = str(uuid.uuid4())

    background_tasks.add_task(
        execute_heavy_ocr_processing,
        file_bytes,
        job_id
    )

    return {"status": "completed", "job_id": job_id}
