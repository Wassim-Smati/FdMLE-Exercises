"""
Exercice 4 : Tokenization & Embedding Layer (PyTorch)

Contexte Entretien :
Pour entrer dans un modèle LLM / Transformer, du texte brut doit d'abord être converti en une suite d'identifiants 
numériques (tokens), puis chaque token ID est transformé en un vecteur dense auquel on ajoute une Positional Encoding.

Consignes :
1. Implémenter la classe `SimpleVocabulary` :
   - Construire un vocabulaire à partir d'un corpus de texte (avec tokens spéciaux `<pad>` et `<unk>`).
   - Méthodes `encode(text: str) -> List[int]` et `decode(token_ids: List[int]) -> str`.

2. Implémenter le module PyTorch `TransformerEmbedding` :
   - Combiner un `nn.Embedding` pour les tokens et un `nn.Embedding` (ou encodage sinusoïdal) pour les positions.
   - Calculer `embedding_tokens + positional_embeddings` pour un tenseur `input_ids` de forme (B, T).
"""

import torch
import torch.nn as nn
from typing import List, Dict


class SimpleVocabulary:
    """Vocabulaire simple basé sur les mots pour la démonstration de tokenization."""

    def __init__(self, pad_token: str = "<pad>", unk_token: str = "<unk>"):
        self.pad_token = pad_token
        self.unk_token = unk_token
        self.token_to_id: Dict[str, int] = {pad_token: 0, unk_token: 1}
        self.id_to_token: Dict[int, str] = {0: pad_token, 1: unk_token}

    def build_vocab(self, texts: List[str]) -> None:
        """Construit le dictionnaire de tokens à partir d'une liste de textes."""
        pass

    def encode(self, text: str) -> List[int]:
        """Convertit une chaîne de texte en une liste d'identifiants de tokens (IDs)."""
        pass

    def decode(self, token_ids: List[int]) -> str:
        """Convertit une liste d'identifiants de tokens (IDs) en une chaîne de texte."""
        pass


class TransformerEmbedding(nn.Module):
    """Module PyTorch combinant Token Embeddings et Learned Positional Embeddings."""

    def __init__(self, vocab_size: int, embed_dim: int, max_seq_len: int = 512):
        """Initialise la table d'embeddings des tokens et des positions.

        Args:
            vocab_size: Taille du vocabulaire.
            embed_dim: Dimension de l'espace vectoriel d'embedding D.
            max_seq_len: Longueur maximale de séquence supportée.
        """
        super().__init__()
        # TODO: Définir self.token_embedding (nn.Embedding) et self.pos_embedding (nn.Embedding)
        pass

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        """Calcule la représentation vectorielle finale (Tokens + Positions).

        Args:
            input_ids: Tenseur d'identifiants de tokens de forme (B, T).

        Returns:
            Tenseur d'embeddings de forme (B, T, D).
        """
        pass


if __name__ == "__main__":
    print("Exercice B.4 chargé. Complétez la classe SimpleVocabulary et le module TransformerEmbedding.")
