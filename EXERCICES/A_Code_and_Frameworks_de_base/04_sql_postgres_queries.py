"""
Exercice 4 : Requêtes SQL & Postgres pour RAG Multi-Tenant

Contexte Entretien :
Dans un environnement d'entreprise (comme Supabase/Postgres avec pgvector), la qualité et la sécurité 
de la recherche RAG dépendent directement des jointures SQL et des clauses de sécurité (Isolation Multi-Tenant, ACL, Soft-Deletes).

Schéma des tables :
- `rag_documents` (id UUID, tenant_id UUID, title TEXT, deleted_at TIMESTAMP)
- `rag_chunks` (id UUID, document_id UUID, tenant_id UUID, content TEXT, embedding VECTOR(1536), deleted_at TIMESTAMP)
- `rag_document_acl` (document_id UUID, user_id UUID, can_read BOOLEAN)

Consignes :
1. Écrire la fonction `get_vector_search_sql_query()` qui retourne une chaîne SQL paramétrée.
   La requête doit :
   - Sélectionner `c.id`, `c.document_id`, `c.content` et la distance vectorielle `(c.embedding <-> :query_embedding) AS distance`.
   - Joindre `rag_chunks` (c) avec `rag_documents` (d) et `rag_document_acl` (a).
   - Filtrer pour que `c.tenant_id = :tenant_id` ET `d.tenant_id = :tenant_id`.
   - Vérifier que `c.deleted_at IS NULL` ET `d.deleted_at IS NULL`.
   - Vérifier que `a.user_id = :user_id` ET `a.can_read = TRUE`.
   - Ordonner par distance vectorielle croissante et limiter à `:limit` résultats.
"""


def get_vector_search_sql_query() -> str:
    """Retourne la requête SQL paramétrée pour la recherche vectorielle sécurisée multi-tenant avec ACL.

    Returns:
        Une chaîne SQL valide contenant les paramètres paramétrés (:tenant_id, :user_id, :query_embedding, :limit).
    """
    pass


def format_sql_count_chunks_per_tenant() -> str:
    """Écrire une requête SQL qui compte le nombre total de chunks actifs (non supprimés) par tenant_id.

    Returns:
        Une chaîne SQL effectuant un GROUP BY tenant_id avec filtrage sur deleted_at IS NULL.
    """
    pass


if __name__ == "__main__":
    print("Exercice 4 chargé. Complétez les fonctions de génération SQL ci-dessus.")
