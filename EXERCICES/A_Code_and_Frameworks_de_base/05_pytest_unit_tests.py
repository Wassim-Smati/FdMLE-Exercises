"""
Exercice 5 : Tests Unitaires avec Pytest

Contexte Entretien :
Pendant l'épreuve de Live Coding ou de Pair Programming, montrer que vous savez écrire des tests 
unitaires rapides pour vérifier vos algorithmes est une preuve de maturité d'ingénierie essentielle.

Fonction sous test :
Nous fournissons ci-dessous une fonction simple `clean_and_chunk_text` qui nettoie un texte et le découpe en chunks.

Consignes :
1. Compléter les fonctions de test unitaires `test_clean_and_chunk_normal()`, `test_clean_and_chunk_empty_input()` 
   et `test_clean_and_chunk_invalid_params()` avec `pytest.raises`.
"""

import pytest
from typing import List


# --- Fonction à tester ---

def clean_and_chunk_text(text: str, chunk_size: int = 10, overlap: int = 2) -> List[str]:
    """Nettoie les espaces multiples d'un texte et le découpe en mots par chunks avec chevauchement.

    Args:
        text: Texte d'entrée.
        chunk_size: Nombre de mots par chunk (> 0).
        overlap: Nombre de mots en chevauchement (0 <= overlap < chunk_size).

    Returns:
        Liste de chaînes de caractères (les chunks).

    Raises:
        ValueError: Si chunk_size <= 0 ou overlap >= chunk_size.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size doit être strictement positif")
    if overlap >= chunk_size or overlap < 0:
        raise ValueError("overlap doit être compris entre 0 et chunk_size - 1")
        
    words = text.split()
    if not words:
        return []
        
    chunks = []
    step = chunk_size - overlap
    for i in range(0, len(words), step):
        chunk = words[i:i + chunk_size]
        chunks.append(" ".join(chunk))
        if i + chunk_size >= len(words):
            break
    return chunks


# --- Suite de Tests Pytest ---

def test_clean_and_chunk_normal():
    """Test le fonctionnement normal avec une phrase de 8 mots, chunk_size=4 et overlap=1."""
    # TODO: Écrire les assertions assert len(result) == ... et vérifier le contenu des chunks.
    pass


def test_clean_and_chunk_empty_input():
    """Test le comportement quand le texte d'entrée est vide ou ne contient que des espaces."""
    # TODO: Vérifier que la fonction retourne une liste vide []
    pass


def test_clean_and_chunk_invalid_params():
    """Test que ValueError est levée quand overlap >= chunk_size ou chunk_size <= 0."""
    # TODO: Utiliser pytest.raises(ValueError) pour vérifier la levée d'exceptions
    pass


if __name__ == "__main__":
    print("Exercice 5 chargé. Complétez les fonctions de test pytest ci-dessus.")
