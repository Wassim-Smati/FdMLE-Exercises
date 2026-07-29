"""
Exercice 2 : Métriques de Similarité (Cosine, L2, TF-IDF)

Contexte Entretien :
Pour comparer un vecteur de requête avec des vecteurs de documents (embeddings denses) 
ou pour mesurer la pertinence textuelle (sparse TF-IDF), vous devez connaître les formules mathématiques 
et savoir les implémenter en Python / NumPy / PyTorch.

Formules :
- Cosine Similarity : dot(u, v) / (||u||_2 * ||v||_2)  (résultat entre -1 et 1, 1 = identique)
- Distance L2 (Euclidienne) : sqrt( sum( (u_i - v_i)^2 ) )  (0 = identique)
"""

import math
from typing import List, Dict, Tuple


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calcule la similarité cosinus entre deux vecteurs denses v1 et v2.

    Args:
        v1: Premier vecteur (liste de floats).
        v2: Second vecteur (liste de floats de même dimension).

    Returns:
        Valeur float de similarité cosinus entre -1.0 et 1.0 (ou 0.0 si norme nulle).

    Raises:
        ValueError: Si les dimensions des deux vecteurs ne correspondent pas.
    """
    pass


def l2_distance(v1: List[float], v2: List[float]) -> float:
    """Calcule la distance euclidienne (L2) entre deux vecteurs v1 et v2.

    Args:
        v1: Premier vecteur.
        v2: Second vecteur.

    Returns:
        Distance L2 >= 0.0.
    """
    pass


def compute_tfidf_scores(query: str, documents: List[str]) -> List[Tuple[int, float]]:
    """Calcule le score de pertinence TF-IDF simple entre la requête et une liste de documents.

    TF(t, d) = nombre d'occurrences du mot t dans d / nombre total de mots dans d
    IDF(t) = log( (1 + N) / (1 + df(t)) ) + 1

    Args:
        query: Chaîne de caractères de recherche.
        documents: Liste des textes de documents.

    Returns:
        Liste de tuples (index_doc, score_tfidf) triée par score décroissant.
    """
    pass


if __name__ == "__main__":
    print("Exercice C.2 chargé. Complétez les fonctions de métriques de similarité.")
