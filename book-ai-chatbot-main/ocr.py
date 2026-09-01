import streamlit as st
import os
import io
import pytesseract
from PIL import Image
import pdf2image
import tempfile


def render_ocr_uploader():
    """Upload images or PDFs, run OCR, and store extracted text in session state.
    The extracted text is appended to `st.session_state['ocr_text']` for later ingestion.
    """
    uploaded = st.file_uploader("📄 Upload Image or Scanned PDF for OCR", type=["png", "jpg", "jpeg", "pdf"], accept_multiple_files=False)
    if uploaded is not None:
        if uploaded.type == "application/pdf":
            # Convert each PDF page to image and OCR
            with tempfile.TemporaryDirectory() as tmpdir:
                images = pdf2image.convert_from_bytes(uploaded.read(), fmt="png", output_folder=tmpdir)
                texts = []
                for img in images:
                    txt = pytesseract.image_to_string(img)
                    texts.append(txt)
                ocr_text = "\n".join(texts)
        else:
            # Assume image file
            image = Image.open(uploaded)
            ocr_text = pytesseract.image_to_string(image)
        st.session_state["ocr_text"] = ocr_text
        st.success("OCR completed. Extracted text stored for ingestion.")
        st.write(ocr_text[:500] + "..." if len(ocr_text) > 500 else ocr_text)
