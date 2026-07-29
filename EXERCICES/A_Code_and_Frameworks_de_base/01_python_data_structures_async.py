"""
Exercice 1 : Manipulation de structures de données & Async en Python

Contexte Entretien :
Dans un système AI/RAG, on reçoit souvent des flux de données brutes (métadonnées de documents, logs, résultats de requêtes) 
qu'il faut filtrer, grouper et traiter de manière asynchrone pour ne pas bloquer les I/O (appels API LLM, lectures DB).

Consignes :
1. Implémenter `process_document_batches` :
   - Prendre une liste de dictionnaires représentant des métadonnées de documents.
   - Filtrer les documents invalides (ex: sans contenu ou avec statut != 'ready').
   - Grouper les documents par `tenant_id`.
   - Trier les documents de chaque tenant par score de priorité décroissant.

2. Implémenter `async_fetch_embeddings` :
   - Simuler un traitement asynchrone (ex: requêtes réseau parallèles vers une API d'embedding).
   - Prendre une liste de textes et retourner un dictionnaire mappant chaque texte à son embedding (simulé sous forme de liste de float).
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple


def process_document_batches(documents: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Filtre, groupe par tenant_id et trie les documents par score de priorité décroissant.

    Args:
        documents: Liste de dicts contenant au minimum :
            - 'id': str
            - 'tenant_id': str
            - 'status': str (ex: 'ready', 'pending', 'error')
            - 'content': str
            - 'priority_score': float

    Returns:
        Dict dont la clé est le 'tenant_id' et la valeur est la liste des documents valides 
        (status == 'ready' et content non vide), triés par priority_score décroissant.
    """
    pass


async def async_fetch_embeddings(texts: List[str], embedding_dim: int = 128) -> Dict[str, List[float]]:
    """Simule la récupération asynchrone d'embeddings pour une liste de textes.

    Chaque texte doit être traité de façon asynchrone (ex: avec asyncio.gather ou asyncio.sleep).

    Args:
        texts: Liste des chaînes de caractères à vectoriser.
        embedding_dim: Dimension du vecteur d'embedding produit.

    Returns:
        Dictionnaire {texte: liste_de_floats_de_taille_embedding_dim}.
    """
    pass


if __name__ == "__main__":
    # Zone de test local (vous pourrez exécuter ce script une fois complété)
    print("Exercice 1 chargé. Complétez les fonctions ci-dessus.")
