"""
FLAMEHAVEN FileSearch - Open Source Semantic Document Search
Fast, simple, and transparent file search powered by Google Gemini
"""

import logging
import os
import textwrap
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from google import genai as google_genai
    from google.genai import types as google_genai_types
except ImportError:  # pragma: no cover - optional dependency
    google_genai = None
    google_genai_types = None

from .config import Config

logger = logging.getLogger(__name__)


class FlamehavenFileSearch:
    """
    FLAMEHAVEN FileSearch - Open source semantic document search

    Examples:
        >>> searcher = FlamehavenFileSearch()
        >>> result = searcher.upload_file("document.pdf")
        >>> answer = searcher.search("What are the key findings?")
        >>> print(answer['answer'])
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        config: Optional[Config] = None,
        allow_offline: bool = False,
    ):
        """
        Initialize FLAMEHAVEN FileSearch

        Args:
            api_key: Google GenAI API key (optional if set in environment)
            config: Configuration object (optional)
        """
        self.config = config or Config(api_key=api_key)
        self._use_native_client = bool(google_genai)

        # Validate config - API key required only for remote mode
        self.config.validate(require_api_key=not allow_offline)

        self._local_store_docs: Dict[str, List[Dict[str, str]]] = {}
        self.client = None

        if self._use_native_client:
            self.client = google_genai.Client(api_key=self.config.api_key)
            mode_label = "google-genai"
        else:
            mode_label = "local-fallback"
            logger.warning(
                "google-genai SDK not found; running FLAMEHAVEN FileSearch in "
                "local fallback mode."
            )

        self.stores: Dict[str, str] = {}  # Track remote IDs or local handles

        logger.info(
            "FLAMEHAVEN FileSearch initialized with model: %s (mode=%s)",
            self.config.default_model,
            mode_label,
        )

    def create_store(self, name: str = "default") -> str:
        """
        Create file search store

        Args:
            name: Store name

        Returns:
            Store resource name
        """
        if name in self.stores:
            logger.info("Store '%s' already exists", name)
            return self.stores[name]

        if self._use_native_client:
            try:
                store = self.client.file_search_stores.create()
                self.stores[name] = store.name
                logger.info("Created store '%s': %s", name, store.name)
                return store.name
            except Exception as e:
                logger.error("Failed to create store '%s': %s", name, e)
                raise

        # Local fallback mode
        store_id = f"local://{name}"
        self.stores[name] = store_id
        self._local_store_docs.setdefault(name, [])
        logger.info("Created local store '%s' (fallback mode)", name)
        return store_id

    def list_stores(self) -> Dict[str, str]:
        """
        List all created stores

        Returns:
            Dictionary of store names to resource names
        """
        return self.stores.copy()

    def upload_file(
        self,
        file_path: str,
        store_name: str = "default",
        max_size_mb: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Upload file with basic validation

        Args:
            file_path: Path to file to upload
            store_name: Store name to upload to
            max_size_mb: Maximum file size (defaults to config)

        Returns:
            Upload result dict with status, store, and file info
        """
        max_size_mb = max_size_mb or self.config.max_file_size_mb

        # Validate file exists
        if not os.path.exists(file_path):
            return {"status": "error", "message": f"File not found: {file_path}"}

        # Lite tier: Check file size only
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if size_mb > max_size_mb:
            return {
                "status": "error",
                "message": f"File too large: {size_mb:.1f}MB > {max_size_mb}MB",
            }

        # Check file extension
        ext = Path(file_path).suffix.lower()
        supported_exts = [".pdf", ".docx", ".md", ".txt"]
        if ext not in supported_exts:
            logger.warning("File extension '%s' may not be supported", ext)

        # Check/create store
        if store_name not in self.stores:
            logger.info("Creating new store: %s", store_name)
            self.create_store(store_name)

        if self._use_native_client:
            try:
                # Upload file
                logger.info("Uploading file: %s (%.2f MB)", file_path, size_mb)
                upload_op = self.client.file_search_stores.upload_to_file_search_store(
                    file_search_store_name=self.stores[store_name], file=file_path
                )

                # Simple polling
                timeout = self.config.upload_timeout_sec
                start = time.time()
                while not upload_op.done:
                    if time.time() - start > timeout:
                        return {"status": "error", "message": "Upload timeout"}
                    time.sleep(3)
                    upload_op = self.client.operations.get(upload_op)

                logger.info("Upload completed: %s", file_path)
                return {
                    "status": "success",
                    "store": store_name,
                    "file": file_path,
                    "size_mb": round(size_mb, 2),
                }

            except Exception as e:
                logger.error("Upload failed: %s", e)
                return {"status": "error", "message": str(e)}

        return self._local_upload(file_path, store_name, size_mb)

    def upload_files(
        self, file_paths: List[str], store_name: str = "default"
    ) -> Dict[str, Any]:
        """
        Upload multiple files

        Args:
            file_paths: List of file paths
            store_name: Store name to upload to

        Returns:
            Dict with upload results for each file
        """
        results = []
        for file_path in file_paths:
            result = self.upload_file(file_path, store_name)
            results.append({"file": file_path, "result": result})

        success_count = sum(1 for r in results if r["result"]["status"] == "success")
        return {
            "status": "completed",
            "total": len(file_paths),
            "success": success_count,
            "failed": len(file_paths) - success_count,
            "results": results,
        }

    def _local_upload(
        self, file_path: str, store_name: str, size_mb: float
    ) -> Dict[str, Any]:
        """Store file metadata/content locally when google-genai is unavailable."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as source:
                content = source.read()
        except OSError:
            content = ""

        self._local_store_docs.setdefault(store_name, []).append(
            {
                "title": Path(file_path).name,
                "uri": os.path.abspath(file_path),
                "content": content,
            }
        )
        logger.info("Stored file locally for fallback mode: %s", file_path)
        return {
            "status": "success",
            "store": store_name,
            "file": file_path,
            "size_mb": round(size_mb, 2),
        }

    def _local_search(
        self,
        store_name: str,
        query: str,
        max_tokens: int,
        temperature: float,
        model: str,
    ) -> Dict[str, Any]:
        """Simple local search fallback used when google-genai SDK is missing."""
        docs = self._local_store_docs.get(store_name, [])
        if not docs:
            return {
                "status": "error",
                "message": f"No files available in store '{store_name}'.",
            }

        matches = []
        for doc in docs:
            snippet = self._build_snippet(doc["content"], query)
            if snippet:
                matches.append((doc, snippet))

        if not matches:
            answer = "No matching content found in stored files."
            sources = [
                {"title": doc["title"], "uri": doc["uri"]}
                for doc in docs[: self.config.max_sources]
            ]
        else:
            sources = [
                {"title": doc["title"], "uri": doc["uri"]}
                for doc, _ in matches[: self.config.max_sources]
            ]
            answer = " ".join(snippet for _, snippet in matches[:5])

        return {
            "status": "success",
            "answer": answer,
            "sources": sources,
            "model": f"local-fallback:{model}",
            "query": query,
            "store": store_name,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

    def _build_snippet(self, content: str, query: str) -> str:
        """Extract a short snippet around the query text."""
        if not content:
            return ""

        haystack = content.lower()
        needle = query.lower()
        idx = haystack.find(needle)
        if idx == -1:
            return ""

        window = 160
        start = max(idx - window, 0)
        end = min(idx + len(needle) + window, len(content))
        snippet = content[start:end].replace("\n", " ").strip()
        snippet = " ".join(snippet.split())
        return textwrap.shorten(snippet, width=300, placeholder="...")

    def search(
        self,
        query: str,
        store_name: str = "default",
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Search and generate answer

        Args:
            query: Search query
            store_name: Store name to search in
            model: Model to use (defaults to config)
            max_tokens: Max output tokens (defaults to config)
            temperature: Model temperature (defaults to config)

        Returns:
            Dict with answer, sources, and metadata
        """
        model = model or self.config.default_model
        max_tokens = max_tokens or self.config.max_output_tokens
        temperature = (
            temperature if temperature is not None else self.config.temperature
        )

        if store_name not in self.stores:
            return {
                "status": "error",
                "message": (
                    f"Store '{store_name}' not found. Create it first or upload files."
                ),
            }

        if not self._use_native_client:
            return self._local_search(
                store_name=store_name,
                query=query,
                max_tokens=max_tokens,
                temperature=temperature,
                model=model,
            )

        try:
            logger.info("Searching in store '%s' with query: %s", store_name, query)

            # Call Google File Search
            response = self.client.models.generate_content(
                model=model,
                contents=query,
                config=google_genai_types.GenerateContentConfig(
                    tools=[
                        google_genai_types.Tool(
                            file_search=google_genai_types.FileSearch(
                                file_search_store_names=[self.stores[store_name]]
                            )
                        )
                    ],
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                    response_modalities=["TEXT"],
                ),
            )

            answer = response.text

            # Driftlock validation
            if len(answer) < self.config.min_answer_length:
                logger.warning("Answer too short: %d chars", len(answer))
            if len(answer) > self.config.max_answer_length:
                logger.warning("Answer too long: %d chars, truncating", len(answer))
                answer = answer[: self.config.max_answer_length]

            # Check banned terms
            for term in self.config.banned_terms:
                if term.lower() in answer.lower():
                    logger.error("Banned term detected: %s", term)
                    return {
                        "status": "error",
                        "message": f"Response contains banned term: {term}",
                    }

            # Extract grounding information
            grounding = response.candidates[0].grounding_metadata
            sources = []
            if grounding:
                sources = [
                    {
                        "title": c.retrieved_context.title,
                        "uri": c.retrieved_context.uri,
                    }
                    for c in grounding.grounding_chunks
                ]

            logger.info("Search completed with %d sources", len(sources))

            return {
                "status": "success",
                "answer": answer,
                "sources": sources[: self.config.max_sources],  # Lite: max 5 sources
                "model": model,
                "query": query,
                "store": store_name,
            }

        except Exception as e:
            logger.error("Search failed: %s", e)
            return {"status": "error", "message": str(e)}

    def delete_store(self, store_name: str) -> Dict[str, Any]:
        """
        Delete a store

        Args:
            store_name: Store name to delete

        Returns:
            Deletion result
        """
        if store_name not in self.stores:
            return {"status": "error", "message": f"Store '{store_name}' not found"}

        if self._use_native_client:
            try:
                self.client.file_search_stores.delete(name=self.stores[store_name])
                del self.stores[store_name]
                logger.info("Deleted store: %s", store_name)
                return {"status": "success", "store": store_name}
            except Exception as e:
                logger.error("Failed to delete store '%s': %s", store_name, e)
                return {"status": "error", "message": str(e)}

        # Local fallback deletion
        del self.stores[store_name]
        self._local_store_docs.pop(store_name, None)
        logger.info("Deleted local store: %s", store_name)
        return {"status": "success", "store": store_name}

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current metrics

        Returns:
            Dict with metrics
        """
        return {
            "stores_count": len(self.stores),
            "stores": list(self.stores.keys()),
            "config": self.config.to_dict(),
        }
