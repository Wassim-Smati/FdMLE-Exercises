"""
Exercice 3 : API REST avec FastAPI & Validation Pydantic

Contexte Entretien :
En tant que Forward Deployed ML Engineer, vous devez souvent exposer vos modèles ou pipelines RAG 
via des endpoints API propres, robustes et documentés pour l'équipe Frontend ou les systèmes clients.

Consignes :
1. Définir les modèles Pydantic de requête (`RagQueryRequest`) et de réponse (`RagQueryResponse`).
   - `RagQueryRequest` :
     - `query` : str (longueur min: 3, max: 1000)
     - `tenant_id` : str (non vide)
     - `top_k` : int (valeur entre 1 et 20, défaut 5)
     - `include_metadata` : bool (défaut True)
   - `RagQueryResponse` :
     - `answer` : str
     - `sources` : List[dict] (contient doc_id, score, preview)
     - `latency_ms` : float

2. Créer l'application FastAPI `app` et implémenter l'endpoint `POST /v1/rag/answer` :
   - Valider la requête via Pydantic.
   - Si la requête contient une query contenant 'error', lever une HTTPException(status_code=400).
   - Retourner une réponse mockée conforme au schéma `RagQueryResponse`.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any


# --- 1. Schémas Pydantic ---

class RagQueryRequest(BaseModel):
    """Schéma de validation pour la requête d'interrogation RAG."""
    # TODO: Définir les champs avec Field(...) et validations
    pass


class RagQueryResponse(BaseModel):
    """Schéma de réponse structurée d'interrogation RAG."""
    # TODO: Définir les champs de réponse
    pass


# --- 2. Application FastAPI ---

app = FastAPI(title="Mistral FDE RAG API", version="1.0.0")


@app.post("/v1/rag/answer", response_model=RagQueryResponse)
async def answer_rag_query(request: RagQueryRequest) -> RagQueryResponse:
    """Endpoint REST traitant une question RAG et retournant la réponse avec sources.

    Raises:
        HTTPException: Si la requête échoue la validation métier (ex: query interdite).
    """
    pass


if __name__ == "__main__":
    print("Exercice 3 chargé. Complétez les modèles Pydantic et l'endpoint FastAPI.")
