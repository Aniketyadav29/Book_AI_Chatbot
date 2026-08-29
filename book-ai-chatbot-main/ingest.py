"""
ingest.py — Standalone ingestion script for The Enchanted Library
-----------------------------------------------------------------
* Creates the Pinecone 'enchanted-library' index if it doesn't exist
* Downloads all 8 books from Project Gutenberg (via Gutendex API)
* Splits each book into ~1000-char chunks with 200-char overlap
* Embeds with fastembed (same model as app.py, no PyTorch needed)
* Upserts all embeddings into Pinecone

Run once before starting app.py:
    python ingest.py
"""

import os
import re
import time
import requests

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.embeddings import Embeddings
from fastembed import TextEmbedding
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

# ── Load API keys from .env file if present ──────────────────────────────────
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY not set. Add it to your .env file.")

# ── Same embedding class as app.py (fastembed, no PyTorch) ───────────────────
class FastEmbedEmbeddings(Embeddings):
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model = TextEmbedding(model_name=model_name)

    def embed_documents(self, texts):
        return [emb.tolist() for emb in self.model.embed(texts)]

    def embed_query(self, text):
        return list(self.model.embed([text]))[0].tolist()


# ── Create Pinecone index if it doesn't exist ─────────────────────────────────
INDEX_NAME   = "enchanted-library"
DIMENSION    = 384          # all-MiniLM-L6-v2 output dimension
METRIC       = "cosine"

print("\n[*] Connecting to Pinecone...")
pc = Pinecone(api_key=PINECONE_API_KEY)
existing = [idx.name for idx in pc.list_indexes()]

if INDEX_NAME not in existing:
    print(f"[+] Index '{INDEX_NAME}' not found. Creating it...")
    pc.create_index(
        name=INDEX_NAME,
        dimension=DIMENSION,
        metric=METRIC,
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )
    # Wait until index is ready
    while not pc.describe_index(INDEX_NAME).status.get("ready", False):
        print("   Waiting for index to be ready...")
        time.sleep(3)
    print(f"[+] Index '{INDEX_NAME}' created and ready!\n")
else:
    print(f"[+] Index '{INDEX_NAME}' already exists.\n")


# ── Embedding model (loaded once, reused for all books) ───────────────────────
print("[*] Loading embedding model (sentence-transformers/all-MiniLM-L6-v2)...")
embedding_model = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")
print("[+] Embedding model ready!\n")


# ── Ingest function ────────────────────────────────────────────────────────────
def ingest(book_title: str):
    print(f"[BOOK] [{book_title}] Searching on Gutendex...")

    # 1. Search Gutendex for the book
    search_url = f"https://gutendex.com/books/?search={book_title.replace(' ', '%20')}"
    response = requests.get(search_url, timeout=30).json()

    if response["count"] == 0:
        print(f"   [!] '{book_title}' not found on Project Gutenberg. Skipping.\n")
        return

    book_info = response["results"][0]
    title     = book_info["title"]
    formats   = book_info["formats"]

    # 2. Find plain-text URL
    text_url = None
    for key, fmt_url in formats.items():
        if "text/plain" in key and "zip" not in fmt_url:
            text_url = fmt_url
            break
    # fallback: any text/plain
    if not text_url:
        for key, fmt_url in formats.items():
            if "text/plain" in key:
                text_url = fmt_url
                break

    if not text_url:
        print(f"   [!] Plain text for '{title}' not found. Skipping.\n")
        return

    print(f"   [>>] Downloading: {title}")
    print(f"      URL: {text_url}")

    # 3. Download the text
    text_response = requests.get(text_url, timeout=60)
    text_response.encoding = "utf-8"

    # 4. Save to temp file
    safe_title = re.sub(r'[\\/*?:"<>|]', "", title)
    file_path  = f"temp_{safe_title[:50].replace(' ', '_')}.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text_response.text)

    # 5. Load & chunk
    print(f"   [~] Chunking text...")
    loader    = TextLoader(file_path, encoding="utf-8")
    documents = loader.load()
    splitter  = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks    = splitter.split_documents(documents)

    for chunk in chunks:
        chunk.metadata = {"book_title": safe_title}

    print(f"   [i] Total chunks: {len(chunks)}")

    # 6. Embed & upsert to Pinecone
    print(f"   [^] Embedding & uploading to Pinecone...")
    PineconeVectorStore.from_documents(
        documents=chunks,
        embedding=embedding_model,
        index_name=INDEX_NAME,
    )

    # 7. Cleanup temp file
    os.remove(file_path)
    print(f"   [OK] '{title}' successfully added to Pinecone!\n")


# ── Books to ingest ────────────────────────────────────────────────────────────
BOOKS = [
    "Pride and Prejudice",
    "Frankenstein",
    "Little Women",
    "Crime and Punishment",
    "The Mahabharata",
    "Bhagavad Gita",
    "Sense and Sensibility",
    "The Yoga-Vasishtha Maharamayana",
]

print("=" * 60)
print("  THE ENCHANTED LIBRARY - INGESTION PIPELINE")
print("=" * 60)
print(f"  Books to process: {len(BOOKS)}")
print("=" * 60 + "\n")

for i, book in enumerate(BOOKS, 1):
    print(f"[{i}/{len(BOOKS)}] Processing: {book}")
    try:
        ingest(book)
    except Exception as e:
        print(f"   [ERR] Error processing '{book}': {e}\n")

print("=" * 60)
print("  INGESTION COMPLETE!")
print("  You can now run: python -m streamlit run app.py")
print("=" * 60 + "\n")
