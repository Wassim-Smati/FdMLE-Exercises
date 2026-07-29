"""
Exercice 1 : Stratégies de Chunking (Découpage de Texte)

Contexte Entretien :
Dans un pipeline RAG, la première étape est de découper les documents volumineux en 'chunks' (morceaux) 
qui s'insèrent dans la fenêtre de contexte du modèle et permettent une recherche vectorielle précise.
Le chevauchement (overlap) préserve le contexte entre deux chunks consécutifs.

Consignes :
1. Implémenter `character_chunking` :
   - Découper une chaîne de caractères par taille fixe de caractères `chunk_size` et un `overlap`.

2. Implémenter `word_chunking_with_metadata` :
   - Découper un document texte par mots (tokens simples).
   - Conserver les métadonnées du document parent (ex: `doc_id`, `source`) et assigner un `chunk_id` séquentiel.
"""

from typing import List, Dict, Any


def character_chunking(text: str, chunk_size: int = 200, overlap: int = 50) -> List[str]:
    """Découpe un texte en morceaux de taille 'chunk_size' caractères avec un chevauchement 'overlap'.

    Args:
        text: Texte d'entrée à découper.
        chunk_size: Nombre de caractères par chunk (> 0).
        overlap: Nombre de caractères de chevauchement (0 <= overlap < chunk_size).

    Returns:
        Liste de chaînes de caractères représentant les chunks.

    Raises:
        ValueError: Si overlap >= chunk_size ou chunk_size <= 0.
    """
    pass


def word_chunking_with_metadata(
    doc_id: str,
    text: str,
    metadata: Dict[str, Any],
    chunk_size_words: int = 50,
    overlap_words: int = 10
) -> List[Dict[str, Any]]:
    """Découpe un texte par mots et produit une liste de dictionnaires enrichis de métadonnées.

    Args:
        doc_id: Identifiant unique du document parent.
        text: Contenu texte du document.
        metadata: Dictionnaire de métadonnées du document parent (ex: title, author, tenant_id).
        chunk_size_words: Nombre de mots par chunk.
        overlap_words: Chevauchement en nombre de mots.

    Returns:
        Liste de dictionnaires au format :
        [
            {
                "chunk_id": "doc_id_chunk_0",
                "doc_id": doc_id,
                "chunk_index": 0,
                "text": "contenu du chunk...",
                "word_count": int,
                "metadata": metadata
            },
            ...
        ]
    """
    pass


if __name__ == "__main__":
    print("Exercice C.1 chargé. Complétez les fonctions de chunking.")
