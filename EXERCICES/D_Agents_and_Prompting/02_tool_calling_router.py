"""
Exercice 2 : Routeur d'Appel d'Outils (Tool Calling & Guardrails)

Contexte Entretien :
Dans un système d'Agent IA, le LLM ne répond pas toujours directement avec du texte : 
il peut décider d'appeler des fonctions (outils/API). 
Votre rôle d'ingénieur est de parser la demande du LLM, de vérifier les garde-fous de sécurité (guardrails) 
en code Python déterministe, puis d'exécuter l'outil approprié.

Consignes :
1. Implémenter `validate_and_execute_tool_call` :
   - Analyser le dictionnaire `tool_call` produit par le LLM `{"name": "create_refund", "arguments": {...}}`.
   - Appliquer un garde-fou déterministe : Si `name == "create_refund"` et `amount > 100.0`, rejeter l'action avec une exception/erreur de garde-fou.
   - Si valide, exécuter la fonction Python correspondante et retourner le résultat.
"""

from typing import Dict, Any, Callable


# --- Outils Fictifs (Functions) ---

def search_tickets(query: str, status: str = "open") -> Dict[str, Any]:
    """Recherche des tickets de support."""
    return {"status": "success", "found_tickets": [{"id": "TK-101", "query": query, "status": status}]}


def create_refund(ticket_id: str, amount: float, reason: str) -> Dict[str, Any]:
    """Effectue un remboursement pour un client."""
    return {"status": "success", "refund_id": "RF-999", "ticket_id": ticket_id, "amount": amount}


# Registre des outils autorisés
TOOL_REGISTRY: Dict[str, Callable] = {
    "search_tickets": search_tickets,
    "create_refund": create_refund,
}


def validate_and_execute_tool_call(
    tool_call: Dict[str, Any],
    max_refund_limit: float = 100.0
) -> Dict[str, Any]:
    """Valide les arguments d'un appel d'outil LLM via des guardrails déterministes et l'exécute.

    Args:
        tool_call: Dict au format `{"name": str, "arguments": Dict[str, Any]}`.
        max_refund_limit: Seuil maximal autorisé pour un remboursement automatique (défaut: 100.0).

    Returns:
        Dict contenant le résultat de l'exécution ou un rapport de rejet de garde-fou :
        `{"status": "error", "reason": "Guardrail violation: Refund amount exceeds limit"}`

    Raises:
        ValueError: Si le nom de l'outil est inconnu dans TOOL_REGISTRY.
    """
    pass


if __name__ == "__main__":
    print("Exercice D.2 chargé. Complétez la fonction validate_and_execute_tool_call.")
