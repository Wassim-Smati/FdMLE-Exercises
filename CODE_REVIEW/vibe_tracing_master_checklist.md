# Master Checklist - Evaluation Key for vibe_tracing_bugged.py

This document keeps track of all architectural flaws, bugs, and best practices injected into `vibe_tracing_bugged.py` for Wassim's final practice exercise.

---

## 📋 List of Injected Flaws & Expectations

### 1. Mauvaise Architecture / Violation SRP (Single Responsibility Principle)
- **Code concerné** : `process_and_export_agent_telemetry` et `VibeTelemetryPipeline`
- **Problème** : Une seule classe/fonction fait la validation manuelle des entrées, le formatting OpenTelemetry, la sauvegarde SQL directe via `sqlite3`, l'export HTTP synchrone, et le formatting du retour.
- **Attente de correction** : 
  - Mentionner la violation du SRP (God Function / God Class).
  - Proposer une décomposition propre : DTO Pydantic (`TelemetryPayload`), Formatter, Repository DB, et Service Exporter HTTP.

### 2. Timeouts & Retries Manquants
- **Code concerné** : `build_otel_span_exporter_config` et `execute_llm_and_store_audit`
- **Problème** : `requests.post(...)` exécuté sans paramètre `timeout`, sans stratégie de retry (en cas de statut HTTP 503 temporaire), et avec accès direct à `response.json()["status"]` sans vérifier `response.status_code == 200`.
- **Attente de correction** : 
  - Utiliser `httpx.AsyncClient()` asynchrone.
  - Ajouter `timeout=5`.
  - Utiliser `response.raise_for_status()`.

### 3. Absence de Typage Python (Type Hints)
- **Code concerné** : `Span.__init__`, `Span.set_attribute`, `Tracer.start_span`, `build_otel_span_exporter_config`, `log_agent_execution_span`, `execute_llm_and_store_audit`, `trace_llm_inference_async`.
- **Problème** : Signatures brutes sans annotations de type ni types de retour.
- **Attente de correction** : 
  - Ajouter les type hints modernes Python 3.10+ (`str`, `dict[str, Any]`, `list[str]`, `str | None`, `-> dict[str, Any]`).

### 4. Noms de Variables Cryptiques / Obscurs
- **Code concerné** : `q`, `s`, `tmp`, `d`, `sp`, `txt`, `p`, `q_str`, `res1`.
- **Problème** : Variables monolettres ou génériques obscures au lieu de noms métier explicites.
- **Attente de correction** : 
  - Renommer `q` ➡️ `user_query`, `s` ➡️ `session_id`, `tmp` ➡️ `model_name`, `d` ➡️ `formatted_payload`, `sp` ➡️ `span`, `p` ➡️ `payload`, `q_str` ➡️ `query_string`, `res1` ➡️ `trace_result`.

### 5. Couplage Fort & Confusion des Services (LLM -> SQL -> HTTP)
- **Code concerné** : `VibeTelemetryPipeline.execute_llm_and_store_audit`
- **Problème** : Le service LLM appelle directement SQL, qui déclenche directement un appel HTTP synchrone, qui fait du parsing JSON manuel.
- **Attente de correction** : 
  - Découpler les services en 4 composants distincts : `LLMService`, `TelemetryRepository` (SQL), `TelemetryExporterClient` (HTTP), `SpanTelemetryService`.

### 6. Configuration Hardcodée (Secrets, URLs, Hyperparamètres)
- **Code concerné** : `SECRET_API_KEY`, `TELEMETRY_EXPORT_URL`, `DB_PATH`, `DEFAULT_MODEL_NAME`, `DEFAULT_TEMPERATURE`, `DEFAULT_TOP_P`.
- **Problème** : Hyperparamètres et secrets figés dans le code sous forme de constantes globales.
- **Attente de correction** : 
  - Créer un modèle Pydantic `TracingSettings(BaseSettings)` pour charger la config depuis l'environnement ou un fichier `.env`.

