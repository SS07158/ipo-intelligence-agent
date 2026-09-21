# Indian IPO Intelligence Agent

An evidence-grounded AI research assistant for Indian IPO research.

The system combines **structured IPO and financial data, SEBI/NSE offer documents, hybrid document retrieval, reranking, news intelligence, and an agentic tool-routing workflow** to answer IPO research questions with source-backed evidence.

> **Purpose:** Help users research and understand IPO information from available sources.
>
> **Important:** This project is a research and educational assistant. It does not provide personalized buy/sell recommendations or guarantee investment outcomes.

---

## Overview

Researching an IPO often requires moving between prospectuses, financial statements, exchange information, news articles, and different sections of long regulatory documents.

The Indian IPO Intelligence Agent brings these sources into a single research workflow.

Instead of sending every question through the same RAG pipeline, the system uses an **agentic workflow** to determine which tools are appropriate for the question.

For example:

| Question type        | Retrieval strategy                         |
| -------------------- | ------------------------------------------ |
| IPO facts            | Structured IPO lookup                      |
| Financial metrics    | Structured financial lookup                |
| Revenue calculations | Financial data + deterministic calculation |
| DRHP/RHP questions   | Document RAG                               |
| Risk questions       | Section-aware document retrieval           |
| Recent news          | News lookup                                |
| Complex questions    | Multiple tools + synthesis                 |

The result is an architecture that separates **structured data retrieval, document retrieval, deterministic calculations, and language-model synthesis**.

---

## Key Features

### Agentic Query Routing

A LangGraph-based agent determines which tools are required to answer a question.

Examples:

```text
"What is the fresh issue size?"
        ↓
IPO lookup
```

```text
"What was revenue from operations in FY2026?"
        ↓
Financial lookup
```

```text
"What are the major internal risks?"
        ↓
Document retrieval
        ↓
Risk-aware filtering
```

```text
"How has revenue changed and what risks could affect that growth?"
        ↓
Financial analysis
        +
Document retrieval
        ↓
Combined synthesis
```

The architecture also includes deterministic fallback routing for cases where the language model does not produce the expected tool calls.

---

### Evidence-Grounded Document RAG

IPO documents such as DRHP/RHP files are processed into searchable chunks.

Each chunk can retain metadata including:

* Company
* IPO ID
* Document ID
* Document type
* Source
* Page number
* Section
* Risk category
* Subsection
* Chunk index
* Document version

This metadata allows retrieval to be more precise than a basic vector-search-only RAG system.

---

### Hybrid Retrieval

The document retrieval pipeline combines multiple retrieval strategies:

```text
User Query
    ↓
Query Expansion
    ↓
 ┌───────────────────────┐
 │                       │
 ▼                       ▼
Dense Retrieval       BM25 Retrieval
 │                       │
 └───────────┬───────────┘
             ↓
    Reciprocal Rank Fusion
             ↓
         Reranking
             ↓
      Evidence Collection
```

The motivation is to combine the strengths of different retrieval methods:

**Dense retrieval** helps with semantic similarity.

**BM25** helps with exact terminology, financial language, legal wording, section names, and other lexical matches.

The resulting candidate rankings are combined using **Reciprocal Rank Fusion (RRF)** before reranking.

---

### Metadata-Aware Risk Retrieval

Risk questions require more than generic semantic similarity because IPO documents contain large amounts of financial and business information outside the actual risk-factor sections.

The retriever can dynamically resolve the relevant risk category using indexed metadata.

For example:

```text
SECTION II: RISK FACTORS
        ↓
INTERNAL RISK FACTORS
```

or:

```text
SECTION II: RISK FACTORS
        ↓
EXTERNAL RISK FACTORS
```

This approach avoids hardcoding a single IPO's document structure into the retrieval pipeline.

---

### Multi-IPO Retrieval Isolation

The system is designed to prevent evidence from one IPO from leaking into another company's retrieval results.

IPO identity is propagated through the ingestion and retrieval pipeline using metadata such as:

```text
ipo_id
document_id
company
document_type
```

This becomes especially important when the vector store contains documents from multiple companies.

---

### Citation Grounding

The system keeps retrieved evidence connected to document metadata such as:

```text
Company
Document
Document Type
Source
Page
Section
```

A citation-validation layer checks generated references against the evidence returned during retrieval.

The objective is to avoid unsupported references being presented as if they came from the retrieved documents.

