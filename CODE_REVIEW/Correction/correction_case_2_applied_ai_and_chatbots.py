"""
================================================================================
CORRECTION OFFICIELLE — CAS DE CODE REVIEW #2
Secteur: Applied AI, Agentic Workflows & Enterprise Chatbots (Mistral FDE)
================================================================================

LISTE DES FAILLES IDENTIFIÉES & IMPACTS :

1. 🔴 Ligne 14: Clé API Mistral Hardcodée dans le code source (`MISTRAL_API_KEY = "sk-..."`)
   - Impact Sécurité: Fuite de crédentials sur les dépôts Git.
   - Correction: Utiliser `os.getenv("MISTRAL_API_KEY")` ou `pydantic-settings`.

2. 🟠 Ligne 40: Absence de Router de Modèles (Over-provisioning)
   - Impact Coût & Latence: Utiliser `mistral-large-latest` pour de la simple classification d'intention. Coûts API 10x plus élevés.
   - Correction: Router la classification vers `mistral-small-latest`.

3. 🟠 Ligne 38: Formattage JSON de prompt fait à la main via f-string (`f'{{"query": "{user_query}"}}'`)
   - Impact Scalabilité: Faille de sérialisation dès que `user_query` contient des guillemets `"` ou retours `\n`.
   - Correction: Utiliser `json.dumps({"query": user_query})`.

4. 🔴 Ligne 47: Fuite de Données Inter-Locataires (Cross-Tenant Data Leakage dans le Vector Store)
   - Impact Sécurité Multi-Tenant: La recherche vectorielle s'effectue sans filtrer par `tenant_id`. Les données d'un client fuitent vers un autre.
   - Correction: `vector_store.search(query=query, filter={"tenant_id": tenant_id}, top_k=5)`

5. 🔴 Ligne 53: Effacement du System Prompt lors du Slicing de Mémoire (`messages[-max_size:]`)
   - Impact Agent: La tranche `-max_size` supprime le message `system` situé à l'index `0`. L'agent perd ses consignes et guardrails.
   - Correction: Isoler `system_prompt = messages[0]` et slicer uniquement `messages[1:]`.

6. 🔴 Ligne 72: Accès Direct aux Tool Calls sans Vérification `None`
   - Impact Exécution: Lève `TypeError` / `AttributeError` si le LLM répond avec un message texte sans appel d'outil.
   - Correction: Vérifier `if message_obj.tool_calls:` avant d'accéder à l'index `[0]`.

7. 🔴 Ligne 25: Exécution d'Outils avec Arguments Non Validés (`execute_sql_query(**args)`)
   - Impact Sécurité: Exécution d'arguments brut du LLM sans validation Pydantic. Faille d'injection de code.
   - Correction: Valider avec un modèle Pydantic `SQLQuerySchema.model_validate(args)`.

8. 🏗️ Instance d'Agent Globale Partagée (`chatbot = EnterpriseChatbotAgent(...)`)
   - Impact Structure: Fait mélanger les historiques de chat entre différents utilisateurs.
   - Correction: Gérer l'état par ID de session dans un store externe (Redis/BDD) ou instancier par requête.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

app = FastAPI(title="Enterprise Agentic Chatbot API - Refactored")
logger = logging.getLogger("chatbot_service")

# Charger la clé API depuis l'environnement
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")


# ==============================================================================
# SCHÉMAS PYDANTIC POUR LE FUNCTION CALLING (Tool Args Validation)
# ==============================================================================
class SQLQuerySchema(BaseModel):
    query: str = Field(..., description="Requête SQL à exécuter")
    database_name: str = Field(default="default_db", description="Nom de la base de données")


class ChatRequestPayload(BaseModel):
    query: str = Field(..., description="Message de l'utilisateur")
    tenant_id: str = Field(..., description="Identifiant unique du locataire enterprise")
    session_id: str = Field(..., description="Identifiant de la session de chat")


# ==============================================================================
# SERVICE D'EXÉCUTION D'OUTILS SÉCURISÉ
# ==============================================================================
class ValidatedToolExecutionService:
    @staticmethod
    def execute_sql_query(validated_args: SQLQuerySchema) -> dict:
        logger.info(f"Exécution SQL sécurisée sur BDD {validated_args.database_name}: {validated_args.query}")
        return {"status": "success", "rows": [["order_123", "shipped"]]}

    def dispatch_tool(self, tool_name: str, args_json_str: str) -> dict:
        try:
            raw_args = json.loads(args_json_str)
            if tool_name == "execute_sql_query":
                # Validation Pydantic stricte avant exécution
                validated_args = SQLQuerySchema.model_validate(raw_args)
                return self.execute_sql_query(validated_args)
            return {"error": f"Outil inconnu: {tool_name}"}
        except Exception as e:
            logger.exception(f"Erreur de validation/exécution de l'outil {tool_name}")
            return {"error": "Échec de validation des arguments de l'outil"}


# ==============================================================================
# AGENT CHATBOT AVEC MODEL ROUTER ET ISOLATION MULTI-TENANT
# ==============================================================================
class EnterpriseChatbotAgent:
    def __init__(self, vector_store_client: Any, mistral_client: Any):
        self.vector_store = vector_store_client
        self.mistral_client = mistral_client
        self.tool_service = ValidatedToolExecutionService()

    def classify_user_intent(self, user_query: str) -> str:
        """Routeur de Modèle : Utilise mistral-small pour les tâches simples de classification."""
        payload_json = json.dumps({"task": "classify_intent", "query": user_query})
        response = self.mistral_client.chat.complete(
            model="mistral-small-latest",  # ✅ Mistral Small pour le routage rapide et économique
            messages=[{"role": "user", "content": payload_json}]
        )
        return response.choices[0].message.content

    def retrieve_context_documents(self, query: str, tenant_id: str) -> List[str]:
        """Isolation Multi-Tenant : Filtre obligatoire par tenant_id."""
        results = self.vector_store.search(
            query=query,
            filter={"tenant_id": tenant_id},  # ✅ Isolation stricte multi-tenant
            top_k=5
        )
        return [doc.text for doc in results]

    def slice_memory_preserving_system_prompt(self, history: List[Dict[str, str]], max_history_size: int = 6) -> List[Dict[str, str]]:
        """Fenêtrage glissant avec préservation systématique du System Prompt (index 0)."""
        if len(history) <= max_history_size:
            return history
            
        system_prompt = history[0]  # ✅ Isoler le System Prompt à l'index 0
        recent_history = history[1:][-(max_history_size - 1):]
        return [system_prompt] + recent_history

    def handle_user_message(self, user_query: str, tenant_id: str, chat_history: List[Dict[str, str]]) -> Tuple[str, List[Dict[str, str]]]:
        # 1. Intent Routing (Mistral Small)
        intent = self.classify_user_intent(user_query)
        
        # 2. Context Retrieval avec filtre tenant_id
        context_docs = self.retrieve_context_documents(user_query, tenant_id)
        context_str = "\n".join(context_docs)
        
        # 3. Prompt Construction
        full_user_input = f"Contexte ({tenant_id}):\n{context_str}\n\nQuestion:\n{user_query}"
        updated_history = list(chat_history)
        updated_history.append({"role": "user", "content": full_user_input})
        
        # 4. Slicing Mémoire sécurisé
        sliced_history = self.slice_memory_preserving_system_prompt(updated_history, max_history_size=6)
        
        # 5. Inférence (Mistral Large pour le raisonnement complexe)
        response = self.mistral_client.chat.complete(
            model="mistral-large-latest",
            messages=sliced_history
        )
        
        message_obj = response.choices[0].message
        
        # 6. Traitement sécurisé des Tool Calls
        if hasattr(message_obj, "tool_calls") and message_obj.tool_calls:  # ✅ Vérification de présence
            tool_call = message_obj.tool_calls[0]
            tool_name = tool_call.function.name
            tool_args = tool_call.function.arguments
            
            tool_result = self.tool_service.dispatch_tool(tool_name, tool_args)
            assistant_reply = f"Résultat outil: {json.dumps(tool_result)}"
        else:
            assistant_reply = message_obj.content
            
        sliced_history.append({"role": "assistant", "content": assistant_reply})
        return assistant_reply, sliced_history


# ==============================================================================
# ENDPOINT FASTAPI
# ==============================================================================
@app.post("/chat")
async def chat_endpoint(payload: ChatRequestPayload):
    if not MISTRAL_API_KEY:
        raise HTTPException(status_code=500, detail="MISTRAL_API_KEY manquante dans l'environnement")

    # Initialisation de l'agent par requête (ou injection de dépendances)
    chatbot = EnterpriseChatbotAgent(vector_store_client=None, mistral_client=None)
    
    # Historique de conversation exemple
    initial_history = [
        {"role": "system", "content": "Tu es un assistant support client strictement professionnel."}
    ]
    
    reply, updated_history = chatbot.handle_user_message(
        user_query=payload.query,
        tenant_id=payload.tenant_id,
        chat_history=initial_history
    )
    
    return {"reply": reply, "session_id": payload.session_id}
