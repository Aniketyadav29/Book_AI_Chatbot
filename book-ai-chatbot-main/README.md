<div align="center">

<!-- 3D Holographic Animated Header Banner -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=0,2,10,25&height=280&section=header&text=🏛️%20The%20Ancient%20Heritage%20Library&fontSize=42&fontColor=fff&animation=twinkling&fontAlignY=38&desc=Universal%20Multi-Format%20Book%20Intelligence%20•%20Neural%20Vector%20RAG%20•%20Groq%20LPU&descFontSize=18&descAlignY=62&descAlign=50" alt="Ancient Heritage Library Banner" width="100%"/>
</p>

### 🌌 *Step into an Ancient Sanctuary of Knowledge Powered by Next-Gen Neural AI*

<p align="center">
  <a href="https://book-ai-chatbot.streamlit.app"><img src="https://img.shields.io/badge/🚀_Live_Demo-Streamlit_Cloud-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit App Live Demo"/></a>
  <a href="https://streamlit.io"><img src="https://img.shields.io/badge/Streamlit-1.36.0-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit"/></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/></a>
  <a href="https://groq.com"><img src="https://img.shields.io/badge/Groq_LPU-Ultra_Fast_Inference-F55036?style=for-the-badge&logo=groq&logoColor=white" alt="Groq"/></a>
  <a href="https://pinecone.io"><img src="https://img.shields.io/badge/Pinecone-Serverless_Vector_DB-000000?style=for-the-badge&logo=pinecone&logoColor=white" alt="Pinecone"/></a>
  <a href="https://qdrant.github.io/fastembed/"><img src="https://img.shields.io/badge/FastEmbed-Local_ONNX_384d-4B8BBE?style=for-the-badge" alt="FastEmbed"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-F59E0B?style=for-the-badge" alt="License"/></a>
</p>

<p align="center">
  <a href="https://book-ai-chatbot.streamlit.app"><b>🌟 Open Streamlit App</b></a> •
  <a href="#-overview">Overview</a> •
  <a href="#-key-capabilities">Key Features</a> •
  <a href="#-3d-architecture-pipeline">Architecture</a> •
  <a href="#-supported-manuscript-formats">Formats</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-author--connect">Author</a>
</p>

<img src="https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif" width="100%"/>

</div>

---

## 📖 Overview

**The Ancient Heritage Library & Book Intelligence** is an enterprise-grade Retrieval-Augmented Generation (RAG) ecosystem. It unites timeless historical manuscripts and contemporary literature with cutting-edge **Groq LPU Inference**, **FastEmbed ONNX Embeddings**, and an **in-memory normalized vector search engine**.

Upload any document in **any format (PDF, EPUB, DOCX, TXT, Markdown, HTML)** to instantly unlock:
- 📑 **Comprehensive Literary Overviews** (Executive synopsis, core themes, key figures, narrative arc, takeaways).
- 💬 **Grounded Conversational Q&A** with verbatim citations, page tracking, and zero hallucination risk.
- 🏛️ **Timeless Classics Archive** pre-indexed across 13,000+ vector chunks in Pinecone Serverless.

---

## 🌟 Key Capabilities

<table>
  <tr>
    <td width="50%" valign="top">
      <div align="center">
        <h3>📤 Universal Multi-Format Upload</h3>
      </div>
      <ul>
        <li><b>PDF, EPUB, DOCX, TXT, MD, HTML</b> — Native client-side parsing without requiring third-party cloud uploads.</li>
        <li><b>Reading Metrics Engine</b>: Instant calculation of total word count, section/page count, and estimated reading time.</li>
        <li><b>Fast ONNX Embeddings</b>: Local vector generation using <code>BAAI/bge-small-en-v1.5</code>.</li>
      </ul>
    </td>
    <td width="50%" valign="top">
      <div align="center">
        <h3>📑 Automated Deep Book Analysis</h3>
      </div>
      <ul>
        <li><b>Executive Synopsis</b>: Core premise, central conflict, and thematic resolution.</li>
        <li><b>Key Figures & Dynamics</b>: Motivations, character arcs, and roles.</li>
        <li><b>Structural Narrative Map</b>: Critical turning points & literary takeaways.</li>
        <li><b>1-Click Export</b>: Download full analysis reports in clean Markdown.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <div align="center">
        <h3>💬 Grounded Q&A with Citations</h3>
      </div>
      <ul>
        <li><b>Conversational Query Rewriter</b>: Resolves follow-up pronouns (he, she, it) in multi-turn dialogues.</li>
        <li><b>Transparent Citations</b>: Expandable cards displaying exact manuscript passages and relevance scores.</li>
        <li><b>Starter Question Pills</b>: 1-click prompts for immediate narrative insights.</li>
      </ul>
    </td>
    <td width="50%" valign="top">
      <div align="center">
        <h3>🏛️ Pre-Indexed Classics Cloud Archive</h3>
      </div>
      <ul>
        <li><b>13,000+ Pre-Indexed Vectors</b> across 8 timeless masterworks in Pinecone.</li>
        <li><b>Dual-Mode Architecture</b>: Seamlessly switch between custom uploaded books and canonical classics.</li>
        <li><b>Sub-Second Retrieval</b>: Powered by Pinecone Serverless on AWS.</li>
      </ul>
    </td>
  </tr>
