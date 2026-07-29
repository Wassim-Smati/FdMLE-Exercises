"""
Exercice 1 : Scaled Dot-Product Attention (PyTorch)

Contexte Entretien :
C'est LA question classique de Live Coding chez Mistral AI et dans les startups d'IA.
La formule théorique est :
    Attention(Q, K, V) = Softmax( (Q * K^T) / sqrt(d_k) + Mask ) * V

Consignes :
1. Écrire la fonction `scaled_dot_product_attention` à partir de zéro avec PyTorch.
2. Gérer le scaling par 1 / sqrt(d_k).
3. Remplacer les positions masquées par -inf (ou une grande valeur négative comme -1e9) avant le Softmax.
4. Appliquer torch.softmax sur la dernière dimension.
5. Retourner le tenseur de sortie ET la matrice des poids d'attention (pour la visualisation ou les tests).
"""

import math
import torch
import torch.nn.functional as F
from typing import Tuple, Optional


def scaled_dot_product_attention(
    query: torch.Tensor,
    key: torch.Tensor,
    value: torch.Tensor,
    mask: Optional[torch.Tensor] = None
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Calcule l'attention produit scalaire à l'échelle.

    Args:
        query: Tenseur Query de forme (B, H, T_q, d_k)
        key: Tenseur Key de forme (B, H, T_k, d_k)
        value: Tenseur Value de forme (B, H, T_v, d_v) avec T_k == T_v
        mask: Tenseur masque optionnel de forme (B, 1, T_q, T_k) ou (1, 1, T_q, T_k).
              Les positions où mask == 0 (ou False) doivent être masquées (-1e9 ou -inf).

    Returns:
        Tuple contenant :
        - output: Tenseur de sortie de forme (B, H, T_q, d_v)
        - attention_weights: Tenseur des poids d'attention après Softmax, de forme (B, H, T_q, T_k)
    """
    pass


if __name__ == "__main__":
    print("Exercice B.1 chargé. Complétez la fonction scaled_dot_product_attention.")
