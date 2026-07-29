"""
Exercice 1 : Constructeur de System Prompt & Contraintes de Format

Contexte Entretien :
Formater des prompts système robustes est indispensable en production pour s'assurer que le LLM 
respecte son rôle, utilise le contexte fourni, refuse de répondre si l'information est manquante 
et produit une sortie strictement conforme au format demandé (ex: JSON ou Markdown avec citations).

Consignes :
1. Implémenter la fonction `build_system_prompt` :
   - Accepter un rôle (ex: "Support Technique"), des instructions système, des règles de refus et un format de sortie.

2. Implémenter `format_rag_context_block` :
   - Structurer les chunks sous un bloc XML/Markdown clair `<context>...</context>` sans fuite de prompt.
"""

from typing import List, Dict, Any, Optional


def build_system_prompt(
    role: str,
    instructions: List[str],
    refusal_message: str = "Je ne dispose pas de cette information dans les documents fournis.",
    output_format: str = "JSON"
) -> str:
    """Génère un System Prompt structuré avec contraintes strictes.

    Args:
        role: Le rôle attribué à l'assistant (ex: 'Assistant Support Client').
        instructions: Liste de règles métiers à appliquer (ex: ['Ne jamais inventer d'information', ...]).
        refusal_message: Phrase exacte à retourner si le contexte est insuffisant.
        output_format: Format exigé pour la réponse ('JSON' ou 'MARKDOWN').

    Returns:
        Chaîne de caractères du System Prompt complet.
    """
    pass


def format_rag_context_block(chunks: List[Dict[str, Any]]) -> str:
    """Formatte une liste de chunks sous la forme d'un bloc de contexte balisé et sécurisé.

    Args:
        chunks: Liste de dicts contenant au moins 'chunk_id' et 'text'.

    Returns:
        Chaîne formatée avec balises de séparation.
    """
    pass


if __name__ == "__main__":
    print("Exercice D.1 chargé. Complétez les fonctions de construction de prompts.")