</table>

---

## 🌌 3D Architecture Pipeline

```mermaid
flowchart TD
    %% Styling Configuration
    classDef inputStyle fill:#2d1d12,stroke:#d4af37,stroke-width:2px,color:#fff;
    classDef processStyle fill:#1a281e,stroke:#52b788,stroke-width:2px,color:#fff;
    classDef vectorStyle fill:#16222f,stroke:#4895ef,stroke-width:2px,color:#fff;
    classDef outputStyle fill:#2c1b2d,stroke:#f72585,stroke-width:2px,color:#fff;

    subgraph INGESTION ["📥 1. Universal Document Ingestion"]
        A["📄 Document / Manuscript<br/>(PDF, EPUB, DOCX, TXT, HTML)"]:::inputStyle --> B{"Format Classifier"}:::inputStyle
        B -->|PDF| C1["pypdf Page Extractor"]:::processStyle
        B -->|EPUB| C2["zipfile + BeautifulSoup"]:::processStyle
        B -->|DOCX| C3["python-docx Structure"]:::processStyle
        B -->|TXT/MD| C4["Multi-Encoding Auto-Decode"]:::processStyle
        B -->|HTML| C5["DOM Script/Style Stripper"]:::processStyle
    end

    subgraph VECTOR ["⚡ 2. Local Neural Embedding & In-Memory Index"]
        C1 & C2 & C3 & C4 & C5 --> D["RecursiveCharacterTextSplitter<br/>(900-char chunks, 150-char overlap)"]:::processStyle
        D --> E["FastEmbed ONNX<br/>(BAAI/bge-small-en-v1.5)"]:::vectorStyle
        E --> F[("In-Memory Normalized<br/>Cosine Similarity Matrix")]:::vectorStyle
    end

    subgraph ARCHIVE ["🏛️ 3. Pinecone Cloud Archive"]
        Z["8 Canonical Masterworks<br/>(13,000+ Vectors)"]:::vectorStyle --> Y[("Pinecone Serverless Index<br/>'enchanted-library'")]:::vectorStyle
    end

    subgraph RAG ["🧠 4. Conversational RAG & Groq LPU Inference"]
        Q["User Query / Follow-up"]:::inputStyle --> R["Contextual Query Rewriter"]:::processStyle
        R --> S["Vector Search Engine"]:::vectorStyle
        F -.-> S
        Y -.-> S
        S --> T["Top-K Passage Excerpts"]:::processStyle
        T & Q --> U["Groq LPU Synthesis<br/>(openai/gpt-oss-120b)"]:::outputStyle
        U --> V["✨ Grounded Answer + Source Citations + Analysis Report"]:::outputStyle
    end
```

---

## 📚 Supported Manuscript Formats

<div align="center">

| Format | Extension | Extraction Engine | Capabilities |
| :--- | :---: | :---: | :--- |
| **Portable Document** | `.pdf` | `pypdf.PdfReader` | Page-by-page text parsing with exact page metadata |
| **Electronic Publication** | `.epub` | `zipfile` + `BeautifulSoup` | Chapter-order XML/XHTML extraction |
| **Microsoft Word** | `.docx`, `.doc` | `python-docx` | Paragraph & table content extraction |
| **Plain Text & Markdown** | `.txt`, `.md`, `.rst` | Multi-Encoding Decoder | UTF-8, UTF-8-SIG, Latin-1, CP1252 auto-detection |
| **Web Hypertext** | `.html`, `.htm` | `BeautifulSoup` | Clean semantic DOM parsing |

</div>

---

## 🏛️ Pre-Indexed Canonical Classics

The Pinecone Cloud archive includes full vector indexing for:

<div align="center">

