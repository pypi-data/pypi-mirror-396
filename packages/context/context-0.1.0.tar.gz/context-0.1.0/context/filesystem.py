"""Filesystem-like interface for context."""

import re
from io import StringIO
from typing import Optional, Iterator, List, Dict, Callable, Any
from dataclasses import dataclass

from .client import ChromaClient, Document
from .chunking import chunk_document
from .config import Config


@dataclass
class SearchResult:
    """Result from semantic search."""
    path: str
    content: str
    score: float
    metadata: Optional[Dict] = None


class VirtualFile:
    """File-like object for reading/writing."""

    def __init__(self, fs: "FileSystem", path: str, mode: str = "r"):
        self.fs = fs
        self.path = path
        self.mode = mode
        self._buffer = StringIO()
        self._closed = False

        if "r" in mode or "a" in mode:
            try:
                content = fs.read(path)
                if "a" in mode:
                    self._buffer.write(content)
                    self._buffer.seek(0, 2)
                else:
                    self._buffer.write(content)
                    self._buffer.seek(0)
            except FileNotFoundError:
                if "r" in mode and "+" not in mode:
                    raise

    def read(self, size: int = -1) -> str:
        if self._closed:
            raise ValueError("I/O operation on closed file")
        if "r" not in self.mode and "+" not in self.mode:
            raise IOError("File not open for reading")
        return self._buffer.read(size)

    def readline(self) -> str:
        if self._closed:
            raise ValueError("I/O operation on closed file")
        return self._buffer.readline()

    def readlines(self) -> List[str]:
        if self._closed:
            raise ValueError("I/O operation on closed file")
        return self._buffer.readlines()

    def write(self, data: str) -> int:
        if self._closed:
            raise ValueError("I/O operation on closed file")
        if "w" not in self.mode and "a" not in self.mode and "+" not in self.mode:
            raise IOError("File not open for writing")
        return self._buffer.write(data)

    def writelines(self, lines: List[str]) -> None:
        for line in lines:
            self.write(line)

    def seek(self, offset: int, whence: int = 0) -> int:
        if self._closed:
            raise ValueError("I/O operation on closed file")
        return self._buffer.seek(offset, whence)

    def tell(self) -> int:
        if self._closed:
            raise ValueError("I/O operation on closed file")
        return self._buffer.tell()

    def flush(self) -> None:
        if self._closed:
            raise ValueError("I/O operation on closed file")
        if "w" in self.mode or "a" in self.mode or "+" in self.mode:
            self.fs.write(self.path, self._buffer.getvalue())

    def close(self) -> None:
        if not self._closed:
            if "w" in self.mode or "a" in self.mode or "+" in self.mode:
                self.flush()
            self._closed = True

    @property
    def closed(self) -> bool:
        return self._closed

    def __enter__(self) -> "VirtualFile":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def __iter__(self) -> Iterator[str]:
        return iter(self._buffer)


