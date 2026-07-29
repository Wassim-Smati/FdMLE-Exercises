"""
================================================================================
CORRECTION OFFICIELLE — CAS DE CODE REVIEW #4
Secteur: System Design, Async Web APIs & Data Batching (Mistral FDE)
================================================================================

LISTE DES FAILLES IDENTIFIÉES & IMPACTS :

1. 🔴 Ligne 54 & 64: Codes de Statut HTTP Inappropriés (FastAPI renvoie 200 OK en cas d'erreur)
   - Impact Observabilité: Trompe les tableaux de bord et le monitoring APM (les sondes affichent 100% de succès alors que le service échoue).
   - Correction: Lever `HTTPException` avec les bons codes (400 Client Error, 502 Bad Gateway).

2. 🔴 Ligne 32: Retries d'Écritures HTTP POST sans Clé d'Idempotence
   - Impact Scalabilité: Risques de Thundering Herd Problem, créations de doublons en BDD et corruption d'état.
   - Correction: Transmettre un header `Idempotency-Key` (UUID) sur chaque requête POST/PUT réessayée.

3. 🔴 Ligne 19: Requêtes N+1 de BDD dans une boucle `for` (`fetch_documents_by_ids`)
   - Impact Scalabilité: Latence linéaire en O(N) allers-retours réseau. Saturation rapide des pools de connexions SQL sous trafic.
   - Correction: Effectuer une requête SQL groupée en une seule passe : `WHERE id IN (...)`.

4. 🔴 Ligne 73: Opération Lourde Bloquant le Worker HTTP (`execute_heavy_ocr_processing`)
   - Impact Scalabilité: Bloque le thread de l'API pendant 25 secondes. Saturation immédiate des workers Uvicorn et timeouts 504 Gateway Timeout.
   - Correction: Renvoyer un statut `HTTP 202 Accepted` avec un `job_id` et déporter le travail lourd dans un `BackgroundTasks` ou Celery.

5. 🟠 Ligne 32: Utilisation de `requests.post()` Synchrone
   - Impact Concurrence: Bloque le thread async d'E/S.
   - Correction: Préférer le client HTTP asynchrone `httpx.AsyncClient()`.
"""

import uuid
import logging
import asyncio
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from pydantic import BaseModel, Field
import httpx

app = FastAPI(title="Scale Data Processing API - Refactored")
logger = logging.getLogger("system_design_service")


# ==============================================================================
# SCHÉMAS PYDANTIC (DTOs & Payload Validation)
# ==============================================================================
class BatchProcessPayload(BaseModel):
    document_ids: List[str] = Field(..., min_items=1, description="Liste des IDs de documents à traiter")


class OCRJobResponse(BaseModel):
    job_id: str
    status: str = "accepted"
    message: str = "Traitement OCR en cours d'exécution en arrière-plan"


# ==============================================================================
# REPOSITORY SQL OPTIMISÉ (Élimination des requêtes N+1)
# ==============================================================================
class OptimizedDocumentRepository:
    def __init__(self, db_connection: Any):
        self.db = db_connection

    def fetch_documents_by_ids_batch(self, document_ids: List[str]) -> List[dict]:
        """
        Récupération par Batch : Élimination complète du problème N+1.
        Toutes les lignes sont lues en un seul aller-retour réseau SQL.
        """
        if not document_ids:
            return []

        # Construction sécurisée de la requête SQL IN (...)
        # En production real-world, utiliser un ORM (SQLAlchemy) ou des placeholders typés
        placeholders = ", ".join(["%s"] * len(document_ids))
        query = f"SELECT id, title, content FROM documents WHERE id IN ({placeholders})"
        
        try:
            cursor = self.db.execute(query, tuple(document_ids))
            rows = cursor.fetchall()
            return [{"id": row[0], "title": row[1], "content": row[2]} for row in rows]
        except Exception:
            logger.exception("Erreur lors de la lecture batch en BDD")
            return []


# ==============================================================================
# CLIENT HTTP IDEMPOTENT & ASYNCHRONE
# ==============================================================================
class IdempotentIndexingClient:
    async def sync_to_search_engine_async(self, payload: dict, idempotency_key: str, max_retries: int = 3) -> bool:
        """
        Calcul de Retry Asynchrone avec Clé d'Idempotence obligatoire.
        """
        url = "https://search-engine.internal/api/v1/index"
        headers = {
            "Idempotency-Key": idempotency_key,  # ✅ Contrôle d'idempotence
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            for attempt in range(max_retries):
                try:
                    response = await client.post(url, json=payload, headers=headers)
                    if response.status_code == 200:
                        return True
                    logger.warning(f"Tentative {attempt + 1} échouée (HTTP {response.status_code}). Re-tentative...")
                except httpx.RequestError as e:
                    logger.warning(f"Erreur réseau tentative {attempt + 1}: {e}")
                
                await asyncio.sleep(2 ** attempt)  # ✅ Exponential backoff
                
        return False


# ==============================================================================
# WORKER EN ARRIÈRE-PLAN (Slow Execution Path)
# ==============================================================================
async def execute_heavy_ocr_background_job(job_id: str, file_bytes: bytes):
    """
    Traitement lourd (Slow Path) déporté hors de la boucle HTTP.
    """
    logger.info(f"[JOB_ID: {job_id}] Démarrage du traitement OCR lourd...")
    await asyncio.sleep(25)  # Simulation du calcul CPU/OCR
    logger.info(f"[JOB_ID: {job_id}] Traitement OCR terminé avec succès.")
    # Sauvegarde des résultats en BDD / S3


repo = OptimizedDocumentRepository(db_connection=None)
indexing_client = IdempotentIndexingClient()


# ==============================================================================
# ENDPOINTS FASTAPI STRUCTURÉS
# ==============================================================================
@app.post("/batch_process", status_code=200)
async def batch_process_endpoint(payload: BatchProcessPayload):
    # 1. Validation de l'entrée garantie par Pydantic (si document_ids est vide, FastAPI renvoie HTTP 422)
    
    # 2. Récupération BDD optimisée en 1 seule passe SQL (Pas de N+1)
    docs = repo.fetch_documents_by_ids_batch(payload.document_ids)
    
    # 3. Génération d'une clé d'idempotence unique pour ce traitement
    idempotency_key = str(uuid.uuid4())
    
    # 4. Synchronisation HTTP async avec Retry et Idempotence
    success = await indexing_client.sync_to_search_engine_async(
        payload={"count": len(docs)},
        idempotency_key=idempotency_key
    )
    
    if not success:
        # ✅ Notification d'erreur HTTP 502 Bad Gateway appropriée
        raise HTTPException(status_code=502, detail="Échec de l'indexation externe après plusieurs tentatives")
        
    return {"status": "success", "processed_count": len(docs)}


@app.post("/process_ocr_pdf", status_code=202, response_model=OCRJobResponse)
async def process_ocr_pdf_endpoint(background_tasks: BackgroundTasks):
    """
    Séparation Fast vs Slow Paths : 
    Renvoyer HTTP 202 Accepted immédiatement (<5ms) et traiter le fichier en tâche de fond.
    """
    job_id = str(uuid.uuid4())
    file_bytes = b"PDF_CONTENT"
    
    # ✅ Déport de la tâche lourde en arrière-plan
    background_tasks.add_task(execute_heavy_ocr_background_job, job_id, file_bytes)
    
    # ✅ Réponse instantanée au client avec le job_id pour polling/webhook
    return OCRJobResponse(job_id=job_id)
