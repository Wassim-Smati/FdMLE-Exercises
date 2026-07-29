"""
Exercice 2 : Manipulation de Tenseurs PyTorch & Attention Prep

Contexte Entretien :
Dans un entretien de Live Coding ML (PyTorch), on vous demande très souvent d'effectuer des opérations 
sur des tenseurs 3D/4D représentant des séquences d'embeddings (Batch Size B, Sequence Length T, Embedding Dim D).
Comprendre le reshaping, le transposage et le broadcasting est la base absolue avant d'écrire une Multi-Head Attention.

Consignes :
1. Implémenter `split_heads` :
   - Prendre un tenseur de projection Query/Key/Value de forme (B, T, D).
   - Décomposer la dimension D en num_heads (H) * head_dim (d_k) avec D = H * d_k.
   - Réarranger les dimensions pour obtenir une forme finale (B, H, T, d_k).

2. Implémenter `compute_scaled_dot_product_scores` :
   - Prenez Q de forme (B, H, T, d_k) et K de forme (B, H, T, d_k).
   - Calculez le produit matriciel (Q x K^T) / sqrt(d_k) pour obtenir des scores d'attention de forme (B, H, T, T).
   - Appliquez un masque de causalité (remplacer les positions du futur par -inf).
"""

import math
import torch


def split_heads(x: torch.Tensor, num_heads: int) -> torch.Tensor:
    """Décompose la dernière dimension D en (num_heads, head_dim) et permute pour MHA.

    Args:
        x: Tenseur PyTorch de forme (B, T, D) où D = num_heads * head_dim.
        num_heads: Nombre de têtes d'attention H.

    Returns:
        Tenseur PyTorch de forme (B, H, T, d_k) où d_k = D // num_heads.
        
    Raises:
        ValueError: Si D n'est pas divisible par num_heads.
    """
    pass


def compute_scaled_dot_product_scores(
    Q: torch.Tensor, 
    K: torch.Tensor, 
    mask: torch.Tensor = None
) -> torch.Tensor:
    """Calcule les scores d'attention $(Q K^T) / \\sqrt{d_k}$ avec masque optionnel.

    Args:
        Q: Tenseur Query de forme (B, H, T, d_k).
        K: Tenseur Key de forme (B, H, T, d_k).
        mask: Tenseur masque optionnel (ex: booléen ou additif) de forme (B, 1, T, T) ou (1, 1, T, T).
              Si booléen : True indique les positions valides, False les positions à masquer (-inf).

    Returns:
        Tenseur des scores d'attention non-normalisés (avant Softmax) de forme (B, H, T, T).
    """
    pass


if __name__ == "__main__":
    print("Exercice 2 chargé. Complétez les fonctions PyTorch ci-dessus.")
