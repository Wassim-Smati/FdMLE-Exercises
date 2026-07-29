"""
Exercice 3 : Évaluation du Grounding & Détection d'Hallucinations

Contexte Entretien :
Une hallucination survient quand un LLM produit des faits non étayés par le contexte RAG fourni.
Vous devez savoir écrire des vérifications hors-ligne (Offline Evals) pour évaluer la présence 
de citations valides et vérifier que l'assistant refuse de répondre quand aucune source n'est disponible.

Consignes :
1. Implémenter `verify_citations_presence` :
   - Vérifier que la réponse générée contient au moins une citation au format `[doc:ID]` ou `[chunk:ID]`.

2. Implémenter `check_hallucination_refusal` :
   - Si les chunks fournis sont vides, vérifier que la réponse du LLM correspond bien au message de refus attendu.
"""

import re
from typing import List, Dict, Any, Tuple


def verify_citations_presence(answer: str) -> Tuple[bool, List[str]]:
    """Vérifie si la réponse contient des balises de citation valides.

    Args:
        answer: Réponse texte produite par le LLM.

    Returns:
        Tuple (has_citations: bool, list_of_extracted_citations: List[str]).
        Exemple : (True, ['doc:1 chunk:0', 'doc:2'])
    """
    pass


def evaluate_grounding_and_refusal(
    generated_answer: str,
    context_chunks: List[Dict[str, Any]],
    expected_refusal_keyword: str = "ne dispose pas de cette information"
) -> Dict[str, Any]:
    """Évalue si la réponse est correctement ancrée (grounded) ou si le refus est approprié.

    Args:
        generated_answer: Réponse du LLM.
        context_chunks: Liste des chunks transmis au prompt.
        expected_refusal_keyword: Mot-clé indiquant un refus valide.

    Returns:
        Dictionnaire au format :
        {
            "is_valid": bool,
            "reason": str  # Ex: "Valid Citations Found", "Valid Refusal", "Hallucination Detected"
        }
    """
    pass


if __name__ == "__main__":
    print("Exercice D.3 chargé. Complétez les fonctions d'évaluation du grounding.")
