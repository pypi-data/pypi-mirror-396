# NeuroIndex 🧠

[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://www.python.org/)
[![PyPI version](https://img.shields.io/pypi/v/neuroindex)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

NeuroIndex is a hybrid **vector + semantic graph memory system** for embeddings.  
It provides:

- ✅ RAM-based LRU cache for fast lookups  
- ✅ FAISS vector search for large-scale similarity  
- ✅ Semantic graph traversal for relationship-aware queries  
- ✅ Persistent SQLite storage  

Perfect for AI document retrieval, chatbot memory, and semantic search workflows.

---

## Installation

```bash
git clone https://github.com/<your-username>/neuroindex.git
cd neuroindex
pip install -e .
