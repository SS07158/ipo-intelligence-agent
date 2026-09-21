Phase 0 — Architecture & Data Strategy
Status: In Progress

Initial dataset:
CULT.FIT LIMITED

Primary source:
SEBI public issue documents

Initial architecture:
Structured SQL + Document RAG

# Indian IPO Intelligence Agent

An evidence-grounded AI research assistant for Indian IPO research.

The system combines IPO structured data, financial metrics, SEBI/NSE IPO documents, news, hybrid retrieval, reranking, and an agentic workflow to answer research questions with source-backed evidence.

> **Purpose:** Help users research and understand IPO information from available sources.
> **The system does not provide buy/sell recommendations or guaranteed investment outcomes.**

## Features

### Agentic Query Routing

A LangGraph-based agent determines which tools are required for a question.

Examples:

* IPO facts → IPO lookup
* Financial questions → financial lookup
* DRHP/RHP questions → document RAG
* News questions → news lookup
* Complex questions → multiple tools can be combined

### Document RAG

IPO documents are processed into searchable chunks containing metadata such as:

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

The retrieval pipeline combines:

1. Query expansion
2. Dense vector retrieval
3. BM25 lexical retrieval
4. Reciprocal Rank Fusion
5. Reranking
6. Citation-aware answer generation

### Metadata-Aware Retrieval

The system supports IPO-level and document-level filtering.

For risk questions, the retriever can dynamically resolve:

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

without hardcoding a specific IPO's risk section into the retrieval pipeline.

### Citation Grounding

Answers contain evidence references linked to document metadata such as:

```text
Company
Document
Source
Page
Section
```

A citation validator checks generated references against the retrieved evidence.

### Financial Intelligence

Structured financial information is stored and queried through the database layer.

Supported metrics include items such as:

* Revenue from operations
* Adjusted EBITDA
* Profit / loss
* Operating cash flow

### News Intelligence

The system ingests public news through RSS-based providers and associates articles with IPO companies.

News records include:

* Headline
* Source
* Publication date
* Topic
* Sentiment
* Article URL

## Architecture

```text
                    ┌──────────────────────┐
                    │      User Query      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    LangGraph Agent   │
                    └──────────┬───────────┘
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
        ┌────────────┐ ┌──────────────┐ ┌──────────────┐
        │ IPO Tool   │ │ Financial    │ │ Document RAG │
        │            │ │ Tool         │ │              │
        └────────────┘ └──────────────┘ └──────┬───────┘
                                               │
                              ┌────────────────┼────────────────┐
                              ▼                ▼                ▼
                           Chroma            BM25          Reranker
                              │                │                │
                              └────────────────┼────────────────┘
                                               ▼
                                      Evidence Collection
                                               │
                                               ▼
                                      Citation Validation
                                               │
                                               ▼
                                        Grounded Answer
```

## Data Pipeline

```text
SEBI / NSE / Issuer Sources
          ↓
     Acquisition
          ↓
     PDF Extraction
          ↓
   Section Detection
          ↓
      Chunking
          ↓
    Metadata Enrichment
          ↓
      ┌───────┴───────┐
      ▼               ▼
   Chroma             BM25
      │               │
      └───────┬───────┘
              ▼
        Hybrid Retrieval
              ↓
          Reranking
              ↓
       Evidence Grounding
```

## Technology Stack

* Python
* PyTorch
* LangGraph / LangChain
* FastAPI
* Streamlit
* ChromaDB
* BM25
* Sentence-transformer embeddings
* SQLite
* SQLAlchemy
* RSS news ingestion
* Docker
* Git / GitHub

## Example Questions

```text
What are the major internal risks of Sterlite Electric Limited?

What is the revenue of CULT.FIT LIMITED in FY2026?

How has CULT.FIT's adjusted EBITDA changed over the last three fiscal years?

What are the latest available news developments about CULT.FIT LIMITED?

What does the DRHP say about a specific risk or business factor?
```

## Engineering Challenges

### Multi-IPO Retrieval Isolation

Initially, documents from different IPOs could be mixed during retrieval.

The system was updated to propagate and enforce `ipo_id` metadata throughout the retrieval pipeline.

### Section-Aware Risk Retrieval

Generic semantic retrieval could return financially related text outside the actual risk section.

The retriever was enhanced to dynamically resolve the relevant risk section and category using indexed metadata.

### PDF Section Detection

IPO documents contain complex headings, subsections, tables, and formatting artifacts.

The parser preserves major sections while separately tracking risk categories and subsections.

### Hybrid Retrieval

Dense retrieval provides semantic matching while BM25 provides lexical matching for exact terms and financial/legal language.

The two rankings are combined using Reciprocal Rank Fusion before reranking.

### Citation Validation

Generated citations are checked against the actual evidence returned to the language model instead of allowing unsupported references.

## Project Status

Core functionality implemented:

* [x] IPO structured data
* [x] Financial data retrieval
* [x] SEBI/NSE document ingestion
* [x] PDF parsing
* [x] Section-aware chunking
* [x] Multi-IPO document isolation
* [x] Chroma vector search
* [x] BM25 retrieval
* [x] Hybrid retrieval
* [x] Reranking
* [x] Agentic tool routing
* [x] Dynamic company resolution
* [x] Citation validation
* [x] News ingestion
* [x] News sentiment/topic analysis

## Disclaimer

This project is intended for research and educational purposes. It retrieves and summarizes information from available sources and should not be treated as personalized financial advice or a guaranteed investment recommendation.
