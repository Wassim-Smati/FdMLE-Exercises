"I see a reliability issue here."
→ bugs production, erreurs non gérées, timeouts manquants

"This creates strong coupling."
→ composants trop dépendants

"This will be hard to test."
→ side effects, HTTP/DB directement dans la logique

"This won't scale because..."
→ mémoire, N+1, trop d'appels, complexité

"This is a security concern."
→ secrets, injection, données non validées

"I would refactor this into..."
→ séparation des responsabilités

"This is a maintainability issue."
→ code difficile à lire/faire évoluer

"This is not production-ready yet."
→ prototype OK mais pas prêt prod

"I would add proper error handling here."
→ exceptions, validation, fallback

"I would make this configurable."
→ hardcoded values

"I would avoid blocking the event loop here."
→ async/FastAPI

"I would add observability here."
→ logs, metrics, trace IDs

"I would validate this input before processing it."
→ Pydantic, payloads

"I would use dependency injection here."
→ testabilité, découplage

"I would optimize this by batching/streaming."
→ performance, gros volumes