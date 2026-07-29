"""
Cas de Code Review #2 — Microservice Chatbot Enterprise & Agent Workflow (Mistral API)
Société: Enterprise AI Customer Support
Fichier à reviewer par le candidat en vue du call Mistral AI.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI(title="Enterprise Agentic Chatbot API")
logger = logging.getLogger("chatbot_service")

# Configuration du client Mistral
MISTRAL_API_KEY = "sk-mistral-live-prod-secret-998877"
DEFAULT_MODEL = "mistral-large-latest"


class ToolExecutionService:
    def execute_sql_query(self, query: str, database_name: str) -> dict:
        # Simulation d'exécution SQL
        return {"status": "success", "rows": [["order_123", "shipped"]]}

    def dispatch_tool(self, tool_name: str, args_json_str: str) -> dict:
        # Exécution dynamique d'outil basée sur le JSON généré par le LLM
        args = json.loads(args_json_str)
        if tool_name == "execute_sql_query":
            return self.execute_sql_query(**args)
        return {"error": "Unknown tool"}


class EnterpriseChatbotAgent:
    def __init__(self, vector_store_client: Any, mistral_client: Any):
        self.vector_store = vector_store_client
        self.mistral_client = mistral_client
        self.tool_service = ToolExecutionService()
        self.chat_history: List[Dict[str, str]] = [
            {"role": "system", "content": "Tu es un assistant support client strictement professionnel pour Enterprise SaaS."}
        ]

    def classify_user_intent(self, user_query: str) -> str:
        # Classification d'intention (tâche simple de routage)
        prompt = f'{{"task": "classify", "query": "{user_query}"}}'
        response = self.mistral_client.chat.complete(
            model="mistral-large-latest",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def retrieve_context_documents(self, query: str, tenant_id: str) -> List[str]:
        # Recherche vectorielle RAG dans la base de connaissance
        results = self.vector_store.search(query=query, top_k=5)
        return [doc.text for doc in results]

    def truncate_memory_sliding_window(self, max_history_size: int = 6):
        # Limiter la taille de l'historique pour éviter le Context Overflow
        if len(self.chat_history) > max_history_size:
            self.chat_history = self.chat_history[-max_history_size:]

    def handle_user_message(self, user_query: str, tenant_id: str) -> str:
        # 1. Classification de la requête
        intent = self.classify_user_intent(user_query)
        
        # 2. Ingestion du contexte RAG
        context_docs = self.retrieve_context_documents(user_query, tenant_id)
        context_str = "\n".join(context_docs)
        
        # 3. Construction du prompt utilisateur
        full_user_input = f"Contexte:\n{context_str}\n\nQuestion utilisateur:\n{user_query}"
        self.chat_history.append({"role": "user", "content": full_user_input})
        
        # 4. Fenêtrage glissant de la mémoire
        self.truncate_memory_sliding_window(max_history_size=6)
        
        # 5. Appel de l'API Mistral
        response = self.mistral_client.chat.complete(
            model=DEFAULT_MODEL,
            messages=self.chat_history
        )
        
        message_obj = response.choices[0].message
        
        # 6. Exécution des Tool Calls
        tool_call = message_obj.tool_calls[0]
        tool_name = tool_call.function.name
        tool_args = tool_call.function.arguments
        
        tool_result = self.tool_service.dispatch_tool(tool_name, tool_args)
        
        assistant_reply = f"Résultat outil: {json.dumps(tool_result)}"
        self.chat_history.append({"role": "assistant", "content": assistant_reply})
        
        return assistant_reply


@app.post("/chat")
async def chat_endpoint(request: Request):
    payload = await request.json()
    user_query = payload.get("query")
    tenant_id = payload.get("tenant_id")
    
    chatbot = EnterpriseChatbotAgent(vector_store_client=None, mistral_client=None)
    reply = chatbot.handle_user_message(user_query, tenant_id)
    
    return {"reply": reply}