### 8. Stratégie de Test, Mocks & Edge Cases
- **Code concerné** : `build_otel_span_exporter_config`, `execute_llm_and_store_audit`, `trace_endpoint`
- **Questions d'entretien posées** :
  1. *Comment tester `build_otel_span_exporter_config` sans appel HTTP ?* ➡️ Utiliser `unittest.mock.patch("requests.post")` ou `respx` / `httpx.MockTransport`.
  2. *Comment tester `execute_llm_and_store_audit` sans écrire sur le disque ?* ➡️ Injecter une BDD SQLite en mémoire (`sqlite3.connect(":memory:")`) ou mocker le Repository.
  3. *Quels Edge Cases tester sur `trace_endpoint` ?* ➡️ JSON vide/invalide, `query=""`, timeout du service amont, requêtes simultanées concurrentes.

### 10. Scalabilité, Perfs, Memory OOM & Batching
- **Code concerné** : `batch_export_all_telemetry_logs(log_file_path)`
- **Problème** : `open().read()` charge un fichier de 10 Go en mémoire RAM d'un coup, puis boucle en N+1 appels HTTP uniques un par un.
- **Attente de réponse** :
  1. **Streaming (Generators / `yield`)** : Lire le fichier ligne par ligne (`for line in file:`).
  2. **Batching** : Envois par paquets de 100 entries.

### 11. Vulnérabilités de Sécurité Critiques (SQL Injection & Pickle RCE)
- **Code concerné** : `VibeTelemetryPipeline.execute_llm_and_store_audit` et `load_cached_spans`
- **Problèmes** :
  1. **SQL Injection** : `sql_query = f"INSERT INTO audit_logs VALUES ('{str(uuid.uuid4())}', '{s}', '{q}')"` via concaténation f-string brute !
  2. **RCE / Pickle Unsafe** : `pickle.loads(cache_file_bytes)` permettant l'exécution de code arbitraire à distance lors de la désérialisation.

### 12. Code Python Non-Idiomatique
- **Code concerné** : `batch_export_all_telemetry_logs`
- **Problème** : Utilisation de `for i in range(len(logs)): entry = logs[i]` au lieu d'une itération directe `for entry in logs:` ou d'un `enumerate()`.
- **Attente de correction** : 
  - Remplacer par l'itération directe pythonique `for entry in logs:`.

Things I don't know : 
-> timeout, stratégie de retry
-> syntaxe 'str | None'
-> config hardcodée -> os.environ ? config ? 
-> réponses a "comment tester?"
-> scale : streaming (yield?), batching
-> sécurité : pickle.loads, sql injections? 


La phrase Mistral parfaite à retenir :

"For external dependencies, I would add timeouts, retries with exponential backoff, and make sure retries are safe regarding idempotency."

La phrase code review si tu vois du code sans type hints :

"I would add proper type annotations here to make the expected inputs and outputs clearer, especially for optional values like str | None."

"I see hardcoded configuration values here. I would move them to environment variables using os.environ so the application can be configured differently across environments without modifying the code, and to avoid exposing secrets."

Les 3 phrases les plus importantes à retenir pour Mistral :
Dépendance externe :

"I would mock external dependencies to make the test deterministic and avoid relying on external services."

DB :

"I would inject the database dependency and use an in-memory database or a mock repository."

API :

"I would test both the happy path and failure cases, especially invalid inputs and downstream service failures."

En code review, si tu vois :
content = file.read()

Tu dis :

"This won't scale because we load the entire file into memory. I would stream the data using an iterator or a generator with yield."

Différence streaming vs batching

Ils résolvent deux problèmes différents :

Concept	Problème résolu
Streaming	Trop de données en mémoire
Batching	Trop d'appels réseau

Phrase parfaite en entretien :

Si tu vois :

content = file.read()

for log in logs:
    requests.post(...)

Tu peux dire :

"This won't scale because we load everything into memory and perform one network call per item. I would stream the data using generators and process it in batches to reduce memory usage and network overhead."

En code review :

Si tu vois :

cursor.execute(f"...{variable}...")

Tu dis :

"This is vulnerable to SQL injection. I would use parameterized queries instead of string concatenation."

En code review :

Si tu vois :

pickle.loads(user_input)

Tu dis :

"This is a security vulnerability because pickle deserialization can lead to remote code execution. I would avoid pickle for untrusted data and use a safer format like JSON."

**Objectifs pour demain (~The Last Dance~)**
-> Faire le final mock exam en mettant énormément l'accent sur l'oral
-> Une fois en anglais, une fois en français
-> Préparer les antisèches
-> Préparer les questions pour Soël
