
<h1 align="center">Prompt Amplifier</h1>

<!-- Center-align the logo and set its size -->
<p align="center">
  <img src="https://github.com/user-attachments/assets/969c98f9-364c-4db7-a13a-9d8777a6686f" alt="Prompt Amplifier Logo" width="400" height="200"/>
</p>

**Transform short prompts into detailed, structured instructions using context-aware retrieval.**

[![PyPI version](https://badge.fury.io/py/prompt-amplifier.svg)](https://pypi.org/project/prompt-amplifier/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

---

## 🎯 What is Prompt Amplifier?

Prompt Amplifier is a library for **Prompt Amplification** — the process of transforming short, ambiguous user intents into comprehensive, well-structured prompts that LLMs can execute effectively.

```python
from prompt_amplifier import PromptForge

forge = PromptForge()
forge.load_documents("./company_docs/")

# Short, vague input
short_prompt = "How's the deal going?"

# Detailed, structured output
detailed = forge.expand(short_prompt)
```

**Before (user input):**
> "How's the deal going?"

**After (expanded prompt):**
> "Generate a Deal Health Assessment report with the following structure:
> 
> **1. Executive Summary** - Overall health status (Healthy/Warning/Critical)
> 
> **2. Key Metrics Table**
> | Metric | Current | Target | Status |
> |--------|---------|--------|--------|
> | Winscore | ... | ... | ... |
> | POC Progress | ... | ... | ... |
> 
> **3. Risk Factors** - List blocking issues from Success Plan
> 
> **4. Recommended Actions** - Prioritized next steps
> 
> Use data from: Deal Profile, Success Plan, Activity Log..."

---

## ✨ Features

- 📄 **Multi-format Document Loading** — PDF, DOCX, Excel, CSV, TXT, Markdown, HTML
- 🔢 **Pluggable Embedders** — TF-IDF, BM25, Sentence Transformers, OpenAI, Cohere, Google
- 💾 **Vector Store Support** — In-memory, ChromaDB, FAISS, Pinecone, Qdrant, Weaviate
- 🔍 **Smart Retrieval** — Vector search, hybrid (BM25 + Vector), reranking
- 🤖 **LLM Backends** — OpenAI, Anthropic, Google Gemini, Ollama (local)
- 📋 **Domain Schemas** — Define field structures for your domain
- 🔌 **Extensible** — Easy to add custom loaders, embedders, and vector stores

---

## 🚀 Quick Start

### Installation

```bash
# Core library
pip install prompt-amplifier

# With common extras
pip install prompt-amplifier[loaders,embeddings-local,vectorstore-chroma]

# Everything
pip install prompt-amplifier[all]
```

### API Key Setup

> ⚠️ **Required for `expand()`**: The prompt expansion feature requires an LLM API key.

```python
import os

# Option 1: Google Gemini (has free tier!)
os.environ["GOOGLE_API_KEY"] = "your-key-from-aistudio.google.com"

# Option 2: OpenAI
os.environ["OPENAI_API_KEY"] = "sk-your-key"

# Option 3: Anthropic
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-your-key"
```

### Basic Usage

```python
import os
os.environ["GOOGLE_API_KEY"] = "your-key"  # Required for expand()

from prompt_amplifier import PromptForge
from prompt_amplifier.generators import GoogleGenerator

# Initialize with Google Gemini (free tier available)
forge = PromptForge(generator=GoogleGenerator())

# Add your documents
forge.add_texts([
    "POC Health: Healthy means all milestones on track.",
    "Winscore ranges from 0-100, measuring deal probability.",
])

# Expand a short prompt
result = forge.expand("Give me a POC health check")

print(result.prompt)      # The expanded prompt
print(result.expansion_ratio)  # How much longer it got
```

### Search Without API Key

```python
from prompt_amplifier import PromptForge

# No API key needed for search!
forge = PromptForge()
forge.add_texts(["doc1", "doc2", "doc3"])

# Search works without LLM
results = forge.search("my query")
for r in results.results:
    print(r.chunk.content)
```

### With Persistent Vector Store

```python
from prompt_amplifier import PromptForge
from prompt_amplifier.vectorstores import ChromaStore
from prompt_amplifier.embedders import SentenceTransformerEmbedder

forge = PromptForge(
    embedder=SentenceTransformerEmbedder("all-MiniLM-L6-v2"),
    vectorstore=ChromaStore(
        collection_name="my_docs",
        persist_directory="./chroma_db"
    )
)

# First run: embeds and stores
forge.load_documents("./docs/")

# Subsequent runs: uses existing embeddings
result = forge.expand("Summarize the project status")
```

### With Cloud Vector Store (Pinecone)

```python
from prompt_amplifier import PromptForge
from prompt_amplifier.vectorstores import PineconeStore
from prompt_amplifier.embedders import OpenAIEmbedder

forge = PromptForge(
    embedder=OpenAIEmbedder(model="text-embedding-3-small"),
    vectorstore=PineconeStore(
        api_key="your-api-key",
        index_name="prompt-amplifier-prod"
    ),
    generator="gpt-4o"
)
```

---

## 📖 Documentation

- [Getting Started](https://prompt-amplifier.readthedocs.io/getting-started)
- [API Reference](https://prompt-amplifier.readthedocs.io/api-reference)
- [Tutorials](https://prompt-amplifier.readthedocs.io/tutorials)
- [Research Paper](https://prompt-amplifier.readthedocs.io/research)

---

## 🧩 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Prompt Amplifier                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   Documents    →   Chunker   →   Embedder   →   VectorStore │
│   (PDF, DOCX)      (split)       (encode)       (persist)   │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   User Query   →   Embedder  →   Retriever  →   Generator   │
│   "short"          (encode)      (search)       (expand)    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔌 Supported Integrations

### Document Loaders
| Format | Loader |
|--------|--------|
| PDF | `PDFLoader` |
| Word | `DocxLoader` |
| Excel | `ExcelLoader` |
| CSV | `CSVLoader` |
| Text | `TxtLoader` |
| Markdown | `MarkdownLoader` |
| HTML | `HTMLLoader` |
| JSON | `JSONLoader` |

### Embedders
| Provider | Class | Type |
|----------|-------|------|
| TF-IDF | `TFIDFEmbedder` | Free, Local |
| BM25 | `BM25Embedder` | Free, Local |
| Sentence Transformers | `SentenceTransformerEmbedder` | Free, Local |
| OpenAI | `OpenAIEmbedder` | Paid API |
| Cohere | `CohereEmbedder` | Paid API |
| Google | `GoogleEmbedder` | Paid API |
| Voyage AI | `VoyageEmbedder` | Paid API |

### Vector Stores
| Store | Class | Type |
|-------|-------|------|
| In-Memory | `MemoryStore` | Local |
| ChromaDB | `ChromaStore` | Local |
| FAISS | `FAISSStore` | Local |
| LanceDB | `LanceDBStore` | Local |
| Pinecone | `PineconeStore` | Cloud |
| Qdrant | `QdrantStore` | Local/Cloud |
| Weaviate | `WeaviateStore` | Cloud |
| pgvector | `PGVectorStore` | Self-host |

### LLM Generators
| Provider | Class |
|----------|-------|
| OpenAI | `OpenAIGenerator` |
| Anthropic | `AnthropicGenerator` |
| Google Gemini | `GoogleGenerator` |
| Ollama | `OllamaGenerator` |
| HuggingFace | `HuggingFaceGenerator` |

---

## 🧪 Research

Prompt Amplifier was developed as part of research into **Prompt Amplification** — systematically transforming short user intents into detailed, structured prompts.

Key contributions:
- Formalization of the prompt expansion problem
- Comparison of embedding strategies for prompt enhancement
- Evaluation metrics for prompt quality
- Benchmark datasets across multiple domains

📄 **Paper**: [Coming Soon]

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
# Clone the repo
git clone https://github.com/DeccanX/Prompt-Amplifier.git
cd Prompt-Amplifier

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check src/
black src/
```

---

## 📜 License

Apache 2.0 — See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Built with inspiration from:
- [LangChain](https://github.com/langchain-ai/langchain)
- [LlamaIndex](https://github.com/run-llama/llama_index)
- [ChromaDB](https://github.com/chroma-core/chroma)

---

**Made with ❤️ by Rajesh More for the AI community**
