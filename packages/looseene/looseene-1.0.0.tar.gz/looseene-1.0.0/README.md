# looseene 🕵️‍♂️

**A tiny, persistent, full-text search engine in a single Python file.**

It's like Lucene, but... *looser*.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

### What is `looseene`?

`looseene` is a lightweight, zero-dependency search library for Python projects where setting up Elasticsearch or Solr is overkill. It provides a simple API to index documents, persist them to disk efficiently, and perform relevant full-text searches with modern ranking and highlighting.

It's the perfect solution for:
*   Adding search to a static site generator (e.g., indexing Markdown files).
*   Searching through application logs or local documents.
*   Desktop applications needing offline search capabilities.
*   Prototyping search features before scaling up to a larger system.

### Installation

To install `looseene`, you can clone the repository and install it directly using pip:
```bash
git clone https://github.com/YOUR_USERNAME/looseene.git
cd looseene
pip install .
```
*(Note: Once the package is on PyPI, this will become `pip install looseene`)*

### Quick Start

Get up and running in less than a minute.

```python
from looseene import create_index, add_to_index, search_text, highlight_result, save_index

# 1. Create a new index or load an existing one from disk.
# The schema defines your document structure. 'id' must be an integer primary key.
create_index(
    'my_docs', 
    schema={'id': int, 'title': str, 'content': str}, 
    path='./my_index_data'
)

# 2. Add some documents. You can add them in batches.
docs = [
    {'id': 1, 'title': 'The Fox', 'content': 'The quick brown fox jumps over the lazy dog.'},
    {'id': 2, 'title': 'The Engine', 'content': 'A lazy developer never creates a good search engine.'}
]
for doc in docs:
    add_to_index('my_docs', doc)

# 3. Flush the in-memory buffer to disk to make the index persistent.
save_index('my_docs')

# 4. Search returns results ranked by BM25 relevance.
query = "lazy fox search"
print(f"Searching for: '{query}'\n")

for doc in search_text('my_docs', query):
    # The 'content' field will be used for highlighting.
    snippet = highlight_result(doc, 'content', query)
    print(f"📄 ID: {doc['id']} | Title: {doc['title']}")
    print(f"   Snippet: {snippet}\n")
```

### Features

`looseene` is packed with features typically found in much larger search systems:

*   🗄️ **Persistent On-Disk Storage:** Your index lives on disk. It uses a Log-Structured Merge-tree (LSM) architecture, flushing data in immutable, compressed segments. This means your data is safe even if your application restarts.
*   🚀 **Fast & Memory-Efficient:** Leverages `mmap` to search through gigabytes of data without loading everything into memory. Vocabularies are kept in RAM for quick lookups, while posting lists are read on demand.
*   🏆 **Modern Ranking (BM25):** Forget simple keyword counts. `looseene` uses the industry-standard BM25 algorithm to rank results by relevance, considering term frequency (TF), inverse document frequency (IDF), and document length.
*   ✨ **Result Highlighting:** Automatically generates highlighted snippets from your documents, showing users exactly where their query matched.
*   🗑️ **Manual Compaction:** Includes a `compact_index()` function to merge segments, reclaim disk space from deleted/updated documents, and keep searches fast over time.
*   🐍 **Pure Python, Zero Dependencies:** Just one file. No complex setup, no external services.

### Advanced Usage

#### Document Updates and Deletions
`looseene` supports the full CRUD lifecycle.
```python
from looseene import update_document, delete_document

# Update a document by providing its full data with the same ID.
update_document('my_docs', {'id': 2, 'content': 'A proactive developer creates a great search engine.'})

# Delete a document by its ID.
delete_document('my_docs', 1)
```

#### Compaction
Over time, your index directory will accumulate segment files. Compaction merges them into a single, optimized segment, removing deleted data and speeding up searches. It's recommended to run this periodically as part of a maintenance task.

```python
from looseene import compact_index

# This can take some time on large indexes.
print("Starting compaction...")
compact_index('my_docs')
print("Compaction finished.")
```

### Schema and Data Types
The `schema` dictionary defines the structure of your documents.
*   **Primary Key:** The primary key field **must be named `id`** and its type must be `int`. This is a current limitation for simplicity.
*   **Indexed Fields:** All fields with type `str` will be tokenized and indexed for full-text search.
*   **Other Types:** Other standard Python types (`int`, `float`, `bool`, etc.) are stored but not indexed. You cannot search on them directly.

### Performance Characteristics
`looseene` is designed for performance on a single machine. Benchmarks on consumer hardware (e.g., a modern SSD and CPU) show:
*   **Indexing Speed:** Can index **3,000+ documents in under 0.1 seconds**.
*   **Search Latency:** Typical queries return results in **under 1 millisecond** on a moderately sized index (thousands of documents).

Performance depends on document size, but the LSM architecture ensures that write performance remains high even as the index grows.

### When *Not* to Use `looseene`
Honesty is the best policy. `looseene` is a powerful tool, but it's not a silver bullet. You should consider more robust solutions like **Elasticsearch** or **Meilisearch** if you need:
*   **Distributed Search:** `looseene` runs on a single node and cannot be clustered.
*   **Terabyte-Scale Data:** While it handles data larger than RAM, it's not optimized for massive, TB-scale indexes.
*   **Real-Time, Sub-Millisecond Indexing:** Indexing is fast, but it's not real-time. There's a delay until `save_index()` is called.
*   **Complex Queries:** No support for geographical queries, faceted search, or complex aggregations.
*   **Fine-grained Security:** No built-in access control or user management.

### API Reference
Here is a summary of the public API:

```python
# --- Index Management ---
create_index(name: str, schema: Dict, path: Optional[str] = None) -> None
save_index(name: str) -> None
compact_index(name: str) -> None

# --- Document Operations ---
add_to_index(name: str, data: Dict) -> None
update_document(name: str, data: Dict) -> None
delete_document(name: str, doc_id: int) -> None

# --- Searching ---
search_text(name: str, query: str) -> Generator[Dict, None, None]
highlight_result(doc: Dict, field: str, query: str, window: int = 60) -> str
```

### Thread Safety
`looseene` is **thread-safe** for common use cases.
*   You can safely have multiple threads reading (searching) from an index concurrently.
*   You can safely have one thread writing (`add`, `update`, `delete`) while other threads are reading.
*   Writing from multiple threads simultaneously is also safe, as write operations are protected by a lock.

### Running Tests
The library includes a comprehensive test suite using Python's standard `unittest` library. The tests cover indexing, search correctness, BM25 ranking, document updates, deletions, segment flushing, and compaction logic.

To run the tests, navigate to the project's root directory and execute:
```bash
python -m unittest tests/test_engine.py
```

### Contributing
Contributions are welcome! Please feel free to submit issues or pull requests. For major changes, please open an issue first to discuss what you would like to change.

### License
This project is licensed under the MIT License - see the `LICENSE` file for details.
