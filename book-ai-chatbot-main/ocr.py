import streamlit as st
import os
import io
import tempfile
from typing import Optional


def render_ocr_uploader():
    """Upload images or scanned PDFs, run OCR, and store extracted text in session state.
    Provides a 1-click button to inscribe extracted OCR text directly into the active book RAG pipeline.
    """
    st.markdown("#### 📷 Scanned Manuscript & Image OCR")
    st.caption("Extract text from scanned book pages, ancient manuscripts, or document images using optical character recognition.")

    uploaded = st.file_uploader(
        "Upload Image or Scanned Document",
        type=["png", "jpg", "jpeg", "webp", "tiff", "pdf"],
        accept_multiple_files=False,
        key="ocr_file_uploader",
        help="Supports PNG, JPG, JPEG, WEBP, TIFF, and scanned single/multi-page PDFs."
    )

    if uploaded is not None:
        if st.button("🔍 Extract Text via OCR", key="run_ocr_btn", use_container_width=True):
            with st.spinner("Processing document through OCR engine…"):
                ocr_text = ""
                try:
                    import pytesseract
                    from PIL import Image

                    if uploaded.type == "application/pdf":
                        try:
                            import pdf2image
                            with tempfile.TemporaryDirectory() as tmpdir:
                                images = pdf2image.convert_from_bytes(uploaded.read(), fmt="png", output_folder=tmpdir)
                                texts = []
                                for idx, img in enumerate(images, start=1):
                                    t = pytesseract.image_to_string(img)
                                    if t.strip():
                                        texts.append(f"--- [Page {idx}] ---\n{t.strip()}")
                                ocr_text = "\n\n".join(texts)
                        except ImportError:
                            st.error("⚠️ `pdf2image` library is not installed. Please install `pdf2image` and `poppler` to OCR multi-page PDFs.")
                        except Exception as pe:
                            st.warning(f"Could not convert PDF pages to images (Poppler might not be installed): {pe}")
                            st.info("💡 Tip: Try converting your PDF page to a PNG or JPG image and uploading that directly.")
                    else:
                        image = Image.open(uploaded)
                        ocr_text = pytesseract.image_to_string(image)

                    if ocr_text.strip():
                        st.session_state["ocr_text"] = ocr_text.strip()
                        st.session_state["ocr_filename"] = uploaded.name
                        st.success("✅ OCR extraction completed successfully!")
                    else:
                        st.warning("⚠️ No readable text could be recognized from this document. Ensure image resolution and contrast are sufficient.")

                except ImportError as ie:
                    st.error(f"⚠️ OCR dependency missing: {ie}. Ensure `pytesseract` and `Pillow` are installed.")
                except Exception as e:
                    err_str = str(e)
                    if "tesseract is not installed" in err_str.lower() or "not found" in err_str.lower():
                        st.error("❌ Tesseract OCR binary not found on the host system PATH.")
                        st.info("💡 To enable OCR, install Tesseract OCR (e.g. `sudo apt install tesseract-ocr` or Windows installer from GitHub) or upload digital PDF/EPUB/DOCX/TXT manuscripts instead.")
                    else:
                        st.error(f"OCR processing error: {e}")

    # Display extracted text and inscription button if available
    saved_ocr = st.session_state.get("ocr_text", "")
    if saved_ocr:
        st.markdown("---")
        st.markdown(f"**Extracted Text Preview ({len(saved_ocr.split()):,} words):**")
        preview_text = saved_ocr[:800] + "..." if len(saved_ocr) > 800 else saved_ocr
        st.text_area("Recognized Text", value=preview_text, height=140, disabled=True, key="ocr_preview_box")

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📥 Download OCR Text",
                data=saved_ocr,
                file_name=f"ocr_{st.session_state.get('ocr_filename', 'manuscript')}.txt",
                mime="text/plain",
                key="dl_ocr_text",
                use_container_width=True
            )
        with col2:
            if st.button("📖 Inscribe as Active Manuscript", key="inscribe_ocr_btn", use_container_width=True):
                # Inscribe OCR text into session state for full RAG analysis
                from langchain_text_splitters import RecursiveCharacterTextSplitter
                splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=150)
                chunks = splitter.split_text(saved_ocr)
                pages = [{"text": c, "page": i + 1, "source": f"OCR: {st.session_state.get('ocr_filename', 'scanned_doc')}"} for i, c in enumerate(chunks)]

                # Build in-memory index
                from app import build_in_memory_index, get_embedding_model
                emb_model = get_embedding_model()
                index_data = build_in_memory_index(pages, emb_model)

                word_count = len(saved_ocr.split())
                st.session_state.current_book_data = {
                    "file_key": f"ocr_{len(saved_ocr)}_{word_count}",
                    "filename": f"OCR: {st.session_state.get('ocr_filename', 'Scanned Manuscript')}",
                    "full_text": saved_ocr,
                    "pages": pages,
                    "word_count": word_count,
                    "reading_time_mins": max(1, word_count // 200),
                    "total_pages": len(pages),
                    "index": index_data
                }
                st.session_state.uploaded_chat_history = []
                st.session_state.current_book_overview = None
                st.success("🎉 Scanned manuscript inscribed! You can now analyze and chat with it above.")
                st.rerun()
