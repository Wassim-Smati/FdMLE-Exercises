"""
Exercice 3 : Multi-Head Self-Attention (MHA) From-Scratch (PyTorch nn.Module)

Contexte Entretien :
Il s'agit du test d'architecture ultime en entretien chez Mistral AI / OpenAI.
Il faut être capable d'écrire un module PyTorch complet `MultiHeadAttention(nn.Module)` 
sans utiliser `torch.nn.MultiheadAttention`.

Architecture :
    Input (B, T, D)
       │
   ┌───┼───┐
  W_q W_k W_v  (Projections Linéaires D -> D)
   │   │   │
 Split Heads (B, H, T, d_k)
   │   │   │
 Scaled Dot-Product Attention (avec Masque optionnel)
       │
 Concat Heads (B, T, D)
       │
     W_out     (Projection Linéaire finale D -> D)
       │
    Output (B, T, D)
"""

import math
import torch
import torch.nn as nn
from typing import Optional


class MultiHeadSelfAttention(nn.Module):
    """Implémentation From-Scratch du module Multi-Head Self-Attention."""

    def __init__(self, embed_dim: int, num_heads: int):
        """Initialise les couches de projection de l'attention multi-têtes.

        Args:
            embed_dim: Dimension totale de l'embedding D.
            num_heads: Nombre de têtes d'attention H.

        Raises:
            ValueError: Si embed_dim n'est pas divisible par num_heads.
        """
        super().__init__()
        if embed_dim % num_heads != 0:
            raise ValueError("embed_dim doit être divisible par num_heads")

        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads

        # TODO: Définir les projections linéaires w_q, w_k, w_v et w_out
        pass

    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Passe avant du module MHA.

        Args:
            x: Tenseur d'entrée de forme (B, T, D)
            mask: Tenseur masque optionnel de forme (B, 1, T, T) ou booléen

        Returns:
            Tenseur de sortie de forme (B, T, D)
        """
        pass


if __name__ == "__main__":
    print("Exercice B.3 chargé. Complétez la classe MultiHeadSelfAttention.")
