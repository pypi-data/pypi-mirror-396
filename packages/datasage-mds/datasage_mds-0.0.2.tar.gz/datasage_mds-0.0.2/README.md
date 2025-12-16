# DataSage 🧙‍♂️
PyPI: https://pypi.org/project/datasage-mds/

A lightweight, modular Python package for building Retrieval-Augmented Generation (RAG) systems. DataSage enables you to query your documents using natural language by combining semantic search with large language models (LLMs).

## 🌟 Features

- **Document Ingestion**: Support for multiple file formats (CSV, XLSX, PDF, TXT).
- **Efficient Chunking**: Configurable text splitting with overlap for context preservation.
- **Vector Storage**: ChromaDB-backed vector database for efficient similarity search.
- **Semantic Search**: HuggingFace embeddings for accurate document retrieval.
- **LLM Integration**: Local LLM support via Ollama for answer generation.
- **Modular Architecture**: Easy to extend and customize components.

## 🏗️ Architecture

```
DataSage
├── Ingestion Layer     → Load and chunk documents
├── Indexing Layer      → Embed and store in vector database
├── Query Layer         → Retrieve relevant context and generate answers
└── RAG Pipeline        → End-to-end question answering system
```

## 📋 Prerequisites

- Python 3.10 or higher
- [Ollama](https://ollama.com/download) (for local LLM inference)

## 🚀 Installation

### 1. Install from PyPI (recommended)
Package is published on PyPI:  
https://pypi.org/project/datasage-mds/

```bash
pip install datasage-mds



### 2. Install Ollama

Download and install Ollama from [ollama.com](https://ollama.com/download). 

Once installed, in a separate terminal do the following:

Pull a model:
```bash
ollama pull llama3.1
```

Verify installation:
```bash
ollama run llama3.1
```

### Supported File Formats

- **CSV**: Loaded with metadata for each row
- **PDF**: Extracted page by page
- **TXT**: Loaded as single document
- **XLSX**: Extracted sheet by sheet

## 🎯 Use Cases

- **Document Q&A**: Query large documents using natural language
- **Knowledge Base Search**: Build searchable knowledge bases
- **Customer Support**: Answer questions from documentation
- **Research Assistant**: Extract information from academic papers
- **Code Documentation**: Query codebases and technical docs


## Contributors

### Yihang Wang
- Sub-package: ingestion
- Modules: loaders.py, chunker.py

### Aaron Sukare
- Sub-package: indexing
- Modules: embedder.py, vector_store.py, index_engine.py

### Zaed Khan
- Sub-package: retrieval
- Modules: rag_engine/__init__.py, generator.py, retriever.py, data_models.py


## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🙏 Acknowledgments

- Built with [LangChain](https://langchain.com/)
- Embeddings powered by [HuggingFace](https://huggingface.co/)
- Vector storage by [ChromaDB](https://www.trychroma.com/)
- Local LLM inference via [Ollama](https://ollama.com/)

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Made with ❤️ by the DataSage Team**

```
datasage_data533_step_3
├─ .DS_Store
├─ coverage.json
├─ datasage_store
│  └─ chroma.sqlite3
├─ main.py
├─ project_description.pdf
├─ rag_engine
│  ├─ .DS_Store
│  ├─ indexing
│  │  ├─ embedder.py
│  │  ├─ indexing_documentation_updated.md
│  │  ├─ index_engine.py
│  │  ├─ testing_readme.md
│  │  └─ vector_store.py
│  ├─ ingestion
│  │  ├─ chunker.py
│  │  ├─ coverage_ingestion
│  │  │  ├─ coveragehtml_ingestion.png
│  │  │  └─ coverage_ingestion.png
│  │  ├─ documentation.md
│  │  ├─ loaders.py
│  │  ├─ README.md
│  │  └─ __init__.py
│  ├─ retrieval
│  │  ├─ data_models.py
│  │  ├─ documentation.md
│  │  ├─ generator.py
│  │  ├─ README.md
│  │  ├─ retriever.py
│  │  └─ __init__.py
│  ├─ tests
│  │  ├─ coverage_report.png
│  │  ├─ test_csv_loader.py
│  │  ├─ test_data_models.py
│  │  ├─ test_embedder.py
│  │  ├─ test_generator.py
│  │  ├─ test_index_engine.py
│  │  ├─ test_pdf_loader.py
│  │  ├─ test_retriever.py
│  │  ├─ test_text_chunker.py
│  │  ├─ test_txt_loader.py
│  │  ├─ test_vector_store.py
│  │  └─ __init__.py
│  ├─ rag_engine.py  
│  └─ __init__.py
├─ README.md
├─ pyproject.toml
├─ requirements.txt
├─ search_test.txt
├─ test_data.csv
└─ utils_test.txt

```