class FileSystem:
    """Filesystem-like interface to a context collection."""

    def __init__(
        self,
        collection: str,
        url: Optional[str] = None,
        tenant: Optional[str] = None,
        database: Optional[str] = None,
        api_key: Optional[str] = None,
        auto_create: bool = True,
        embedder: Optional[Callable[[str], List[float]]] = None,
    ):
        config = Config.load()
        self.collection = collection
        self.client = ChromaClient(
            url=url or config.get_url(),
            tenant=tenant or config.tenant,
            database=database or config.database,
            api_key=api_key or config.api_key,
        )
        self.embedder = embedder
        if auto_create:
            self.client.get_or_create_collection(collection)

    def open(self, path: str, mode: str = "r") -> VirtualFile:
        """Open a file for reading or writing."""
        return VirtualFile(self, path, mode)

    def read(self, path: str) -> str:
        """Read entire file contents."""
        docs = self.client.get_documents(self.collection, where={"path": path}, limit=300)
        if not docs:
            raise FileNotFoundError(f"No such file: {path}")
        docs.sort(key=lambda d: d.chunk_index)
        return "".join(d.content for d in docs)

    def write(self, path: str, content: str) -> int:
        """Write content to file (overwrites existing)."""
        self._delete_path(path)
        chunks = chunk_document(content)

        ids = []
        documents = []
        metadatas: List[Dict[str, Any]] = []
        embeddings: List[List[float]] = []

        for chunk in chunks:
            chunk_path = f"{path}#{chunk.index}" if len(chunks) > 1 else path
            doc_id = self._path_to_id(chunk_path)
            ids.append(doc_id)
            documents.append(chunk.content)
            metadatas.append({
                "path": path,
                "chunk_index": chunk.index,
                "total_chunks": len(chunks),
            })
            if self.embedder:
                embeddings.append(self.embedder(chunk.content))
            else:
                embeddings.append([0.0] * 384)

        self.client.upsert_documents(
            self.collection, ids=ids, documents=documents,
            metadatas=metadatas, embeddings=embeddings,
        )
        return len(content.encode("utf-8"))

    def append(self, path: str, content: str) -> int:
        """Append content to file."""
        try:
            existing = self.read(path)
        except FileNotFoundError:
            existing = ""
        return self.write(path, existing + content)

    def exists(self, path: str) -> bool:
        """Check if file exists."""
        docs = self.client.get_documents(self.collection, where={"path": path}, limit=1)
        return len(docs) > 0

    def remove(self, path: str) -> None:
        """Remove a file."""
        if not self.exists(path):
            raise FileNotFoundError(f"No such file: {path}")
        self._delete_path(path)

    def unlink(self, path: str) -> None:
        """Alias for remove()."""
        self.remove(path)

    def listdir(self, path: str = "/") -> List[str]:
        """List files in a directory."""
        docs = self.client.get_documents(self.collection, limit=300)
        paths = set()
        for doc in docs:
            if doc.path:
                paths.add(doc.path)

        if not path.endswith("/"):
            path = path + "/"
        if path == "/":
            path = ""

        items = set()
        for p in paths:
            if p.startswith("/" + path if path else "/"):
                rest = p[len("/" + path if path else "/"):]
                if "/" in rest:
                    items.add(rest.split("/")[0])
                else:
                    items.add(rest)
        return sorted(items)

    def walk(self, top: str = "/") -> Iterator[tuple]:
        """Walk directory tree (like os.walk)."""
        docs = self.client.get_documents(self.collection, limit=300)
        paths = set()
        for doc in docs:
            if doc.path:
                paths.add(doc.path)

        dirs: Dict[str, tuple] = {}
        for p in paths:
            parts = p.strip("/").split("/")
            filename = parts[-1]
            dirpath = "/" + "/".join(parts[:-1]) if len(parts) > 1 else "/"
            if dirpath not in dirs:
                dirs[dirpath] = (set(), set())
            dirs[dirpath][1].add(filename)
            for i in range(len(parts) - 1):
                parent = "/" + "/".join(parts[:i]) if i > 0 else "/"
                child = parts[i]
                if parent not in dirs:
                    dirs[parent] = (set(), set())
                dirs[parent][0].add(child)

        def _walk(d: str) -> Iterator[tuple]:
            if d not in dirs:
                return
            subdirs, files = dirs[d]
            yield d, sorted(subdirs), sorted(files)
            for subdir in sorted(subdirs):
                subpath = f"{d}/{subdir}".replace("//", "/")
                yield from _walk(subpath)

        yield from _walk(top)

    def glob(self, pattern: str) -> List[str]:
        """Find files matching glob pattern."""
        docs = self.client.get_documents(self.collection, limit=300)
        paths = set()
        for doc in docs:
            if doc.path:
                paths.add(doc.path)
        regex = self._glob_to_regex(pattern)
        return sorted(p for p in paths if regex.match(p))

    def _glob_to_regex(self, pattern: str) -> Any:
        pattern = pattern.replace("**", "{{RECURSIVE}}")
        pattern = re.escape(pattern)
        pattern = pattern.replace(r"\*", "[^/]*")
        pattern = pattern.replace(r"\?", "[^/]")
        pattern = pattern.replace("\\{\\{RECURSIVE\\}\\}", ".*")
        if not pattern.startswith("/"):
            pattern = ".*" + pattern
        return re.compile(f"^{pattern}$")

    def search(
        self,
        query: str,
        k: int = 10,
        path_pattern: Optional[str] = None,
    ) -> List[SearchResult]:
        """Semantic search for documents."""
        if not self.embedder:
            raise RuntimeError("No embedder configured. Pass embedder= to FileSystem()")

        query_embedding = self.embedder(query)
        results = self.client.query(self.collection, query_embeddings=[query_embedding], n_results=k * 2)

        search_results = []
        seen_paths: set = set()

        for r in results:
            path = r.document.path
            if not path or path in seen_paths:
                continue
            if path_pattern:
                regex = self._glob_to_regex(path_pattern)
                if not regex.match(path):
                    continue
            seen_paths.add(path)
            search_results.append(SearchResult(
                path=path,
                content=r.document.content,
                score=1.0 - r.distance,
                metadata=r.document.metadata,
            ))
            if len(search_results) >= k:
                break
        return search_results

    def search_text(
        self,
        query: str,
        k: int = 10,
        path_pattern: Optional[str] = None,
    ) -> List[SearchResult]:
        """Text-based search."""
        results = self.client.query_text(self.collection, query_text=query, n_results=k * 2)

        search_results = []
        seen_paths: set = set()

        for r in results:
            path = r.document.path
            if not path or path in seen_paths:
                continue
            if path_pattern:
                regex = self._glob_to_regex(path_pattern)
                if not regex.match(path):
                    continue
            seen_paths.add(path)
            search_results.append(SearchResult(
                path=path,
                content=r.document.content,
                score=1.0 - r.distance,
                metadata=r.document.metadata,
            ))
            if len(search_results) >= k:
                break
        return search_results

    def stat(self, path: str) -> Dict[str, Any]:
        """Get file statistics."""
        docs = self.client.get_documents(self.collection, where={"path": path}, limit=300)
        if not docs:
            raise FileNotFoundError(f"No such file: {path}")
        total_size = sum(len(d.content.encode("utf-8")) for d in docs)
        return {"path": path, "size": total_size, "chunks": len(docs)}

    def _delete_path(self, path: str) -> None:
        self.client.delete_documents(self.collection, where={"path": path})

    def _path_to_id(self, path: str) -> str:
        return "".join(c if c.isalnum() or c in "-_" else "_" for c in path)


def connect(collection: str, url: Optional[str] = None, **kwargs: Any) -> FileSystem:
    """Connect to a context collection."""
    return FileSystem(collection, url=url, **kwargs)
