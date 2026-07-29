"""
================================================================================
CORRECTION OFFICIELLE — CAS DE CODE REVIEW #1
Secteur: Python Async, Mémoire, Scope & Architecture Logicielle
================================================================================

LISTE DES FAILLES IDENTIFIÉES & IMPACTS :

1. 🔴 Ligne 48: Oubli du mot-clé `await` sur `self.fetch_user_profile_async(user_id)`
   - Impact Bug: `user_profile` contient un objet <coroutine> non exécuté. Ligne 51 plante avec TypeError.
   - Impact Scalabilité & Structure: Rupture de la chaîne async et blocage du contrat de données.
   - Correction: `user_profile = await self.fetch_user_profile_async(user_id)`

2. 🔴 Ligne 79: Appel à `asyncio.run()` dans un handler FastAPI (`ingested_document_endpoint`)
   - Impact Scalabilité: Lève `RuntimeError: Cannot call asyncio.run() from a running event loop`. Crashe les workers Web Uvicorn sous charge.
   - Correction: Remplacer par `await ingestion_service.process_document(user_id, file_path)`

3. 🔴 Ligne 35 & 45: Arguments par défaut mutables (`tags: list = []`, `extra_info: dict = {}`)
   - Impact Structure & Mémoire: La même liste est instanciée une seule fois et réutilisée/polluée entre toutes les requêtes utilisateurs concurrentes.
   - Correction: `tags: Optional[List[str]] = None` et initialisation dynamique `if tags is None: tags = []`

4. 🟠 Ligne 30: Fuite de ressource fichier (`f = open(...)` sans context manager)
   - Impact Scalabilité: Si `json.loads` échoue, le fichier reste ouvert. Entraîne l'erreur OS `Too many open files`.
   - Correction: Utiliser `with open(file_path, "r", encoding="utf-8") as f:`

5. 🟠 Ligne 33: Accès direct non sécurisé `parsed["data"]["text"]`
   - Impact Structure: Clé absente lève `KeyError` non géré.
   - Correction: Utiliser Pydantic pour valider le schéma JSON d'entrée.

6. 🔴 Ligne 64-66: Exception ravalée silencieusement (`try ... except Exception: pass`)
   - Impact Scalabilité: Masque les crashs et rend le monitoring de latence p99 et d'erreurs impossible.
   - Correction: Logger l'exception avec `logger.exception()` et relancer `HTTPException`.

7. 🏗️ God Class & Couplage Fort (`DocumentIngestionGodService`)
   - Impact Structure: Viol du Single Responsibility Principle (SRP).
   - Correction: Découpler en services autonomes (Reader, Formatter, IngestionService).
"""

import json
import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

app = FastAPI(title="Document Ingestion API - Refactored")
logger = logging.getLogger("ingestion_service")


# ==============================================================================
# SCHÉMAS PYDANTIC (DTO - Data Transfer Objects)
# ==============================================================================
class DocumentPayload(BaseModel):
    user_id: str = Field(..., description="ID de l'utilisateur")
    file_path: str = Field(..., description="Chemin du fichier à ingérer")
    tags: Optional[List[str]] = Field(default=None, description="Tags optionnels")


class DocumentContent(BaseModel):
    text: str


class DocumentRootSchema(BaseModel):
    data: DocumentContent


# ==============================================================================
# SERVICES DÉCOUPÉS (Single Responsibility Principle)
# ==============================================================================
class DocumentFileReader:
    """Responsable uniquement de la lecture sécurisée de fichiers."""
    
    @staticmethod
    def read_and_parse_json(file_path: str) -> str:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                raw_json = json.loads(content)
                validated = DocumentRootSchema.model_validate(raw_json)
                return validated.data.text
        except FileNotFoundError:
            logger.error(f"Fichier introuvable: {file_path}")
            raise HTTPException(status_code=404, detail="Fichier introuvable")
        except Exception as e:
            logger.exception(f"Erreur de lecture/parsing du fichier {file_path}")
            raise HTTPException(status_code=400, detail="Format de document invalide")


class MetadataFormatter:
    """Responsable du formattage pur des métadonnées (stateless)."""
    
    @staticmethod
    def build_chunk_metadata(text: str, tags: Optional[List[str]] = None, extra_info: Optional[Dict[str, Any]] = None) -> dict:
        # Initialisation sécurisée pour éviter les arguments mutables
        effective_tags = list(tags) if tags else []
        effective_extra = dict(extra_info) if extra_info else {}
        
        effective_tags.append("processed")
        effective_extra["char_count"] = len(text)
        
        return {
            "text_snippet": text[:100],
            "tags": effective_tags,
            "extra": effective_extra
        }


class UserProfileClient:
    """Responsable de l'interaction avec le service profil utilisateur."""
    
    @staticmethod
    async def fetch_user_profile_async(user_id: str) -> Dict[str, Any]:
        # Simulation d'un appel DB / microservice externe
        import asyncio
        await asyncio.sleep(0.1)
        return {"user_id": user_id, "tier": "enterprise", "quota_remaining": 500}


class IngestionService:
    """Orchestrateur principal de l'ingestion."""
    
    def __init__(self, reader: DocumentFileReader, formatter: MetadataFormatter, profile_client: UserProfileClient):
        self.reader = reader
        self.formatter = formatter
        self.profile_client = profile_client

    async def process_document(self, user_id: str, file_path: str, tags_list: Optional[List[str]] = None) -> Dict[str, Any]:
        try:
            # 1. Récupération async avec AWAIT
            user_profile = await self.profile_client.fetch_user_profile_async(user_id)
            
            tier_name = user_profile.get("tier", "standard")
            logger.info(f"Traitement du document pour l'utilisateur {user_id} (tier: {tier_name})")
            
            # 2. Extraction sécurisée via Context Manager
            raw_text = self.reader.read_and_parse_json(file_path)
            
            # 3. Formattage de métadonnées sans mutabilité partagée
            metadata = self.formatter.build_chunk_metadata(raw_text, tags=tags_list)
            
            return {
                "status": "success",
                "user_tier": tier_name,
                "metadata": metadata
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Erreur inattendue lors de l'ingestion du document {file_path}")
            raise HTTPException(status_code=500, detail="Échec du traitement du document")


# Instanciation par Injection de Dépendances
file_reader = DocumentFileReader()
metadata_formatter = MetadataFormatter()
profile_client = UserProfileClient()
ingestion_service = IngestionService(reader=file_reader, formatter=metadata_formatter, profile_client=profile_client)


# ==============================================================================
# ENDPOINT FASTAPI NETTOYÉ
# ==============================================================================
@app.post("/ingest", status_code=200)
async def ingest_document_endpoint(payload: DocumentPayload):
    """
    Endpoint d'ingestion. 
    L'Event Loop FastAPI est préservée grâce au AWAIT direct (pas de asyncio.run).
    """
    result = await ingestion_service.process_document(
        user_id=payload.user_id,
        file_path=payload.file_path,
        tags_list=payload.tags
    )
    return {"status": "ok", "result": result}