| # | Masterwork | Author | Genre / Period |
| :-: | :--- | :--- | :--- |
| 1 | **Pride and Prejudice** | Jane Austen | Romantic Classic (1813) |
| 2 | **Frankenstein** | Mary Shelley | Gothic Science Fiction (1818) |
| 3 | **Little Women** | Louisa May Alcott | Coming-of-Age Fiction (1868) |
| 4 | **Crime and Punishment** | Fyodor Dostoevsky | Psychological Realism (1866) |
| 5 | **The Mahabharata** | Krishna-Dwaipayana Vyasa | Ancient Epic & Philosophy |
| 6 | **Bhagavad Gita** | Vyasa | Spiritual & Philosophical Classic |
| 7 | **Sense and Sensibility** | Jane Austen | Classic Literary Fiction (1811) |
| 8 | **The Yoga-Vasishtha Maharamayana** | Valmiki | Ancient Vedantic Discourse |

</div>

---

## 🛠️ Tech Stack & Dependencies

<p align="center">
  <img src="https://skillicons.dev/icons?i=python,pytorch,git,github,docker,vscode,markdown,html,css" />
</p>

- **Frontend & Visuals**: Streamlit (Ancient Heritage Stone & Gold Aesthetic) • [Live App on Streamlit Cloud](https://book-ai-chatbot.streamlit.app)
- **LLM Synthesis**: Groq LPU (`openai/gpt-oss-120b`, `openai/gpt-oss-20b`, `qwen/qwen3.8-27b`)
- **Embeddings**: `fastembed` ONNX Runtime (`BAAI/bge-small-en-v1.5`, 384 dimensions)
- **Vector Stores**: In-Memory Normalized Numpy Cosine Matrix & Pinecone Serverless
- **Orchestration**: LangChain Core & Community
- **Document Parsers**: `pypdf`, `python-docx`, `beautifulsoup4`, `zipfile`

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Aniketyadav29/Book_AI_Chatbot.git
cd Book_AI_Chatbot/book-ai-chatbot-main
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Credentials
Create a `.env` file in `book-ai-chatbot-main`:
```env
# Free Groq API key: https://console.groq.com
GROQ_API_KEY=gsk_your_groq_api_key_here

# Free Pinecone API key: https://app.pinecone.io
PINECONE_API_KEY=pcsk_your_pinecone_api_key_here
```

### 4. Launch the App
```bash
# Windows One-Click Launcher:
.\run.ps1

# Or with Streamlit directly:
python -m streamlit run app.py
```
Open **`http://localhost:8501`** in your browser.

---

## 🧪 Automated Verification Suite

Run full end-to-end tests across document extractors, in-memory vector similarity, Groq LLM synthesis, and Pinecone:

```bash
python test_verification.py
```

<details>
<summary><b>🔍 View Test Suite Output Preview</b></summary>

```text
============================================================
TEST 1: Multi-Format Document Extraction
============================================================
[OK] TXT Extraction passed! Characters: 205
[OK] HTML Extraction passed! Characters: 95
[OK] DOCX Extraction passed! Characters: 100
[OK] EPUB Extraction passed! Characters: 81
[OK] PDF Handler verified!

============================================================
TEST 2: In-Memory FastEmbed Vector Indexing & Search
============================================================
Query: 'Who translated the ancient glyphs?'
Top Match (Score: 0.767): Dr. Aris Thorne translated the ancient glyphs...
[OK] In-memory vector search passed!

============================================================
TEST 3: Groq LLM Book Overview & Grounded Q&A
============================================================
[OK] Book Overview generated successfully!
[OK] Grounded Q&A verified successfully!

============================================================
TEST 4: Pinecone Classic Library Archive Retriever
============================================================
Retrieved 3 docs from Pinecone 'enchanted-library'
[OK] Pinecone classic library retriever verified!

============================================================
[SUCCESS] ALL 4 TEST SUITES PASSED PERFECTLY!
============================================================
```
</details>

---

## 👤 Author & Connect

<div align="center">

### **Aniket Yadav**
*AI & Full-Stack Developer*

<a href="mailto:anikety7905@gmail.com"><img src="https://img.shields.io/badge/Email-anikety7905%40gmail.com-EA4335?style=for-the-badge&logo=gmail&logoColor=white" alt="Email"/></a>
<a href="https://github.com/Aniketyadav29"><img src="https://img.shields.io/badge/GitHub-Aniketyadav29-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub"/></a>
<a href="https://book-ai-chatbot.streamlit.app"><img src="https://img.shields.io/badge/Live_App-Streamlit_Cloud-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Live App"/></a>

---

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=0,2,10,25&height=120&section=footer" width="100%"/>
</p>

⭐ **Star this repository if you find it helpful!**

</div>
