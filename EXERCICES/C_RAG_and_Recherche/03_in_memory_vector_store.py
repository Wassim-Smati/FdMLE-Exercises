"""
Exercice 3 : Base de Données Vectorielle en Mémoire (Vector Store & Top-K Retrieval)

Contexte Entretien :
Dans de nombreux tests de Live Coding, il vous est demandé d'implémenter un 'Vector Store' 
en mémoire sans utiliser de bibliothèque externe (Chroma, Pinecone, FAISS). 
Vous devez savoir stocker des vecteurs d'embeddings et effectuer une recherche k-NN (k-Nearest Neighbors).

Consignes :
1. Implémenter la classe `SimpleVectorStore` :
   - Stocker les enregistrements sous forme de structures contenant `chunk_id`, `text`, `embedding` et `metadata`.
   - Méthode `add_documents(chunks: List[Dict[str, Any]], embeddings: List[List[float]])`.
   - Méthode `similarity_search(query_embedding: List[float], top_k: int = 3, tenant_id: str = None)`.
"""

from typing import List, Dict, Any, Tuple


class SimpleVectorStore:
    """Base de données vectorielle en mémoire pour recherche k-NN."""

    def __init__(self):
        self.records: List[Dict[str, Any]] = []

    def add_documents(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]) -> None:
        """Ajoute des chunks et leurs embeddings correspondants dans le store.

        Args:
            chunks: Liste de dicts (doit contenir 'chunk_id', 'text', 'metadata').
            embeddings: Liste des vecteurs d'embeddings associés (même longueur que chunks).

        Raises:
            ValueError: Si le nombre de chunks et d'embeddings ne correspond pas.
        """
        pass

    def similarity_search(
        self,
        query_embedding: List[float],
        top_k: int = 3,
        tenant_id: str = None
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Recherche les top_k chunks les plus similaires au vecteur query_embedding par similarité cosinus.

        Args:
            query_embedding: Vecteur de la question.
            top_k: Nombre de résultats à retourner.
            tenant_id: Filtre optionnel pour isoler les données d'un client spécifique (tenant).

        Returns:
            Liste de tuples (chunk_dict, score_similarite) triée par score décroissant.
        """
        pass


if __name__ == "__main__":
    print("Exercice C.3 chargé. Complétez la classe SimpleVectorStore.")
