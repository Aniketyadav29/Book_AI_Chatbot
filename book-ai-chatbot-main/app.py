import os
import io
import re
import textwrap
import zipfile
import numpy as np
import streamlit as st
from typing import List, Dict, Any, Tuple
from bs4 import BeautifulSoup
import docx
from pypdf import PdfReader

from pathlib import Path

# ── Feature module imports ─────────────────────────────────────────────────────
try:
    import voice
except ImportError:
    voice = None
try:
    import multilingual
except ImportError:
    multilingual = None
try:
    import summarizer
except ImportError:
    summarizer = None
try:
    import knowledge
except ImportError:
    knowledge = None
try:
    import offline
except ImportError:
    offline = None
try:
    import profile
except ImportError:
    profile = None
try:
    import analytics
except ImportError:
    analytics = None

# Load .env file explicitly if present
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).resolve().parent / ".env"
    if env_file.exists():
        load_dotenv(dotenv_path=env_file, override=True)
    else:
        load_dotenv(override=True)
except ImportError:
    pass

# LangChain and FastEmbed imports
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.embeddings import Embeddings
from fastembed import TextEmbedding
from langchain_pinecone import PineconeVectorStore
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

# ── Streamlit Page Config ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="🏛️ The Ancient Heritage Library & Book Intelligence",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Ancient Cultural Heritage Homes & Architectural Aesthetics CSS ─────────────
ancient_theme_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@700&family=Cinzel:wght@400;600;700;900&family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

/* Main App Background: Ancient Cultural Courtyard & Stone Heritage Home */
.stApp {
    background: 
        linear-gradient(180deg, rgba(16, 12, 8, 0.88) 0%, rgba(12, 9, 6, 0.92) 50%, rgba(7, 5, 3, 0.97) 100%),
        url("https://images.unsplash.com/photo-1599827056326-802c67d16ee6?auto=format&fit=crop&w=2560&q=85") !important;
    background-size: cover !important;
    background-position: center center !important;
    background-attachment: fixed !important;
    background-repeat: no-repeat !important;
    color: #f3ecd8 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* Headings with Ancient Cultural Heritage Typography */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Cinzel', serif !important;
    color: #e5c98b !important;
    letter-spacing: 0.6px;
}

h1 {
    font-family: 'Cinzel Decorative', 'Cinzel', serif !important;
    color: #f5dfa3 !important;
    text-shadow: 0 0 25px rgba(229, 201, 139, 0.4), 2px 2px 8px rgba(0, 0, 0, 0.9);
    text-align: center;
    font-weight: 700;
}

/* Sidebar with Antique Rosewood & Brass Motif */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(20, 14, 10, 0.96) 0%, rgba(14, 10, 7, 0.98) 100%) !important;
    border-right: 1px solid rgba(212, 175, 55, 0.3) !important;
    backdrop-filter: blur(12px);
    box-shadow: 4px 0 20px rgba(0, 0, 0, 0.7);
}

[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: #e5c98b !important;
}

/* Ancient Navigation Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    background: rgba(24, 17, 11, 0.85);
    padding: 8px 12px;
    border-radius: 14px;
    border: 1px solid rgba(212, 175, 55, 0.35);
    margin-bottom: 24px;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.5);
}

.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    color: #c4b595 !important;
    font-family: 'Cinzel', serif !important;
    font-weight: 600 !important;
    font-size: 1.05rem !important;
    padding: 10px 22px !important;
    background: transparent !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(212, 175, 55, 0.25) 0%, rgba(139, 90, 43, 0.35) 100%) !important;
    color: #fff2d1 !important;
    border: 1px solid rgba(229, 201, 139, 0.6) !important;
    box-shadow: 0 4px 18px rgba(212, 175, 55, 0.25);
    text-shadow: 0 0 10px rgba(229, 201, 139, 0.5);
}

/* Ancient Heritage Glassmorphic Cards */
.heritage-card {
    background: linear-gradient(145deg, rgba(32, 22, 15, 0.85) 0%, rgba(20, 14, 9, 0.92) 100%);
    border: 1px solid rgba(212, 175, 55, 0.35);
    border-radius: 14px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6), inset 0 0 20px rgba(212, 175, 55, 0.05);
    backdrop-filter: blur(10px);
}

.heritage-card h4 {
    margin-top: 0;
    color: #f5dfa3;
    border-bottom: 1px solid rgba(212, 175, 55, 0.25);
    padding-bottom: 10px;
}

/* Metric / Stat Boxes with Filigree Truncation Fix */
.stat-box {
    text-align: center;
    padding: 16px 12px;
    background: linear-gradient(145deg, rgba(38, 26, 17, 0.8) 0%, rgba(22, 15, 10, 0.9) 100%);
    border: 1px solid rgba(212, 175, 55, 0.3);
    border-radius: 12px;
    margin-bottom: 12px;
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4);
}

.stat-number {
    font-family: 'Cinzel', serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: #f5dfa3;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    display: block;
    max-width: 100%;
    padding: 0 4px;
}

.stat-label {
    font-size: 0.82rem;
    color: #bda882;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-top: 4px;
}

/* Chat Messages with Ancient Scroll & Parchment Feel */
[data-testid="stChatMessage"] {
    background: linear-gradient(145deg, rgba(28, 19, 13, 0.92) 0%, rgba(18, 12, 8, 0.96) 100%) !important;
    border: 1px solid rgba(212, 175, 55, 0.3) !important;
    border-radius: 14px !important;
    padding: 18px 22px !important;
    margin-bottom: 14px !important;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.5);
    font-size: 1.05rem !important;
    line-height: 1.65 !important;
}

[data-testid="stChatMessage"] p, [data-testid="stChatMessage"] li {
    color: #f1ebd8 !important;
}

