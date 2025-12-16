"""context - A filesystem-like interface for ChromaDB with semantic search.

Example usage:
    from context import FileSystem, connect

    # Connect to a collection
    fs = connect("my_docs")

    # Write files
    with fs.open("/readme.md", "w") as f:
        f.write("# Hello World")

    # Read files
    content = fs.read("/readme.md")

    # List files
    files = fs.listdir("/")
    matches = fs.glob("**/*.md")

    # Semantic search (requires embedder)
    results = fs.search("machine learning")
"""

__version__ = "0.1.0"
__author__ = "Jeff"
__license__ = "MIT"

from .client import ChromaClient, Document, QueryResult
from .filesystem import FileSystem, VirtualFile, SearchResult, connect
from .chunking import chunk_document, Chunk
from .config import Config

__all__ = [
    # Main interface
    "FileSystem",
    "VirtualFile",
    "SearchResult",
    "connect",
    # Client
    "ChromaClient",
    "Document",
    "QueryResult",
    # Chunking
    "chunk_document",
    "Chunk",
    # Config
    "Config",
    # Version
    "__version__",
]
