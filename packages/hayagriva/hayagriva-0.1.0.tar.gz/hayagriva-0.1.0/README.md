# Hayagriva
Illuminate what was forgotten. Retrieve what matters.

Hayagriva is a lightweight, modular Retrieval-Augmented Generation (RAG) framework designed to help developers build production-ready AI systems that combine large language models with real-world contextual knowledge. Inspired by Hayagriva, the divine preserver and restorer of the Vedas, this library focuses on retrieving truth from stored knowledge and generating accurate, grounded responses.

## Features
- Pluggable retrievers (vector databases, keyword search, hybrid search)
- Model-agnostic generation (choose any LLM backend)
- Flexible embeddings and rerankers
- Built-in document loaders and chunking utilities
- Minimal and extensible architecture
- Easy integration with existing pipelines
- Lightweight and fast
- Basic CLI and Gradio UI for experimentation

## Project Structure
```
hayagriva/
├── core/           # Core RAG building blocks (chunker, embeddings, vector store, retriever, generator)
├── ingestion/      # Loaders and parsers for documents
├── ui/             # Gradio UI components
├── cli/            # Command line interface
├── utils/          # Utilities for logging, validation, etc.
├── config.py       # Configuration dataclasses
├── exceptions.py   # Custom exception types
└── version.py      # Version metadata
```

## Quick Start
### Python API
```python
from hayagriva import Hayagriva, HayagrivaConfig

config = HayagrivaConfig()  # customize models or retrieval parameters if needed
rag = Hayagriva(config)
rag.add_documents(["Hayagriva restores forgotten knowledge."])
response = rag.ask("Who retrieved the lost Vedas?")
print(response)
```

### CLI
```
# Launch the Gradio UI
hayagriva ui --port 7878

# Ingest local text files
hayagriva ingest ./docs

# Ask a question from the terminal
hayagriva query "Explain retrieval-augmented generation"
```

### Gradio UI
Running `hayagriva ui` starts a simple two-panel UI: left for ingestion, right for chat-based Q&A. It is a placeholder designed for future expansion.

## Minimum Requirements
- Python 3.10+
- Dependencies: `sentence-transformers`, `faiss-cpu`, `openai>=1.0.0`, `gradio`

Set `OPENAI_API_KEY` in your environment or configure it programmatically when instantiating `Hayagriva`.

### Installation
Install the package and dependencies in a Python 3.10+ environment:

```
pip install -e .
```

Ensure you have system build tools available for `faiss-cpu` (the default vector store) and that `OPENAI_API_KEY` is set before running generation.

## Roadmap
- Built-in document ingestion for PDFs, DOCX, JSON
- Streaming responses and multi-turn chat memory
- Additional vector stores (Chroma, Qdrant, Pinecone, Milvus)
- Hybrid retrieval and reranking
- Rich UI controls and analytics
- Agentic tool-use within the pipeline

## License
MIT License
