# context

A filesystem-like interface for ChromaDB with semantic search.

## Installation

```bash
pip install context
```

For Python < 3.11, install with TOML support for config file reading:

```bash
pip install context[toml]
```

## Quick Start

```python
from context import connect

# Connect to a collection (uses ~/.config/cvfs/config.toml if available)
fs = connect("my_docs")

# Write files (like Python's built-in open)
with fs.open("/docs/readme.md", "w") as f:
    f.write("# Hello World\n")
    f.write("This is my document.\n")

# Read files
content = fs.read("/docs/readme.md")

# List directory contents
files = fs.listdir("/docs")  # ['readme.md']

# Glob pattern matching
md_files = fs.glob("**/*.md")  # ['/docs/readme.md']

# Check if file exists
if fs.exists("/docs/readme.md"):
    print("File exists!")

# Remove files
fs.remove("/docs/readme.md")
```

## Features

### Familiar Python Interface

context provides a filesystem-like API that feels natural to Python developers:

| context | Python equivalent |
|---------|-------------------|
| `fs.open(path, mode)` | `open(path, mode)` |
| `fs.read(path)` | `Path(path).read_text()` |
| `fs.write(path, content)` | `Path(path).write_text(content)` |
| `fs.exists(path)` | `os.path.exists(path)` |
| `fs.remove(path)` | `os.remove(path)` |
| `fs.listdir(path)` | `os.listdir(path)` |
| `fs.walk(path)` | `os.walk(path)` |
| `fs.glob(pattern)` | `glob.glob(pattern)` |
| `fs.stat(path)` | `os.stat(path)` |

### Semantic Search

With an embedder function, you can perform semantic search:

```python
from context import FileSystem

def my_embedder(text: str) -> list[float]:
    # Your embedding function here
    # Returns a 384-dimensional vector
    ...

fs = FileSystem("my_docs", embedder=my_embedder)

# Write some documents
fs.write("/ml/intro.md", "Machine learning is a subset of AI...")
fs.write("/ml/neural.md", "Neural networks are inspired by the brain...")

# Semantic search
results = fs.search("artificial intelligence", k=5)
for r in results:
    print(f"{r.path}: {r.score:.3f}")
```

### Configuration

context reads ChromaDB connection settings from `~/.config/cvfs/config.toml` (Linux) or `~/Library/Application Support/cvfs/config.toml` (macOS):

```toml
remote_url = "https://api.trychroma.com"
api_key = "your-api-key"
tenant = "your-tenant-id"
database = "your-database"
```

Or configure programmatically:

```python
from context import FileSystem

fs = FileSystem(
    "my_collection",
    url="http://localhost:8000",
    tenant="default_tenant",
    database="default_database",
)
```

## API Reference

### FileSystem

The main interface for interacting with ChromaDB as a filesystem.

```python
class FileSystem:
    def __init__(
        self,
        collection: str,
        url: str = None,           # ChromaDB URL
        tenant: str = None,        # Tenant ID
        database: str = None,      # Database name
        api_key: str = None,       # API key
        auto_create: bool = True,  # Create collection if missing
        embedder: callable = None, # Embedding function
    ): ...
```

### File Operations

```python
# Open file (returns file-like object)
with fs.open("/path", "w") as f:
    f.write("content")

# Direct read/write
content = fs.read("/path")
fs.write("/path", "content")
fs.append("/path", "more content")
```

### Directory Operations

```python
fs.listdir("/")           # List directory contents
fs.exists("/path")        # Check if file exists
fs.remove("/path")        # Delete file
fs.stat("/path")          # Get file statistics

# Walk directory tree
for dirpath, dirs, files in fs.walk("/"):
    print(dirpath, files)

# Glob pattern matching
fs.glob("**/*.md")        # Find all markdown files
fs.glob("/docs/*.txt")    # Find txt files in /docs
```

### Search Operations

```python
# Semantic search (requires embedder)
results = fs.search("query", k=10)
results = fs.search("query", path_pattern="**/*.md")

# Text search (requires Chroma embedding function)
results = fs.search_text("query", k=10)
```

### connect()

Convenience function to create a FileSystem:

```python
from context import connect

fs = connect("my_collection")
fs = connect("my_collection", url="http://localhost:8000")
```

## Requirements

- Python 3.8+
- ChromaDB server (local or cloud)

## License

MIT
