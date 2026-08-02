"""MCP server exposing search and ingest tools for the local Vespa index."""

import os
import requests
import logging
import httpx
import asyncio
import uuid
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import url2pathname

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastapi import FastAPI, Request
from pydantic import BaseModel, Field

from mistralai.client import Mistral
from mistralai.search.toolkit.embedders import MistralEmbedder
from mistralai.search.toolkit.document import compute_id
from mistralai.search.toolkit.ingestion import File
from mistralai.search.toolkit.ingestion.extractors import (
    MistralOCRExtractor,
    PlainTextExtractor,
)
from mistralai.search.toolkit.ingestion.loaders import FilesystemFileLoader
from mistralai.search.toolkit.ingestion.pipelines import Pipeline
from mistralai.search.toolkit.ingestion.text_splitters import (
    MarkdownTextSplitter,
    MarkdownTextSplitterConfig,
)
from mistralai.search.toolkit.plugins.vespa import VespaClientConfig
from mistralai.search.toolkit.retrieval import QueryEngine, VectorRetriever
from mistralai.search.toolkit.search import GrepMode, NavigableIndex, NavigationDirection
from mistralai.search.toolkit.search.errors import DocumentNotFoundError
from vespa_app import app, vespa_endpoint

load_dotenv(override=True)
logger = logging.getLogger("mcp_server_service")

_TEXT_SUFFIXES = {".txt", ".md", ".markdown", ".csv", ".json"}

# [BLOCKER] clé secrète en dur dans le code -> utiliser secret management
MISTRAL_API_KEY = os.environ.get('MISTRAL_KEY', "")

_mistral_client = Mistral(
    api_key=MISTRAL_API_KEY,
    server_url=os.getenv("MISTRAL_API_URL", "https://api.mistral.ai"),
)

_embedder = MistralEmbedder(client=_mistral_client)

_vector_store = app.get_search_index(
    VespaClientConfig(endpoint=vespa_endpoint()),
    collection_name=os.environ.get("COLLECTION_NAME", "exampledocs"),
    query_profile="hybrid-search",
)

_query_engine = QueryEngine(
    retriever=[VectorRetriever(client=_vector_store, embedder=_embedder)],
)

# [BLOCKER] [], {} en paramètre -> mutable -> partage de données entre utilisateurs -> None
def _format_chunks(results: list = None, extra_meta: dict = None) -> list:

    if not results: 
        results = []
    if not extra_meta:
        extra_meta = {}

    extra_meta["formatted"] = True
    return [
        {
            "score": hit.score,
            "content": hit.chunk.content,
            "source_id": hit.chunk.source_id,
            "locator": hit.chunk.locator,
            "start_offset": hit.chunk.start_offset,
            "end_offset": hit.chunk.end_offset,
            "metadata": extra_meta,
        }
        for hit in results
    ]


mcp = FastMCP(
    "Search Starter App Documents",
    instructions="Search and navigate a local document index.",
)

@mcp.tool()
async def search(query: str, tenant_id: str = "default", top_k: int = 5) -> list[dict]:
    #[MAJOR] rajouter await 
    #[MAJOR] pas de validation pydantic de la query 
    #[MAJOR] pas de try/except ni de log 
    #[BLOCKER] tenant_id pas utilisé dans la recherche -> potentiel data leakage 

    try: 
        result = await _query_engine.search(
            query=query,
            top_k=top_k,
            include_metadata=True,
            include_content=True,
            tenant_id=tenant_id,
        )
    
        #[BLOCKER] manque extra_meta
        return _format_chunks(result.results, result.extra_meta)

    except Exception as e: 
        logger.exception('failed to fetch chunks from vector_database with tenant_id : %s', tenant_id)
        raise 


async def _ingest_single_url(url: str) -> str:
    #requests est une bibli synchrone ! remplacer par async with httpx.AsyncClient() as client : response = await client.get(url)

    try: 
        async with httpx.AsyncClient() as client: 
            response = await client.get(url, timeout=5)

        #[MAJOR] mieux de try except et lever une HTTPException (pas sûr) + log
        if response.status_code != 200:
            return "Error: HTTP request failed"
        
        file_bytes = response.content
        file = File(path=url, name="downloaded_doc", raw=file_bytes, source_id=url)
        
        pipeline = Pipeline(
            loader=FilesystemFileLoader(),
            extractor=PlainTextExtractor(),
            text_splitter=MarkdownTextSplitter(MarkdownTextSplitterConfig(chunk_size=4096)),
            embedder=_embedder,
            stores=_vector_store,
        )
        
        doc = await pipeline.run_file(file)
        return f"Indexed {len(doc.chunks)} chunks."

    except Exception as e: 
        logger.exception("Failed to fetch document with url %s", url)
        raise 



@mcp.tool()
async def batch_ingest_urls(urls: list[str]) -> list[str]:
    results = []
    
    #[MAJOR] un appel réseau par doc -> gaspillage -> faire des appel groupés a la vector DB grâce a asyncio.gather

    tasks = [_ingest_single_url(url) for url in urls]
    results = await asyncio.gather(*tasks)

    return results


@mcp.tool()
async def delete(source_id: str, trace_id: str) -> str:
    try:
        await _vector_store.delete_document(compute_id(source_id))
        return f"Deleted document '{source_id}'."

    except Exception as e:
        logger.exception("Failed to delete document with id %s, trace_id: %s", source_id, trace_id)
        raise


fastapi_app = FastAPI(title="Mistral Search MCP Service")

class ValidSource(BaseModel): 
    source_id: str

@fastapi_app.post("/api/v1/delete")
async def delete_endpoint(request: ValidSource):
    source_id = request.source_id
    trace_id = str(uuid.uuid4())

    #[MAJOR] pas de trace_id pour la requête permettant de la suivre, pas de spans telemtry
    #[MAJOR] pas de validation pydantic de l'entrée 
    #[MAJOR] post sans idempotence key -> potentiel essai de détruire une ressource qui existe pas -> crash

    res = await delete(source_id, trace_id)

    #[MAJOR] return en cas d'erreur dans fastapi -> return 200 succès alors que NON -> raise HTTP error
    if res is None:
        raise HTTPException(
            status_code=404,
            detail="document introuvable ou supprimé"
        )

    return {"status": "success", "result": res}
