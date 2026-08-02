"""
Cas de Code Review #2 — Microservice Chatbot Enterprise & Agent Workflow (Mistral API)
Société: Enterprise AI Customer Support
Fichier à reviewer par le candidat en vue du call Mistral AI.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI(title="Enterprise Agentic Chatbot API")
logger = logging.getLogger("chatbot_service")

# Configuration du client Mistral
MISTRAL_API_KEY = os.environ['MISTRAL_KEY']

def truncate_memory_sliding_window(chat_history, max_history_size: int = 6):
    system_prompt = chat_history[0]
    user_history = chat_history[1:]
    # Limiter la taille de l'historique pour éviter le Context Overflow
    if len(user_history) > max_history_size:
        user_history = user_history[-max_history_size:]
    
    return [system_prompt] + user_history

class ValidToolArgument(BaseModel): 
    query: str 
    database_name: str

class ToolExecutionService:
    async def execute_sql_query(self, query: str, database_name: str) -> dict:
        # Simulation d'exécution SQL
        await asyncio.sleep(0.1)
        return {"status": "success", "rows": [["order_123", "shipped"]]}

    async def dispatch_tool(self, tool_name: str, args_json_str: str) -> dict:
        # Exécution dynamique d'outil basée sur le JSON généré par le LLM
        try:
            args = ValidToolArgument.model_validate_json(args_json_str)

            if tool_name == "execute_sql_query":
                return await self.execute_sql_query(args.query, args.database_name)
            else: 
                return {"error": f"Outil inconnu : {tool_name}"}

        except (ValidationError) as e: 
            logger.warning(f"Validation d'arguments échouée : {e}") 
        
            return {"error": "Arguments d'outils invalides"}

class RagKnowledgeService: 
    def __init__(self, vector_store_client: Any): 
        self.vector_store = vector_store_client

    async def retrieve_context_documents(self, query: str, tenant_id: str) -> List[str]:
        # Recherche vectorielle RAG dans la base de connaissance
        try: 
            results = await self.vector_store.search(query=query, top_k=5, tenant_id=tenant_id)
            return [doc.text for doc in results]
        
        except Exception as e: 
            logger.warning(f"Fetch de documents échoué")
            return []

class EnterpriseChatbotAgent:
    def __init__(self, mistral_client: Any, rag_service: RagKnowledgeService, tool_service: ToolExecutionService):
        self.rag_service = rag_service
        self.mistral_client = mistral_client
        self.tool_service = tool_service

    async def handle_user_message(self, user_query: str, tenant_id: str, chat_history: List[Dict[str, str]], model_name: str) -> str:
        
        # 2. Ingestion du contexte RAG
        context_docs = await self.rag_service.retrieve_context_documents(user_query, tenant_id)
        context_str = "\n".join(context_docs)
        
        # 3. Construction du prompt utilisateur
        full_user_input = f"Contexte:\n{context_str}\n\nQuestion utilisateur:\n{user_query}"
        chat_history.append({"role": "user", "content": full_user_input})
        
        # 4. Fenêtrage glissant de la mémoire
        chat_history = truncate_memory_sliding_window(chat_history, max_history_size=6)
        
        # 5. Appel de l'API Mistral
        response = self.mistral_client.chat.complete(
            model=model_name,
            messages=chat_history
        )
        
        message_obj = response.choices[0].message
        
        # 6. Exécution des Tool Calls
        if message_obj.tool_calls:
            tool_call = message_obj.tool_calls[0]
            tool_name = tool_call.function.name
            tool_args = tool_call.function.arguments
        
            tool_result = await self.tool_service.dispatch_tool(tool_name, tool_args)
        else: 
            tool_result = ""
        
        assistant_reply = f"Résultat outil: {json.dumps(tool_result)}"
        chat_history.append({"role": "assistant", "content": assistant_reply})
        
        return assistant_reply

class ValidRequest(BaseModel): 
    user_query: str
    tenant_id: int
    chat_history: List[Dict[str,str]]

@app.post("/chat")
async def chat_endpoint(request: ValidRequest):
    user_query = request.query
    tenant_id = request.tenant_id
    chat_history = request.chat_history
    
    chatbot = EnterpriseChatbotAgent(vector_store_client=None, mistral_client=None)
    reply = await chatbot.handle_user_message(user_query, tenant_id, chat_history, model_name="mistral-large-latest")
    
    return {"reply": reply}