---

### Financial Intelligence

Structured financial information is stored through the database layer and queried independently from document retrieval.

Supported metrics include information such as:

* Revenue from operations
* Adjusted EBITDA
* Profit / loss
* Operating cash flow

Deterministic financial calculations are handled by Python rather than delegated to the language model.

This allows calculations such as growth and percentage changes to remain reproducible.

---

### News Intelligence

The system includes RSS-based news ingestion and associates articles with IPO companies.

News records can contain:

```text
Headline
Source
Publication date
Topic
Sentiment
Article URL
```

This provides a separate news-data path instead of asking the document RAG system to answer questions about current events.

---

## Architecture

```text
                           ┌───────────────────┐
                           │    User Query     │
                           └─────────┬─────────┘
                                     │
                                     ▼
                           ┌───────────────────┐
                           │    LangGraph      │
                           │      Agent        │
                           └─────────┬─────────┘
                                     │
                    ┌────────────────┼─────────────────┐
                    │                │                 │
                    ▼                ▼                 ▼
             ┌────────────┐  ┌──────────────┐  ┌──────────────┐
             │ IPO Lookup │  │ Financial    │  │ Document RAG │
             │    Tool    │  │    Tool      │  │     Tool     │
             └────────────┘  └──────────────┘  └──────┬───────┘
                                                       │
                                      ┌────────────────┼────────────────┐
                                      │                │                │
                                      ▼                ▼                ▼
                                   Chroma            BM25           Reranker
                                      │                │                │
                                      └────────────────┼────────────────┘
                                                       │
                                                       ▼
                                              Evidence Collection
                                                       │
                                                       ▼
                                              Citation Validation
                                                       │
                                                       ▼
                                               Grounded Answer
```

---

## Data Pipeline

```text
             SEBI / NSE / Issuer Sources
                         │
                         ▼
                    Acquisition
                         │
                         ▼
                  PDF Extraction
                         │
                         ▼
                  Section Detection
                         │
                         ▼
                      Chunking
                         │
                         ▼
                Metadata Enrichment
                         │
                ┌────────┴────────┐
                │                 │
                ▼                 ▼
             Chroma              BM25
                │                 │
                └────────┬────────┘
                         ▼
                  Hybrid Retrieval
                         │
                         ▼
                     Reranking
                         │
                         ▼
                 Evidence Grounding
```

---

## Technology Stack

### Application

* Python
* FastAPI
* Streamlit
* SQLAlchemy
* SQLite

### Agent / LLM

* LangGraph
* LangChain
* Ollama
* Qwen3:8B

### Retrieval / NLP

* Sentence Transformers
* BGE-M3 embeddings
* ChromaDB
* BM25
* Reciprocal Rank Fusion
* Reranking

### Document Processing

* PyMuPDF
* PDF extraction
* Section detection
* Metadata-aware chunking

### Data Ingestion

* SEBI documents
* NSE document/data sources
* RSS news sources

### Infrastructure

* Docker
* Docker Compose
* Git
* GitHub

---

## Example Questions

The system can handle questions such as:

```text
What is the revenue of CULT.FIT LIMITED in FY2026?
```

```text
What are the major internal risks of Sterlite Electric Limited?
```

```text
How has CULT.FIT's adjusted EBITDA changed over the last three fiscal years?
```

```text
What are the latest available news developments about CULT.FIT LIMITED?
```

```text
What does the DRHP say about a specific business or risk factor?
```

The architecture also supports questions that require multiple tools and evidence sources.

---

## Example Research Flow

A question such as:

```text
How has CULT.FIT's revenue changed, and what risks could affect that growth?
```

can be decomposed into:

```text
User Question
      │
      ├───────────────┐
      ▼               ▼
Financial Tool    Document RAG
      │               │
      ▼               ▼
Revenue Data       Risk Evidence
      │               │
      └───────┬───────┘
              ▼
        Evidence Synthesis
              │
              ▼
       Grounded Response
```

This separation allows numerical analysis and document evidence to be handled by the components designed for each task.

---

## Engineering Challenges

### 1. Multi-IPO Retrieval Isolation

When multiple IPO documents are indexed, unrestricted retrieval can return evidence belonging to the wrong company.

The retrieval pipeline therefore propagates `ipo_id` and related document metadata so that evidence remains associated with the correct IPO.

---

### 2. Section-Aware Risk Retrieval

