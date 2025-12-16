"""Low-level Chroma HTTP client."""

import json
import urllib.request
import urllib.error
from typing import Optional, Any, List, Dict
from dataclasses import dataclass


@dataclass
class Document:
    """A document in Chroma."""
    id: str
    content: str
    metadata: Optional[Dict] = None
    embedding: Optional[List[float]] = None

    @property
    def path(self) -> Optional[str]:
        """Get path from metadata."""
        if self.metadata:
            return self.metadata.get("path")
        return None

    @property
    def chunk_index(self) -> int:
        """Get chunk index from metadata."""
        if self.metadata:
            return self.metadata.get("chunk_index", 0)
        return 0


@dataclass
class QueryResult:
    """A search result with distance score."""
    document: Document
    distance: float


class ChromaClient:
    """HTTP client for ChromaDB."""

    def __init__(
        self,
        url: str = "http://localhost:8000",
        tenant: str = "default_tenant",
        database: str = "default_database",
        api_key: Optional[str] = None,
    ):
        self.base_url = url.rstrip("/")
        self.tenant = tenant
        self.database = database
        self.api_key = api_key
        self._collection_ids: Dict[str, str] = {}  # name -> uuid cache

    def _request(
        self,
        method: str,
        path: str,
        data: Optional[Dict] = None,
    ) -> Any:
        """Make HTTP request to Chroma."""
        url = f"{self.base_url}{path}"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["x-chroma-token"] = self.api_key

        body = json.dumps(data).encode() if data else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            error_body = e.read().decode() if e.fp else ""
            raise RuntimeError(f"HTTP {e.code}: {error_body}") from e

    def _api_path(self, path: str) -> str:
        """Build API path with tenant/database."""
        return f"/api/v2/tenants/{self.tenant}/databases/{self.database}{path}"

    def _resolve_collection_id(self, name: str) -> str:
        """Resolve collection name to UUID."""
        if len(name) == 36 and name.count("-") == 4:
            return name
        if name in self._collection_ids:
            return self._collection_ids[name]
        coll = self.get_collection(name)
        if coll and "id" in coll:
            self._collection_ids[name] = coll["id"]
            return coll["id"]
        raise ValueError(f"Collection not found: {name}")

    def list_collections(self) -> List[str]:
        """List all collection names."""
        result = self._request("GET", self._api_path("/collections"))
        return [c["name"] for c in result] if result else []

    def get_collection(self, name: str) -> Optional[Dict]:
        """Get collection by name."""
        return self._request("GET", self._api_path(f"/collections/{name}"))

    def create_collection(self, name: str) -> Dict:
        """Create a collection."""
        return self._request("POST", self._api_path("/collections"), {"name": name})

    def delete_collection(self, name: str) -> None:
        """Delete a collection."""
        self._request("DELETE", self._api_path(f"/collections/{name}"))

    def get_or_create_collection(self, name: str) -> Dict:
        """Get existing or create new collection."""
        coll = self.get_collection(name)
        if coll:
            return coll
        return self.create_collection(name)

    def get_documents(
        self,
        collection: str,
        ids: Optional[List[str]] = None,
        where: Optional[Dict] = None,
        limit: int = 1000,
        offset: int = 0,
    ) -> List[Document]:
        """Get documents from collection."""
        coll_id = self._resolve_collection_id(collection)
        data: Dict[str, Any] = {"limit": limit, "offset": offset, "include": ["documents", "metadatas"]}
        if ids:
            data["ids"] = ids
        if where:
            data["where"] = where

        result = self._request("POST", self._api_path(f"/collections/{coll_id}/get"), data)
        if not result:
            return []

        docs = []
        for i, doc_id in enumerate(result.get("ids", [])):
            docs.append(Document(
                id=doc_id,
                content=result.get("documents", [None])[i] or "",
                metadata=result.get("metadatas", [None])[i],
            ))
        return docs

    def get_document(self, collection: str, doc_id: str) -> Optional[Document]:
        """Get single document by ID."""
        docs = self.get_documents(collection, ids=[doc_id])
        return docs[0] if docs else None

    def upsert_documents(
        self,
        collection: str,
        ids: List[str],
        documents: List[str],
        metadatas: Optional[List[Dict]] = None,
        embeddings: Optional[List[List[float]]] = None,
    ) -> None:
        """Upsert documents into collection."""
        coll_id = self._resolve_collection_id(collection)
        data: Dict[str, Any] = {"ids": ids, "documents": documents}
        if metadatas:
            data["metadatas"] = metadatas
        if embeddings:
            data["embeddings"] = embeddings
        self._request("POST", self._api_path(f"/collections/{coll_id}/upsert"), data)

    def delete_documents(
        self,
        collection: str,
        ids: Optional[List[str]] = None,
        where: Optional[Dict] = None,
    ) -> None:
        """Delete documents from collection."""
        coll_id = self._resolve_collection_id(collection)
        data: Dict[str, Any] = {}
        if ids:
            data["ids"] = ids
        if where:
            data["where"] = where
        self._request("POST", self._api_path(f"/collections/{coll_id}/delete"), data)

    def query(
        self,
        collection: str,
        query_embeddings: List[List[float]],
        n_results: int = 10,
        where: Optional[Dict] = None,
    ) -> List[QueryResult]:
        """Query by embedding vectors."""
        coll_id = self._resolve_collection_id(collection)
        data: Dict[str, Any] = {
            "query_embeddings": query_embeddings,
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            data["where"] = where

        result = self._request("POST", self._api_path(f"/collections/{coll_id}/query"), data)
        if not result or not result.get("ids"):
            return []

        results = []
        ids = result["ids"][0] if result.get("ids") else []
        documents = result["documents"][0] if result.get("documents") else []
        metadatas = result["metadatas"][0] if result.get("metadatas") else []
        distances = result["distances"][0] if result.get("distances") else []

        for i, doc_id in enumerate(ids):
            results.append(QueryResult(
                document=Document(
                    id=doc_id,
                    content=documents[i] if i < len(documents) else "",
                    metadata=metadatas[i] if i < len(metadatas) else None,
                ),
                distance=distances[i] if i < len(distances) else 0.0,
            ))
        return results

    def query_text(
        self,
        collection: str,
        query_text: str,
        n_results: int = 10,
        where: Optional[Dict] = None,
    ) -> List[QueryResult]:
        """Query by text (requires collection to have embedding function)."""
        coll_id = self._resolve_collection_id(collection)
        data: Dict[str, Any] = {
            "query_texts": [query_text],
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            data["where"] = where

        result = self._request("POST", self._api_path(f"/collections/{coll_id}/query"), data)
        if not result or not result.get("ids"):
            return []

        results = []
        ids = result["ids"][0] if result.get("ids") else []
        documents = result["documents"][0] if result.get("documents") else []
        metadatas = result["metadatas"][0] if result.get("metadatas") else []
        distances = result["distances"][0] if result.get("distances") else []

        for i, doc_id in enumerate(ids):
            results.append(QueryResult(
                document=Document(
                    id=doc_id,
                    content=documents[i] if i < len(documents) else "",
                    metadata=metadatas[i] if i < len(metadatas) else None,
                ),
                distance=distances[i] if i < len(distances) else 0.0,
            ))
        return results