/* Chat Input Bar */
[data-testid="stChatInput"] {
    border-radius: 14px !important;
    border: 1px solid rgba(212, 175, 55, 0.5) !important;
    background-color: rgba(22, 15, 10, 0.97) !important;
    box-shadow: 0 6px 25px rgba(0, 0, 0, 0.6) !important;
}

[data-testid="stChatInput"] textarea {
    color: #f3ecd8 !important;
}

/* Ancient Golden Heritage Buttons */
.stButton > button {
    background: linear-gradient(135deg, rgba(82, 54, 28, 0.9) 0%, rgba(45, 29, 15, 0.9) 100%) !important;
    color: #f5dfa3 !important;
    border: 1px solid rgba(212, 175, 55, 0.5) !important;
    border-radius: 10px !important;
    font-family: 'Cinzel', serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 9px 20px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4) !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, rgba(120, 80, 40, 0.95) 0%, rgba(70, 45, 22, 0.95) 100%) !important;
    box-shadow: 0 0 20px rgba(212, 175, 55, 0.4) !important;
    border-color: #ffd978 !important;
    color: #ffffff !important;
    transform: translateY(-1px);
}

/* File Uploader Container - Dark Antique Fix */
[data-testid="stFileUploader"] {
    background: rgba(28, 19, 13, 0.7) !important;
    border: 2px dashed rgba(212, 175, 55, 0.45) !important;
    border-radius: 16px !important;
    padding: 20px !important;
}

[data-testid="stFileUploader"] section {
    background-color: rgba(20, 13, 8, 0.8) !important;
    border-radius: 10px !important;
}

[data-testid="stFileUploader"] section button {
    background: rgba(50, 34, 20, 0.9) !important;
    color: #f5dfa3 !important;
    border: 1px solid rgba(212, 175, 55, 0.4) !important;
}

/* Code Snippets and Manuscript Quotes */
.snippet-quote {
    border-left: 3px solid #d4af37;
    background: rgba(38, 26, 17, 0.75);
    padding: 12px 16px;
    border-radius: 0 10px 10px 0;
    margin: 10px 0;
    font-style: italic;
    color: #f1ebd8;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

/* Pill Badges */
.tag-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 600;
    background: rgba(212, 175, 55, 0.2);
    border: 1px solid rgba(212, 175, 55, 0.45);
    color: #f5dfa3;
    margin-right: 8px;
    margin-bottom: 8px;
}

/* Architecture Guide Section Box */
.arch-card {
    background: linear-gradient(145deg, rgba(32, 22, 15, 0.9) 0%, rgba(18, 12, 8, 0.95) 100%);
    border: 1px solid rgba(212, 175, 55, 0.35);
    border-radius: 14px;
    padding: 24px 28px;
    margin-bottom: 20px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.55);
}

.arch-header {
    font-family: 'Cinzel', serif;
    font-size: 1.35rem;
    color: #f5dfa3;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.arch-sub {
    color: #c9b994;
    font-size: 0.95rem;
    line-height: 1.6;
    margin-bottom: 16px;
}
</style>
"""
st.markdown(ancient_theme_css, unsafe_allow_html=True)

def get_secret(key_name: str):
    # 1. Check session state (sidebar manual input)
    if "api_keys" in st.session_state and st.session_state.api_keys.get(key_name):
        return st.session_state.api_keys[key_name].strip()
    # 2. Check OS environment variable
    val = os.environ.get(key_name)
    if val and val.strip() and not val.startswith("your_") and not val.startswith("gsk_your_") and not val.startswith("pcsk_your_"):
        return val.strip()
    # 3. Check Streamlit Secrets (for Streamlit Community Cloud)
    try:
        if hasattr(st, "secrets") and key_name in st.secrets:
            sec_val = str(st.secrets[key_name]).strip()
            if sec_val and not sec_val.startswith("your_"):
                return sec_val
    except Exception:
        pass
    return None

AVAILABLE_GROQ_MODELS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3.8-27b",
    "qwen/qwen3.6-27b",
    "groq/compound",
    "groq/compound-mini"
]

# ── Embedding Model Class (FastEmbed - No PyTorch footprint) ───────────────────
class FastEmbedEmbeddings(Embeddings):
    """Local embeddings using fastembed (ONNX runtime) for rapid, lightweight
    vector generation and cosine similarity calculation."""
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model = TextEmbedding(model_name=model_name)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [emb.tolist() for emb in self.model.embed(texts)]

    def embed_query(self, text: str) -> List[float]:
        return list(self.model.embed([text]))[0].tolist()


@st.cache_resource(show_spinner=False)
def get_embedding_model():
    return FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")


@st.cache_resource(show_spinner=False)
def load_pinecone_retriever(k: int = 8, pinecone_key: str = None):
    """Load the Pinecone classic library retriever with error resilience."""
    key = pinecone_key or get_secret("PINECONE_API_KEY")
    if not key:
        return None
    try:
        embedding_model = get_embedding_model()
        vector_db = PineconeVectorStore(
            index_name="enchanted-library",
            embedding=embedding_model,
            pinecone_api_key=key
        )
        return vector_db.as_retriever(search_kwargs={"k": k})
    except Exception as e:
        print(f"[!] Warning: Could not initialize Pinecone retriever: {e}")
        return None

# ── Multi-Format Book Text Extractor ──────────────────────────────────────────
def extract_text_from_file(uploaded_file) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Extracts text from PDF, EPUB, DOCX, TXT, MD, and HTML files.
    Returns:
        full_text: complete text string
        pages: list of dicts with {'text': ..., 'page': page_num, 'source': filename}
    """
    filename = uploaded_file.name
    ext = os.path.splitext(filename)[1].lower()
    file_bytes = uploaded_file.read()
    
    pages: List[Dict[str, Any]] = []
    full_text = ""

    if ext == ".pdf":
        reader = PdfReader(io.BytesIO(file_bytes))
        for i, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            text = text.strip()
            if text:
                pages.append({"text": text, "page": i, "source": filename})
        full_text = "\n\n".join(p["text"] for p in pages)

    elif ext == ".epub":
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
            page_num = 1
            for name in z.namelist():
                if name.lower().endswith((".html", ".xhtml", ".htm")):
                    with z.open(name) as f:
                        soup = BeautifulSoup(f.read(), "html.parser")
                        for tag in soup(["script", "style", "nav"]):
                            tag.decompose()
                        text = soup.get_text(separator="\n").strip()
                        if text and len(text) > 30:
                            pages.append({"text": text, "page": page_num, "source": f"{filename} ({name})"})
                            page_num += 1
        full_text = "\n\n".join(p["text"] for p in pages)

    elif ext in [".docx", ".doc"]:
        doc = docx.Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        current_chunk = []
        curr_len = 0
        page_num = 1
        for p in paragraphs:
            current_chunk.append(p)
            curr_len += len(p)
            if curr_len >= 2000:
                page_text = "\n\n".join(current_chunk)
                pages.append({"text": page_text, "page": page_num, "source": filename})
                current_chunk = []
                curr_len = 0
                page_num += 1
        if current_chunk:
            pages.append({"text": "\n\n".join(current_chunk), "page": page_num, "source": filename})
        full_text = "\n\n".join(paragraphs)

    elif ext in [".html", ".htm"]:
        soup = BeautifulSoup(file_bytes, "html.parser")
        for tag in soup(["script", "style", "nav"]):
            tag.decompose()
        full_text = soup.get_text(separator="\n").strip()
        pages.append({"text": full_text, "page": 1, "source": filename})

    else:
        # Plain Text / Markdown / RST
        for encoding in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
            try:
                full_text = file_bytes.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        if not full_text:
            full_text = file_bytes.decode("utf-8", errors="ignore")
        
        splitter = RecursiveCharacterTextSplitter(chunk_size=2500, chunk_overlap=200)
        docs = splitter.split_text(full_text)
        for i, doc_chunk in enumerate(docs, start=1):
            pages.append({"text": doc_chunk, "page": i, "source": filename})

    return full_text.strip(), pages