Generic semantic retrieval can return financially related text that appears outside the actual risk-factor section.

The retriever was enhanced to resolve the appropriate risk section and category using indexed metadata.

This improves retrieval specificity for questions such as:

```text
What are the major internal risks?
```

---

### 3. PDF Section Detection

IPO prospectuses are large, highly structured documents containing:

* Major sections
* Subsections
* Tables
* Legal language
* Formatting artifacts
* Repeated headings

The ingestion pipeline therefore separates document parsing, section detection, chunking, and metadata enrichment rather than treating the PDF as a plain text blob.

---

### 4. Hybrid Retrieval

Dense retrieval and lexical retrieval solve different retrieval problems.

Instead of choosing only one:

```text
Dense Search
```

or:

```text
BM25
```

the system combines both rankings using Reciprocal Rank Fusion and then applies reranking.

---

### 5. Citation Validation

A language model can generate plausible-looking references that were not actually present in the retrieved evidence.

The citation-validation layer checks references against the available evidence instead of trusting generated citations blindly.

---

### 6. Deterministic Financial Calculations

Language models are not used as calculators for deterministic financial metrics.

Calculations are handled in Python and the resulting values can then be incorporated into the final explanation.

This separates:

```text
Data
+
Calculation
+
Language generation
```

into distinct responsibilities.

---

## Project Structure

```text
ipo-intelligence-agent/
│
├── app/
│   ├── agents/
│   │   ├── company_resolver.py
│   │   ├── langgraph_agent.py
│   │   ├── router.py
│   │   ├── state.py
│   │   ├── synthesizer.py
│   │   └── tool_registry.py
│   │
│   ├── api/
│   │   ├── main.py
│   │   └── schemas.py
│   │
│   ├── frontend/
│   │   ├── components/
│   │   ├── styles/
│   │   ├── agent_client.py
│   │   ├── api_client.py
│   │   └── streamlit_app.py
│   │
│   ├── prompts/
│   │
│   ├── retrieval/
│   │   ├── bm25_store.py
│   │   ├── citation_validator.py
│   │   ├── embedding_service.py
│   │   ├── hybrid_retriever.py
│   │   ├── rag_service.py
│   │   ├── reranker.py
│   │   └── vector_store.py
│   │
│   └── tools/
│       ├── financial_analysis.py
│       ├── financial_calculator.py
│       ├── financial_tool.py
│       ├── ipo_tool.py
│       ├── news_tool.py
│       └── rag_tools.py
│
├── database/
│
├── ingestion/
│   ├── sebi/
│   ├── nse/
│   ├── news/
│   └── sentiment/
│
├── evaluation/
│
├── tests/
│
├── scripts/
│
├── Dockerfile
├── compose.yaml
├── requirements.txt
├── .dockerignore
├── .env.example
├── .gitignore
└── README.md
```

---

## Running Locally

### Prerequisites

Install:

* Python 3.12
* Git
* Ollama

Create and activate a virtual environment:

```bash
python -m venv venv
```

Windows:

```powershell
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Make sure Ollama is running and the configured model is available:

```bash
ollama pull qwen3:8b
```

Configure environment variables using:

```text
.env.example
```

Create your local `.env` file and add any required configuration.

### Start the API

```bash
uvicorn app.api.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Health check:

```text
http://127.0.0.1:8000/health
```

Swagger/OpenAPI:

```text
http://127.0.0.1:8000/docs
```

### Start the Streamlit frontend

In another terminal:

```bash
streamlit run app/frontend/streamlit_app.py
```

The frontend will normally be available at:

```text
http://127.0.0.1:8501
```

---

## Running with Docker

The project includes a Docker Compose setup containing separate API and frontend services.

Start the complete application:

```bash
docker compose up --build -d
```

Check service status:

```bash
docker compose ps
```

API:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

Streamlit:

```text
http://127.0.0.1:8501
```

Stop the services:

```bash
docker compose down
```

View logs:

```bash
docker compose logs --tail=100
```

### Docker Architecture

```text
                 Host Machine
                     │
          ┌──────────┴──────────┐
          │                     │
          ▼                     ▼
      API Container       Frontend Container
          │                     │
          │                     │
          ▼                     ▼
        Ollama  ◄──────────  Streamlit
          │
          ▼
      Agent / RAG
          │
     ┌────┴────┐
     ▼         ▼
  Chroma     SQLite
```

