# ✨ The Enchanted Library & Book Intelligence

A high-performance Retrieval-Augmented Generation (RAG) system and literary AI chatbot. Upload any book in **any format (PDF, EPUB, DOCX, TXT, Markdown, HTML)** to instantly generate structured book overviews, executive synopses, character breakdowns, and interactive grounded Q&A — or explore 8 timeless pre-indexed canonical masterworks in the Pinecone cloud archive.

---

## 🌟 Key Features

### 1. 📖 Universal Multi-Format Book Upload
- **Supported Formats**: PDF (`.pdf`), EPUB (`.epub`), Microsoft Word (`.docx`, `.doc`), Plain Text (`.txt`), Markdown (`.md`), and Web Books (`.html`, `.htm`).
- **Instant In-Memory Indexing**: Local ONNX embeddings via FastEmbed (`BAAI/bge-small-en-v1.5`) and vectorized cosine similarity search without requiring cloud vector uploads.
- **Reading Metrics**: Automatic computation of total word count, page/section count, and estimated reading time.

### 2. 📑 Automated Deep Book Overview & Intelligence
Upon uploading any book, the AI generates a comprehensive literary analysis:
- **Executive Synopsis**: Core premise, central conflict, and narrative/argument progression.
- **Key Characters & Figures**: Major figures, motivations, alliances, and character arcs.
- **Core Themes & Motifs**: Exploration of philosophical and structural motifs.
- **Narrative Arc & Structure**: Turning points, climax, and resolution.
- **Key Takeaways**: Notable quotes and practical or literary lessons.
- **Export**: One-click download of the complete analysis report in Markdown.

### 3. 💬 Grounded Book Q&A Chatbot
- Ask any question about your uploaded book (characters, plot, specific scenes, symbolism).
- **Conversational Memory**: Automatically reformulates follow-up questions with full dialog context.
- **Verbatim Citations**: Expandable source viewer showing exact passages retrieved, page/section numbers, and similarity scores.
- **Quick Starter Pills**: 1-click suggested prompts for immediate insights.

### 4. 🏛️ The Classic Library Archive (Pinecone)
- Pre-indexed archive of 13,000+ vector chunks across 8 canonical masterworks:
  1. *Pride and Prejudice* (Jane Austen)
  2. *Frankenstein* (Mary Shelley)
  3. *Little Women* (Louisa May Alcott)
  4. *Crime and Punishment* (Fyodor Dostoevsky)
  5. *The Mahabharata* (Vyasa)
  6. *Bhagavad Gita*
  7. *Sense and Sensibility* (Jane Austen)
  8. *The Yoga-Vasishtha Maharamayana* (Valmiki)

---

## 🛠️ Tech Stack

| Purpose | Technology |
|---|---|
| **UI Framework** | Streamlit (Custom Luxury Dark Fantasy Theme) |
| **LLM Inference** | Groq (`openai/gpt-oss-120b`, `openai/gpt-oss-20b`, `qwen/qwen3.8-27b`) |
| **Embeddings** | `fastembed` (ONNX Runtime, `BAAI/bge-small-en-v1.5`, 384-dim) |
| **Classic Vector Store** | Pinecone Serverless |
| **Custom Vector Store** | In-Memory Normalized Numpy Cosine-Similarity Engine |
| **Document Parsers** | `pypdf`, `python-docx`, `beautifulsoup4`, `zipfile` |
| **Orchestration** | LangChain Core & Community |

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+
- A free Groq API key from [Groq Console](https://console.groq.com)
- *(Optional for Classic Archive)* Pinecone API key from [Pinecone Console](https://app.pinecone.io)

### 2. Setup Environment
```bash
# Clone the repository
git clone <repository_url>
cd book-ai-chatbot-main

# Install dependencies
pip install -r requirements.txt

# Create .env from .env.example
cp .env.example .env
```

Add your API keys to `.env`:
```env
GROQ_API_KEY=your_groq_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
```

### 3. Launch the Application
```bash
# On Windows PowerShell:
.\run.ps1

# Or with Streamlit directly:
streamlit run app.py
```

---

## 📚 Ingestion Pipeline (For Classic Tomes)
To re-ingest or add new books to your Pinecone index:
```bash
python ingest.py
```
This script downloads books from Project Gutenberg, chunks them with `RecursiveCharacterTextSplitter`, creates vector embeddings with FastEmbed, and upserts them to Pinecone.

