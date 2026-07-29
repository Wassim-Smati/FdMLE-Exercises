"""
Exercice 4 : Pipeline RAG End-to-End (Intégration Complète)

Contexte Entretien :
Il s'agit du test d'intégration classique où l'on vous demande d'assembler la chaîne RAG complète :
Document -> Chunking -> Vector Store -> Retrieval -> Construction de Prompt avec Citations -> LLM.

Consignes :
1. Implémenter la fonction `build_rag_prompt(query: str, retrieved_chunks: List[Dict[str, Any]]) -> str` :
   - Formater les chunks avec leurs citations sous la forme : `[doc:ID chunk:INDEX] texte...`
   - Construire le prompt final intégrant les instructions du système et le contexte.

2. Implémenter la fonction `run_rag_pipeline` :
   - Prendre une liste de documents textes d'entrée.
   - Découper, vectoriser, stocker, rechercher les top_k et générer la réponse via un LLM fictif/mock.
"""

from typing import List, Dict, Any, Callable


def build_rag_prompt(query: str, retrieved_chunks: List[Dict[str, Any]]) -> str:
    """Construit un prompt RAG structuré avec citations obligatoires.

    Args:
        query: Question de l'utilisateur.
        retrieved_chunks: Chunks récupérés par le VectorStore.

    Returns:
        Prompt sous forme de chaîne de caractères formatée.
    """
    pass


def run_rag_pipeline(
    query: str,
    documents: List[Dict[str, Any]],
    embed_fn: Callable[[str], List[float]],
    llm_fn: Callable[[str], str],
    top_k: int = 2
) -> Dict[str, Any]:
    """Exécute le pipeline RAG complet de bout en bout.

    Args:
        query: Question posée par l'utilisateur.
        documents: Liste de dictionnaires d'entrée `[{"doc_id": "1", "content": "text..."}, ...]`.
        embed_fn: Fonction qui prend un texte et retourne un vecteur float.
        llm_fn: Fonction qui prend un prompt et retourne la réponse générée.
        top_k: Nombre de chunks à inclure dans le contexte.

    Returns:
        Dictionnaire au format :
        {
            "query": str,
            "answer": str,
            "sources": List[str]  # Identifiants des chunks utilisés
        }
    """
    pass


if __name__ == "__main__":
    print("Exercice C.4 chargé. Complétez les fonctions du pipeline RAG end-to-end.")