The Docker configuration also mounts persistent application data and the Hugging Face cache so that local model/data state does not need to be recreated unnecessarily.

---

## Evaluation

Evaluation is treated as part of the project rather than an afterthought.

The repository contains evaluation code covering areas such as:

### Retrieval

* Retrieval recall
* Retrieval precision
* MRR
* Hybrid retrieval checks
* Reranker evaluation

### Answer Quality

* Answer relevance
* Groundedness
* Citation support
* Citation correctness
* Failure analysis

### Agent Behaviour

* Tool selection
* Routing behaviour
* Multi-tool questions
* Failure cases

Evaluation datasets include factual, financial, risk, news, and retrieval-oriented questions.

> Metrics are intentionally not hardcoded into this README unless they have been measured and recorded for the current version of the system.

---

## Data Sources

The system is designed around authoritative and modular sources.

### Primary Documents

* SEBI public issue filings
* DRHP
* RHP
* Offer documents

### Exchange Data

* NSE
* BSE

### News

* RSS-based public news sources
* Modular news providers

The ingestion layer is designed so individual providers can be replaced without restructuring the core agent or retrieval architecture.

---

## Design Principles

### Evidence over hallucination

Important factual answers should be grounded in retrieved evidence.

### Structured data for structured questions

Exact financial and IPO facts are handled through structured tools rather than forcing the language model to infer values from arbitrary text.

### Deterministic calculations outside the LLM

Financial calculations are performed programmatically.

### Facts and opinions remain separate

Company facts, financial data, news, sentiment, and model-generated synthesis should not be presented as if they were the same type of evidence.

### Modular architecture

The project separates:

```text
Ingestion
Retrieval
Tools
Agent
API
Frontend
Evaluation
```

so individual components can evolve independently.

---

## Current Project Scope

The current implementation includes:

* [x] IPO structured data
* [x] Financial data retrieval
* [x] SEBI/NSE document ingestion
* [x] PDF parsing
* [x] Section-aware chunking
* [x] Multi-IPO document isolation
* [x] Chroma vector search
* [x] BM25 retrieval
* [x] Hybrid retrieval
* [x] Reciprocal Rank Fusion
* [x] Reranking
* [x] Agentic tool routing
* [x] Dynamic company resolution
* [x] Citation validation
* [x] News ingestion
* [x] News sentiment/topic analysis
* [x] FastAPI backend
* [x] Streamlit frontend
* [x] Docker / Docker Compose
* [x] Automated tests
* [x] Evaluation suite

---

## Limitations

This is an actively developed research system rather than a production financial-data platform.

Current limitations include:

* Coverage is dependent on the available source data and ingestion providers.
* News availability depends on the configured news providers.
* Local LLM inference requires sufficient local compute.
* Retrieval quality depends on document extraction, chunking, metadata, and ranking quality.
* The current database setup uses SQLite for local development.
* The BM25 index is rebuilt in memory rather than maintained as a persistent standalone index.
* Production deployment would require additional hardening around authentication, observability, scaling, secrets management, and external-service reliability.

---

## Future Work

Potential future improvements include:

* Expanded IPO coverage
* Additional exchange and issuer data sources
* Persistent production-grade retrieval infrastructure
* Improved ingestion scheduling and refresh workflows
* Larger retrieval and answer evaluation datasets
* More systematic retrieval benchmarking
* Additional risk categorization
* Improved news intelligence
* More advanced investor-discussion analysis
* PostgreSQL-based production persistence
* Production observability and monitoring
* Cloud deployment

---

## Why I Built This

A typical document chatbot follows:

```text
PDF → chunks → embeddings → vector database → LLM
```

This project explores a more realistic AI engineering architecture:

```text
User Query
    ↓
Agent
    ↓
Choose the appropriate tool(s)
    ↓
Structured Data / RAG / News
    ↓
Hybrid Retrieval + Reranking
    ↓
Evidence Validation
    ↓
Grounded Response
```

The goal was to build something closer to a **research system** than a simple chatbot while keeping the individual components understandable and testable.

---

## Disclaimer

This project is intended for research and educational purposes.

It retrieves, analyzes, and summarizes information from available sources. It is **not personalized financial advice**, does not provide guaranteed investment outcomes, and should not be interpreted as a recommendation to buy or sell any security.

Users should independently verify important information against the relevant primary sources and official filings.
