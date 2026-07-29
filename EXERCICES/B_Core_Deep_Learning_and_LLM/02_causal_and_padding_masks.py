"""
Exercice 2 : Masques Causal et de Padding (PyTorch)

Contexte Entretien :
Dans un Modèle de Langage Autorégressif (comme GPT ou Mistral), un token ne peut prêter attention 
qu'aux tokens qui le précèdent (pas aux tokens futurs). C'est le Masque Causal (Triangulaire Inferieur).
De plus, les séquences dans un batch sont complétées par du padding, qu'il faut masquer : le Masque de Padding.

Consignes :
1. Implémenter `create_causal_mask(seq_len: int)` :
   - Générer une matrice booléenne de forme (1, 1, seq_len, seq_len) où la partie inférieure triangulaire vaut True.

2. Implémenter `create_padding_mask(input_ids: torch.Tensor, pad_token_id: int)` :
   - Prendre un tenseur d'ids de forme (B, T) et retourner un masque de forme (B, 1, 1, T) avec True là où input_ids != pad_token_id.

3. Implémenter `combine_masks(causal_mask: torch.Tensor, padding_mask: torch.Tensor)` :
   - Combiner les deux masques via un ET logique (`&`) pour obtenir la matrice d'attention autorisée globale (B, 1, T, T).
"""

import torch


def create_causal_mask(seq_len: int) -> torch.Tensor:
    """Génère un masque triangulaire inférieur causal.

    Args:
        seq_len: Longueur de la séquence T.

    Returns:
        Tenseur booléen de forme (1, 1, T, T) avec True pour les positions autorisées 
        (i >= j) et False pour les positions futures (i < j).
    """
    pass


def create_padding_mask(input_ids: torch.Tensor, pad_token_id: int = 0) -> torch.Tensor:
    """Génère un masque de padding.

    Args:
        input_ids: Tenseur d'identifiants de tokens de forme (B, T).
        pad_token_id: L'identifiant représentant le token de padding (défaut: 0).

    Returns:
        Tenseur booléen de forme (B, 1, 1, T) où True indique un token valide (non-pad) 
        et False indique un token de padding.
    """
    pass


def combine_masks(causal_mask: torch.Tensor, padding_mask: torch.Tensor) -> torch.Tensor:
    """Combine un masque causal et un masque de padding via un ET logique broadcasté.

    Args:
        causal_mask: Tenseur booléen de forme (1, 1, T, T).
        padding_mask: Tenseur booléen de forme (B, 1, 1, T).

    Returns:
        Tenseur booléen combiné de forme (B, 1, T, T).
    """
    pass


if __name__ == "__main__":
    print("Exercice B.2 chargé. Complétez les fonctions de masquage PyTorch.")