# ── In-Memory Fast Vector Indexing for Uploaded Book ───────────────────────────
def build_in_memory_index(pages: List[Dict[str, Any]], embedding_model: FastEmbedEmbeddings) -> Dict[str, Any]:
    """
    Chunks uploaded text, computes embeddings via FastEmbed, and builds a
    fast numpy cosine-similarity searchable index.
    """
    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=150)
    all_chunks = []
    
    for p in pages:
        sub_chunks = splitter.split_text(p["text"])
        for chunk in sub_chunks:
            if len(chunk.strip()) > 20:
                all_chunks.append({
                    "text": chunk.strip(),
                    "page": p.get("page", 1),
                    "source": p.get("source", "Uploaded Document")
                })
    
    if not all_chunks:
        return {"chunks": [], "embeddings_matrix": None}
    
    chunk_texts = [c["text"] for c in all_chunks]
    embeddings_list = embedding_model.embed_documents(chunk_texts)
    embeddings_matrix = np.array(embeddings_list, dtype=np.float32)
    
    # Normalize for fast cosine similarity dot product
    norms = np.linalg.norm(embeddings_matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    normalized_matrix = embeddings_matrix / norms
    
    return {
        "chunks": all_chunks,
        "embeddings_matrix": normalized_matrix
    }


def search_uploaded_book(query: str, index_data: Dict[str, Any], embedding_model: FastEmbedEmbeddings, k: int = 6) -> List[Dict[str, Any]]:
    """
    Searches the in-memory vector index for the top-k most relevant chunks.
    """
    if not index_data or not index_data.get("chunks") or index_data.get("embeddings_matrix") is None:
        return []
    
    query_emb = np.array(embedding_model.embed_query(query), dtype=np.float32)
    q_norm = np.linalg.norm(query_emb)
    if q_norm > 0:
        query_emb = query_emb / q_norm
    
    scores = np.dot(index_data["embeddings_matrix"], query_emb)
    top_indices = np.argsort(scores)[::-1][:k]
    
    results = []
    for idx in top_indices:
        chunk_info = dict(index_data["chunks"][idx])
        chunk_info["score"] = float(scores[idx])
        results.append(chunk_info)
    
    return results


# ── Language Prompt Helpers ───────────────────────────────────────────────────
LANG_OVERVIEW_PROMPT_ENGLISH = """You are a master literary scholar, historian, and cultural analyst. Provide a comprehensive, captivating, and insightful analytical overview of the provided book text.

Structure your response using the following rich markdown sections:
## 📖 Executive Synopsis
A compelling 2-3 paragraph synthesis of the book's core premise, central conflict, and thematic progression.

## 🎭 Key Figures & Entities
Detailed breakdown of primary protagonists, focal personalities, or subjects, along with their motivations and roles.

## 💡 Core Themes & Cultural Motifs
Exploration of the major philosophical, cultural, or intellectual themes explored in the work.

## 🗺️ Narrative Arc & Structure
High-level map of the beginning, critical turning points, and resolution or takeaways.

## ⭐ Key Takeaways & Enduring Insights
3-5 pivotal insights, memorable quotes, or timeless lessons from the book.

Format with clear markdown headings, bullet points, and authoritative prose."""

LANG_OVERVIEW_PROMPT_HINGLISH = """Aap ek mast literary scholar aur cultural analyst hain jo books ko desi andaz mein samjhaate hain. Is book ka ek zabardast, detailed analysis do — lekin language Hinglish mein honi chahiye (Hindi aur English ka natural mix, jaise hum normally bolte hain).

Apna response in sections mein dena:
## 📖 Kahani Ka Nichodh (Executive Synopsis)
2-3 paragraphs mein bolo — book ka core kya hai, conflict kya hai, aur kahani kahan le jaati hai. Desi style mein, as if yaar ko bata rahe ho.

## 🎭 Mukhya Kirdar aur Log (Key Figures)
Main characters ke baare mein batao — kaun hai, kya chahte hain, aur unka role kya hai. Relatable examples do.

## 💡 Bade Vichaar aur Themes (Core Themes)
Book ke bade philosophical ya cultural themes ko simple, relatable Hinglish mein explain karo.

## 🗺️ Kahani Ki Line (Narrative Arc)
Shuru se aakhir tak ka ek clear map — kya hua, turning points kya the, aur khatma kaise hua.

## ⭐ Seedhi Baatein — Key Takeaways
3-5 important lessons, memorable lines, ya timeless insights jo book se milti hain.

Format: Markdown headings, bullet points use karo. Tone casual, engaging, aur desi rakhna — jaise koi padha-likha dost bata raha ho!"""

LANG_QA_SYSTEM_ENGLISH = """
RULES:
1. Answer directly, eloquently, and authoritatively in your own authentic voice.
2. Ground your response firmly in the provided Manuscript Excerpts. Weave in direct details and specific passages where helpful.
3. If the user asks for translations, explanations, or specific details, fulfill their request thoroughly and clearly.
4. If the excerpts do not contain the answer, synthesize what is known honestly. Never fabricate contradictory facts.
5. Maintain a respectful, articulate, and engaging tone."""

LANG_QA_SYSTEM_HINGLISH = """
RULES (Hinglish mein jawab dena hai):
1. Jawab seedha, confident aur Hinglish mein do — jaise ek padha-likha dost bata raha ho. English aur Hindi naturally mix karo.
2. Jo passages diye gaye hain unke basis par jawab do. Specific details aur scenes use karo.
3. Agar user ne translation ya explanation maanga ho toh clearly aur clearly do.
4. Agar passages mein jawab na ho toh honestly bolo — kabhi bhi galat facts mat banana.
5. Tone friendly, engaging aur conversational rakhna — bilkul desi style mein!"""


# ── AI Book Overview Generator ────────────────────────────────────────────────
def generate_book_overview(full_text: str, book_name: str, llm: ChatGroq, language: str = "English") -> str:
    """
    Generates a structured, deep literary analysis and overview of the book.
    Supports 'English' and 'Hinglish' language modes.
    """
    total_len = len(full_text)
    if total_len > 25000:
        chunk1 = full_text[:10000]
        mid_idx = total_len // 2
        chunk2 = full_text[mid_idx - 5000 : mid_idx + 5000]
        chunk3 = full_text[-10000:]
        sampled_content = f"--- BEGINNING SECTION ---\n{chunk1}\n\n--- MIDDLE SECTION ---\n{chunk2}\n\n--- CONCLUSION / END SECTION ---\n{chunk3}"
    else:
        sampled_content = full_text

    overview_prompt = LANG_OVERVIEW_PROMPT_HINGLISH if language == "Hinglish" else LANG_OVERVIEW_PROMPT_ENGLISH
    sys_msg = SystemMessage(content=overview_prompt)
    user_msg = HumanMessage(content=f"Book Title / File: {book_name}\n\nBook Content:\n{sampled_content}\n\nPlease generate the comprehensive Book Overview & Analysis:")

    response = llm.invoke([sys_msg, user_msg])
    return response.content


# ── Session State Initialization ──────────────────────────────────────────────
if "api_keys" not in st.session_state:
    st.session_state.api_keys = {}

if "uploaded_chat_history" not in st.session_state:
    st.session_state.uploaded_chat_history = []

if "classic_chat_history" not in st.session_state:
    st.session_state.classic_chat_history = []

if "current_book_data" not in st.session_state:
    st.session_state.current_book_data = None

if "current_book_overview" not in st.session_state:
    st.session_state.current_book_overview = None

if "response_language" not in st.session_state:
    st.session_state.response_language = "English"


# ── Sidebar Controls & Configuration ──────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏛️ Heritage Settings")
    
    default_model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    if default_model not in AVAILABLE_GROQ_MODELS:
        default_model = AVAILABLE_GROQ_MODELS[0]
    
    selected_model = st.selectbox(
        "🧠 AI Intelligence Model",
        options=AVAILABLE_GROQ_MODELS,
        index=AVAILABLE_GROQ_MODELS.index(default_model) if default_model in AVAILABLE_GROQ_MODELS else 0,
        help="Choose the Groq LLM model for analysis and conversational answers."
    )
    # Store in session state so feature modules (profile, summarizer) can access it
    st.session_state["selected_model"] = selected_model


    temperature = st.slider(
        "✨ Creativity (Temperature)",
        min_value=0.0,
        max_value=1.0,
        value=0.1,
        step=0.05,
        help="Lower values produce more grounded, exact answers. Higher values add literary flair."
    )
    
    retrieval_k = st.slider(
        "🔍 Retrieval Depth (Top Chunks)",
        min_value=3,
        max_value=15,
        value=8,
        step=1,
        help="Number of book passages retrieved to answer each question."
    )
    
    st.markdown("---")
    
    # ── Language / Bhasha Selector ──────────────────────────────────────────
    st.markdown("### 🌐 Explanation Language (Bhasha)")
    lang_choice = st.radio(
        "Select language / Bhasha chunein",
        options=["🇬🇧 English", "🇮🇳 Hinglish (हिंग्लिश)"],
        index=0 if st.session_state.response_language == "English" else 1,
        help="Choose how the AI explains — formal English or fun Hinglish (Hindi + English mix)!",
        label_visibility="collapsed",
        key="lang_radio"
    )
    selected_language = "English" if lang_choice == "🇬🇧 English" else "Hinglish"
    if selected_language != st.session_state.response_language:
        st.session_state.response_language = selected_language
        st.session_state.current_book_overview = None  # Reset overview to regenerate in new language
    
    if selected_language == "Hinglish":
        st.caption("🎉 Hinglish mode ON! AI ab Hindi-English mix mein bolega — desi style mein!")
    
    st.markdown("---")
    
    # API Status & Interactive Key Input
    st.markdown("### 🔐 System Status")
    groq_active_key = get_secret("GROQ_API_KEY")
    pinecone_active_key = get_secret("PINECONE_API_KEY")
    
    groq_ok = bool(groq_active_key)
    pinecone_ok = bool(pinecone_active_key)
    
    st.markdown(f"**Groq API:** {'🟢 Connected' if groq_ok else '🔴 Missing Key'}")
    st.markdown(f"**Pinecone Archive:** {'🟢 Connected' if pinecone_ok else '🟡 Missing Key'}")
    
    with st.expander("🔑 Enter / Update API Keys", expanded=(not groq_ok)):
        st.caption("Enter keys below if not in `.env` or Streamlit Secrets:")
        
        user_groq = st.text_input(
            "Groq API Key",
            value=st.session_state.api_keys.get("GROQ_API_KEY", "") or (groq_active_key if groq_active_key else ""),
            type="password",
            placeholder="gsk_...",
            help="Free Groq API key from https://console.groq.com"
        )
        if user_groq and user_groq != st.session_state.api_keys.get("GROQ_API_KEY"):
            st.session_state.api_keys["GROQ_API_KEY"] = user_groq.strip()
            os.environ["GROQ_API_KEY"] = user_groq.strip()
            st.rerun()
            
        user_pinecone = st.text_input(
            "Pinecone API Key (Optional)",
            value=st.session_state.api_keys.get("PINECONE_API_KEY", "") or (pinecone_active_key if pinecone_active_key else ""),
            type="password",
            placeholder="pcsk_...",
            help="Required only for Canonical Classics archive search (https://app.pinecone.io)"
        )
        if user_pinecone and user_pinecone != st.session_state.api_keys.get("PINECONE_API_KEY"):
            st.session_state.api_keys["PINECONE_API_KEY"] = user_pinecone.strip()
            os.environ["PINECONE_API_KEY"] = user_pinecone.strip()
            st.rerun()

    if not groq_ok:
        st.error("⚠️ `GROQ_API_KEY` is not detected. Enter it above or add it to `.env` / Streamlit Secrets.")
    
    st.markdown("---")
    
    # Active Book Statistics
    if st.session_state.current_book_data:
        st.markdown("### 📜 Active Tome Details")
        book = st.session_state.current_book_data
        st.write(f"**File:** `{book['filename']}`")
        st.write(f"**Words:** `{book['word_count']:,}`")
        st.write(f"**Sections:** `{book['total_pages']}`")
        st.write(f"**Chunks:** `{len(book['index']['chunks'])}`")
        
        if st.button("🧹 Clear Active Tome", use_container_width=True):
            st.session_state.current_book_data = None
            st.session_state.current_book_overview = None
            st.session_state.uploaded_chat_history = []
            st.rerun()

    st.markdown("---")
    st.markdown("### 📜 Timeless Classic Tomes")
    st.caption("Pre-indexed classics available in the archive:")
    classic_titles = [
        "Pride and Prejudice",
        "Frankenstein",
        "Little Women",
        "Crime and Punishment",
        "The Mahabharata",
        "Bhagavad Gita",
        "Sense and Sensibility",
        "The Yoga-Vasishtha Maharamayana"
    ]
    for b in classic_titles:
        st.markdown(f"- 🏛️ *{b}*")


# ── Main Header ───────────────────────────────────────────────────────────────
st.title("🏛️ The Ancient Heritage Library & Book Intelligence 🏛️")
st.markdown("<p style='text-align: center; color: #d6c6a2; font-size: 1.15rem;'>Step into an ancient sanctuary of knowledge. Upload any manuscript or book in any format to unlock instant AI analysis, cultural overviews, and grounded conversational Q&A.</p>", unsafe_allow_html=True)
st.write("")

# ── Navigation Tabs ───────────────────────────────────────────────────────────
tab_upload, tab_classic, tab_profile, tab_about = st.tabs([
    "📖 Upload & Analyze",
    "🏛️ Classic Archive",
    "👤 Profile",
    "🏰 Guide"
])


# ==============================================================================
# TAB 1: UPLOAD & ANALYZE BOOK (ANY FORMAT)
# ==============================================================================
with tab_upload:
    st.markdown("### 📤 Inscribe a New Manuscript or Book")
    st.markdown("Supports **PDF, EPUB, DOCX, TXT, Markdown (.md), and HTML** files. The text is analyzed and indexed locally in memory.")
    
    uploaded_file = st.file_uploader(
        "Select or drag and drop your book manuscript",
        type=["pdf", "epub", "docx", "doc", "txt", "md", "markdown", "html", "htm"],
        help="Upload any book, manuscript, or document to analyze."
    )
    
    if uploaded_file is not None:
        file_key = f"{uploaded_file.name}_{uploaded_file.size}"
        
        if (st.session_state.current_book_data is None or 
            st.session_state.current_book_data.get("file_key") != file_key):
            
            with st.status("🔮 Reading and indexing your manuscript...", expanded=True) as status:
                st.write("📜 Extracting text across chapters and pages...")
                full_text, pages = extract_text_from_file(uploaded_file)
                
                if not full_text:
                    st.error("Could not extract any readable text from this file.")
                else:
                    word_count = len(full_text.split())
                    reading_time_mins = max(1, word_count // 200)
                    
                    st.write(f"⚡ Creating fast semantic vector embeddings ({len(pages)} sections)...")
                    emb_model = get_embedding_model()
                    index_data = build_in_memory_index(pages, emb_model)
                    
                    st.session_state.current_book_data = {
                        "file_key": file_key,
                        "filename": uploaded_file.name,
                        "full_text": full_text,
                        "pages": pages,
                        "word_count": word_count,
                        "reading_time_mins": reading_time_mins,
                        "total_pages": len(pages),
                        "index": index_data
                    }
                    st.session_state.uploaded_chat_history = []
                    st.session_state.current_book_overview = None
                    
                    status.update(label="✅ Manuscript inscribed and indexed successfully!", state="complete", expanded=False)
                    st.rerun()

    # Display Active Book Dashboard & Overview
    if st.session_state.current_book_data:
        book = st.session_state.current_book_data
        
        # Metric Stats Bar
        col1, col2, col3, col4 = st.columns(4)
        short_name = book['filename']
        if len(short_name) > 22:
            short_name = short_name[:19] + "..."
            
        with col1:
            st.markdown(f"""
            <div class="stat-box">
                <span class="stat-number" title="{book['filename']}">📖 {short_name}</span>
                <div class="stat-label">Active Tome</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="stat-box">
                <span class="stat-number">{book['word_count']:,}</span>
                <div class="stat-label">Total Words</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="stat-box">
                <span class="stat-number">{book['total_pages']}</span>
                <div class="stat-label">Sections / Pages</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="stat-box">
                <span class="stat-number">~{book['reading_time_mins']} min</span>
                <div class="stat-label">Est. Reading Time</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.write("")
        
        # Overview Section
        col_ov_title, col_ov_btn = st.columns([3, 1])
        with col_ov_title:
            st.markdown("### 📑 Book Intelligence & Overview")
        with col_ov_btn:
            generate_ov_clicked = st.button("🔮 Generate Deep Analysis", use_container_width=True)
        
        active_groq_key = get_secret("GROQ_API_KEY")
        current_lang = st.session_state.get("response_language", "English")
        spinner_msg = "Kitaabon ka vishleshan ho raha hai... zara ruko! 📖" if current_lang == "Hinglish" else "Analyzing themes, characters, structure, and narrative arc..."
        if generate_ov_clicked or (st.session_state.current_book_overview is None):
            if not active_groq_key:
                st.warning("⚠️ Please provide a `GROQ_API_KEY` (in the sidebar, `.env`, or Streamlit Secrets) to generate the AI Book Overview.")
            else:
                with st.spinner(spinner_msg):
                    try:
                        llm = ChatGroq(model=selected_model, temperature=temperature, api_key=active_groq_key)
                        overview_text = generate_book_overview(book["full_text"], book["filename"], llm, language=current_lang)
                        st.session_state.current_book_overview = overview_text
                    except Exception as e:
                        st.error(f"Error generating overview: {e}")
        
        if st.session_state.current_book_overview:
            with st.container():
                st.markdown(st.session_state.current_book_overview)
                
                # Download Button for Overview
                st.download_button(
                    label="📥 Download Overview Report (Markdown)",
                    data=st.session_state.current_book_overview,
                    file_name=f"{book['filename']}_AI_Analysis.md",
                    mime="text/markdown"
                )
        
        st.markdown("---")
        
        # Q&A Chatbot Section for Uploaded Book
        st.markdown(f"### 💬 Inquire About *{book['filename']}*")
        st.caption("Ask questions about specific chapters, character arcs, cultural motifs, or plot turning points.")
        
        # Quick Starter Question Pills
        starter_cols = st.columns(4)
        quick_questions = [
            "Summarize the central plot arc",
            "Who are the key figures and roles?",
            "What are the central themes & motifs?",
            "Explain the ending or resolution"
        ]
        selected_quick_q = None
        for i, q_text in enumerate(quick_questions):
            with starter_cols[i]:
                if st.button(f"💡 {q_text}", key=f"quick_q_{i}", use_container_width=True):
                    selected_quick_q = q_text
        
        # Display Uploaded Book Chat History
        for msg in st.session_state.uploaded_chat_history:
            with st.chat_message(msg["role"], avatar="📜" if msg["role"] == "user" else "🏛️"):
                st.markdown(msg["content"])
                if "snippets" in msg and msg["snippets"]:
                    with st.expander("🔍 View Retrieved Manuscript Passages"):
                        for j, snip in enumerate(msg["snippets"], start=1):
                            st.markdown(f"""
                            <div class="snippet-quote">
                                <strong>Passage {j} (Section {snip.get('page', 'N/A')} — Relevance {snip.get('score', 0.0):.2f}):</strong><br>
                                {snip['text']}
                            </div>
                            """, unsafe_allow_html=True)

        # Clear Chat Button
        if len(st.session_state.uploaded_chat_history) > 0:
            if st.button("🗑️ Clear Conversation History", key="clear_uploaded_chat"):
                st.session_state.uploaded_chat_history = []
                st.rerun()

        # Chat Input Bar
        chat_query = st.chat_input(f"Ask a question about {book['filename']}...")
        query_to_process = selected_quick_q or chat_query
        
        if query_to_process:
            active_groq_key = get_secret("GROQ_API_KEY")
            if not active_groq_key:
                st.error("Missing `GROQ_API_KEY`! Please configure it in the sidebar, `.env` file, or Streamlit Secrets.")
            else:
                st.session_state.uploaded_chat_history.append({"role": "user", "content": query_to_process})
                with st.chat_message("user", avatar="📜"):
                    st.markdown(query_to_process)
                
                with st.chat_message("assistant", avatar="🏛️"):
                    with st.spinner("Consulting manuscript excerpts and formulating answer..."):
                        try:
                            llm = ChatGroq(model=selected_model, temperature=temperature, api_key=active_groq_key)
                            emb_model = get_embedding_model()
                            
                            # Conversational standalone question reformulation
                            history_list = st.session_state.uploaded_chat_history[:-1]
                            if len(history_list) > 0:
                                history_text = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in history_list[-4:]])
                                rewrite_sys = SystemMessage(content="You are an assistant that reformulates follow-up questions into clear, standalone search queries including character names or concepts. Return ONLY the standalone search query without preamble.")
                                rewrite_human = HumanMessage(content=f"Recent conversation:\n{history_text}\n\nUser's new question: '{query_to_process}'")
                                standalone_q = llm.invoke([rewrite_sys, rewrite_human]).content.strip()
                            else:
                                standalone_q = query_to_process
                                history_text = "No prior history."
                            
                            retrieved_snippets = search_uploaded_book(
                                standalone_q,
                                book["index"],
                                emb_model,
                                k=retrieval_k
                            )
                            
                            context_text = "\n\n---\n\n".join([
                                f"[Passage {idx+1} | Page/Section {s.get('page', 'N/A')}]:\n{s['text']}" 
                                for idx, s in enumerate(retrieved_snippets)
                            ])
                            
                            current_lang = st.session_state.get("response_language", "English")
                            lang_rules = LANG_QA_SYSTEM_HINGLISH if current_lang == "Hinglish" else LANG_QA_SYSTEM_ENGLISH
                            
                            lang_intro = (
                                f'Aap ek mast literary aur historical scholar hain jo "{book["filename"]}" ke baare mein baat kar rahe hain.'
                                if current_lang == "Hinglish"
                                else f'You are an insightful, highly knowledgeable literary and historical scholar discussing the uploaded manuscript titled: "{book["filename"]}".'
                            )
                            
                            qa_sys = SystemMessage(content=f"""{lang_intro}

{lang_rules}

Manuscript Excerpts:
{context_text}

Conversation History:
{history_text}""")

                            qa_human = HumanMessage(content=standalone_q)
                            response = llm.invoke([qa_sys, qa_human])
                            answer = response.content
                            
                            st.markdown(answer)
                            
                            if retrieved_snippets:
                                with st.expander("🔍 View Retrieved Manuscript Passages"):
                                    st.write(f"**Interpretation:** `{standalone_q}`")
                                    for j, snip in enumerate(retrieved_snippets, start=1):
                                        st.markdown(f"""
                                        <div class="snippet-quote">
                                            <strong>Passage {j} (Section {snip.get('page', 'N/A')} — Relevance {snip.get('score', 0.0):.2f}):</strong><br>
                                            {snip['text']}
                                        </div>
                                        """, unsafe_allow_html=True)
                            
                            st.session_state.uploaded_chat_history.append({
                                "role": "assistant",
                                "content": answer,
                                "snippets": retrieved_snippets
                            })
                            
                        except Exception as e:
                            st.error(f"Error answering question: {e}")

    else:
        st.info("💡 **Ancient Library Ready:** Upload any book or manuscript above to generate an instant overview and start asking questions!")


# ==============================================================================
# TAB 2: THE CLASSIC LIBRARY ARCHIVE (PINECONE PRE-INDEXED TOMES)
# ==============================================================================
with tab_classic:
    st.markdown("### 🏛️ The Ancient Archive of Timeless Classics")
    st.markdown("Ask deep questions across all 8 canonical masterworks pre-indexed into the Pinecone cloud archive.")
    
    classic_groq_key = get_secret("GROQ_API_KEY")
    classic_pinecone_key = get_secret("PINECONE_API_KEY")
    if not classic_groq_key or not classic_pinecone_key:
        st.warning("⚠️ Both `GROQ_API_KEY` and `PINECONE_API_KEY` are required to query the Pinecone archive. Configure them in the sidebar or Streamlit Secrets.")
    
    # Classic Library Chat History
    for msg in st.session_state.classic_chat_history:
        with st.chat_message(msg["role"], avatar="📜" if msg["role"] == "user" else "🏛️"):
            st.markdown(msg["content"])
            if "snippets" in msg and msg["snippets"]:
                with st.expander("👀 See Retrieved Archive Passages"):
                    for j, snip in enumerate(msg["snippets"], start=1):
                        st.markdown(f"""
                        <div class="snippet-quote">
                            <strong>Snippet {j}:</strong><br>
                            {snip}
                        </div>
                        """, unsafe_allow_html=True)

    if len(st.session_state.classic_chat_history) > 0:
        if st.button("🗑️ Clear Archive Chat", key="clear_classic_chat"):
            st.session_state.classic_chat_history = []
            st.rerun()

    classic_prompt = st.chat_input("Ask a question about Pride and Prejudice, Frankenstein, Little Women, Mahabharata...", key="classic_input")
    
    if classic_prompt:
        classic_groq_key = get_secret("GROQ_API_KEY")
        classic_pinecone_key = get_secret("PINECONE_API_KEY")
        if not classic_groq_key or not classic_pinecone_key:
            st.error("Missing required API keys (GROQ_API_KEY and PINECONE_API_KEY).")
        else:
            st.session_state.classic_chat_history.append({"role": "user", "content": classic_prompt})
            with st.chat_message("user", avatar="📜"):
                st.markdown(classic_prompt)
            
            with st.chat_message("assistant", avatar="🏛️"):
                with st.spinner("Searching the Pinecone archives and consulting the scrolls..."):
                    try:
                        llm = ChatGroq(model=selected_model, temperature=temperature, api_key=classic_groq_key)
                        retriever = load_pinecone_retriever(k=retrieval_k, pinecone_key=classic_pinecone_key)
                        
                        if retriever is None:
                            st.error("Could not connect to Pinecone 'enchanted-library' index. Please check your API key and network.")
                        else:
                            history_list = st.session_state.classic_chat_history[:-1]
                            if len(history_list) > 0:
                                history_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in history_list[-4:]])
                                rewrite_sys = SystemMessage(content="You are an assistant that reformulates follow-up questions into clear, standalone questions that include specific character names or book titles. Return ONLY the rewritten question without extra words.")
                                rewrite_human = HumanMessage(content=f"Recent conversation:\n{history_text}\n\nUser's new question: '{classic_prompt}'")
                                standalone_question = llm.invoke([rewrite_sys, rewrite_human]).content.strip()
                            else:
                                standalone_question = classic_prompt
                                history_text = "No previous history."
                            
                            retrieved_docs = retriever.invoke(standalone_question)
                            context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)
                            snippet_texts = [doc.page_content for doc in retrieved_docs]
                            
                            current_lang = st.session_state.get("response_language", "English")
                            lang_rules = LANG_QA_SYSTEM_HINGLISH if current_lang == "Hinglish" else LANG_QA_SYSTEM_ENGLISH
                            
                            classic_intro = (
                                "Aap ek jadoo-bhari archive ke scholar hain jo classic books ke baare mein desi, friendly style mein batate hain. Directly aur confidently jawab do, jaise ek padha-likha yaar bata raha ho."
                                if current_lang == "Hinglish"
                                else "You are a knowledgeable literary and cultural scholar helping a user explore classic books in the archive. Answer the way a well-read expert would in conversation \u2014 direct, confident, and in your own voice."
                            )
                            
                            sys_msg = SystemMessage(content=f"""{classic_intro}

{lang_rules}

Conversation History:
{history_text}

Context:
{context_text}""")
                            user_msg = HumanMessage(content=standalone_question)
                            response = llm.invoke([sys_msg, user_msg])
                            response_content = response.content
                            
                            st.markdown(response_content)
                            
                            with st.expander("👀 See how the AI thought & what it read"):
                                st.write(f"**Interpreted Question:** `{standalone_question}`")
                                if len(retrieved_docs) > 0:
                                    for i, doc in enumerate(retrieved_docs):
                                        book_tag = doc.metadata.get("book_title", "Classic Tome")
                                        st.markdown(f"""
                                        <div class="snippet-quote">
                                            <strong>Snippet {i+1} [{book_tag}]:</strong><br>
                                            {doc.page_content}
                                        </div>
                                        """, unsafe_allow_html=True)
                                else:
                                    st.write("No matching snippets found. The AI answered from its own literary memory.")
                            
                            st.session_state.classic_chat_history.append({
                                "role": "assistant",
                                "content": response,
                                "snippets": snippet_texts
                            })
                            
                    except Exception as e:
                        st.error(f"Something went wrong: {e}")



# ==============================================================================
# TAB 3: READING PROFILE
# ==============================================================================
with tab_profile:
    st.markdown("### 👤 Personal Reading Profile")
    st.caption("Save your reading preferences — genres, speed, and history — so the AI tailors responses to you.")
    if profile:
        profile.render_profile_section()
    else:
        st.error("profile.py module not found.")

    # Language preferences
    st.markdown("---")
    if multilingual:
        multilingual.render_language_selector()
    else:
        st.warning("multilingual.py not available.")


# ==============================================================================
# TAB 4: ARCHITECTURE & USER GUIDE
# ==============================================================================
with tab_about:
    st.markdown("### 🏰 Architecture & Comprehensive User Guide")
    st.markdown("Explore how the Ancient Heritage Library orchestrates local document extraction, neural embeddings, in-memory vector similarity, and cloud LLM inference.")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("""
        <div class="arch-card">
            <div class="arch-header">📜 1. Multi-Format Book Ingestion</div>
            <div class="arch-sub">Robust client-side extraction across diverse manuscript formats:</div>
            <ul>
                <li><strong>PDF (.pdf):</strong> Page-by-page text extraction with <code>pypdf.PdfReader</code>.</li>
                <li><strong>EPUB (.epub):</strong> Reading order XML/HTML chapter extraction with <code>BeautifulSoup</code>.</li>
                <li><strong>DOCX (.docx):</strong> Structural paragraph and table parsing with <code>python-docx</code>.</li>
                <li><strong>Plain Text & Markdown:</strong> Multi-encoding auto-detection (UTF-8, Latin-1, CP1252).</li>
                <li><strong>Web HTML (.html):</strong> Script and style stripping with semantic text retention.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="arch-card">
            <div class="arch-header">⚡ 2. Local Neural Vector Engine</div>
            <div class="arch-sub">High-efficiency local vector embeddings without external cloud uploads:</div>
            <ul>
                <li><strong>Chunking:</strong> <code>RecursiveCharacterTextSplitter</code> (900 chars, 150-char overlap).</li>
                <li><strong>FastEmbed ONNX:</strong> <code>BAAI/bge-small-en-v1.5</code> 384-dimensional dense vectors.</li>
                <li><strong>Normalized Cosine Search:</strong> Instant Numpy matrix dot-product similarity.</li>
                <li><strong>Zero Data Leakage:</strong> Custom books are embedded and kept in-memory.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown("""
        <div class="arch-card">
            <div class="arch-header">🏛️ 3. Pinecone Cloud Archive</div>
            <div class="arch-sub">Pre-indexed library of 13,000+ vector chunks for timeless canonical works:</div>
            <ul>
                <li><strong>8 Masterworks:</strong> Pride & Prejudice, Frankenstein, Little Women, Mahabharata, etc.</li>
                <li><strong>Vector Index:</strong> Serverless Cosine index on AWS.</li>
                <li><strong>Cached Retrieval:</strong> <code>load_pinecone_retriever()</code> with Streamlit resource caching.</li>
                <li><strong>Dual-Mode Switching:</strong> Explore custom books or canonical classics simultaneously.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="arch-card">
            <div class="arch-header">🧠 4. Groq Ultra-Fast Inference</div>
            <div class="arch-sub">Next-generation language model synthesis with conversational reasoning:</div>
            <ul>
                <li><strong>Active Models:</strong> <code>openai/gpt-oss-120b</code>, <code>openai/gpt-oss-20b</code>, <code>qwen/qwen3.8-27b</code>.</li>
                <li><strong>Standalone Query Rewriter:</strong> Resolves multi-turn pronoun references.</li>
                <li><strong>Grounded Synthesis:</strong> Direct citations and source passage transparency.</li>
                <li><strong>Markdown Export:</strong> 1-click download of generated book analysis reports.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
