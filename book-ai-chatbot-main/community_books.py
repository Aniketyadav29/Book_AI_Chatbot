"""
community_books.py - Community Book Upload, Admin Approval & Public Library
"""
import streamlit as st
import json
import os
import uuid
import shutil
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent / "user_data" / "community"
PENDING_DIR   = BASE_DIR / "pending"
APPROVED_DIR  = BASE_DIR / "approved"
REJECTED_DIR  = BASE_DIR / "rejected"

for _d in [PENDING_DIR, APPROVED_DIR, REJECTED_DIR]:
    _d.mkdir(parents=True, exist_ok=True)

DOMAINS = [
    "Fiction", "Non-Fiction", "Science & Technology",
    "History & Culture", "Philosophy", "Spirituality & Religion",
    "Biography & Memoir", "Children & Young Adult",
    "Poetry & Literature", "Self-Help & Motivation",
    "Adventure & Travel", "Mystery & Thriller", "Other"
]

SUPPORTED_TYPES = ["pdf", "epub", "docx", "doc", "txt", "md"]


def _get_admin_password() -> str:
    """Read admin password - always reads .env directly so no restart needed."""
    # Use abspath to resolve __file__ correctly regardless of Streamlit cwd
    env_file = Path(os.path.abspath(__file__)).parent / ".env"
    if env_file.exists():
        try:
            content = env_file.read_text(encoding="utf-8-sig")  # utf-8-sig handles BOM
            for line in content.splitlines():
                line = line.strip()
                if line.startswith("ADMIN_PASSWORD="):
                    pwd = line.split("=", 1)[1].strip()
                    if pwd:
                        return pwd
        except Exception:
            pass
    # Fallback: os.environ
    pwd = os.environ.get("ADMIN_PASSWORD", "").strip()
    if pwd:
        return pwd
    # Fallback: Streamlit secrets
    try:
        pwd = st.secrets.get("ADMIN_PASSWORD", "").strip()
        if pwd:
            return pwd
    except Exception:
        pass
    return "admin123"


def save_submission(file_bytes, filename, author_name, domain, description):
    book_id = str(uuid.uuid4())
    ext = Path(filename).suffix.lower()
    file_path = PENDING_DIR / f"{book_id}{ext}"
    file_path.write_bytes(file_bytes)
    meta = {
        "id": book_id,
        "filename": filename,
        "author": author_name.strip(),
        "domain": domain,
        "description": description.strip(),
        "submitted_at": datetime.now().isoformat(),
        "status": "pending",
        "ext": ext,
    }
    with open(PENDING_DIR / f"{book_id}.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    return book_id


def load_submissions(status):
    folder = {"pending": PENDING_DIR, "approved": APPROVED_DIR, "rejected": REJECTED_DIR}.get(status, PENDING_DIR)
    books = []
    for meta_file in sorted(folder.glob("*.json"), reverse=True):
        try:
            with open(meta_file, "r", encoding="utf-8") as f:
                books.append(json.load(f))
        except Exception:
            continue
    return books


def _move_book(book_id, from_status, to_status):
    src_dir = {"pending": PENDING_DIR, "approved": APPROVED_DIR, "rejected": REJECTED_DIR}[from_status]
    dst_dir = {"pending": PENDING_DIR, "approved": APPROVED_DIR, "rejected": REJECTED_DIR}[to_status]
    meta_src = src_dir / f"{book_id}.json"
    if not meta_src.exists():
        return False
    with open(meta_src, "r", encoding="utf-8") as f:
        meta = json.load(f)
    meta["status"] = to_status
    meta[f"{to_status}_at"] = datetime.now().isoformat()
    ext = meta.get("ext", "")
    file_src = src_dir / f"{book_id}{ext}"
    if file_src.exists():
        if to_status != "rejected":
            shutil.move(str(file_src), str(dst_dir / f"{book_id}{ext}"))
        else:
            file_src.unlink()
    meta_src.unlink()
    with open(dst_dir / f"{book_id}.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    return True


def approve_book(book_id):
    return _move_book(book_id, "pending", "approved")


def reject_book(book_id):
    return _move_book(book_id, "pending", "rejected")


def delete_approved_book(book_id):
    meta_path = APPROVED_DIR / f"{book_id}.json"
    if not meta_path.exists():
        return False
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    ext = meta.get("ext", "")
    fp = APPROVED_DIR / f"{book_id}{ext}"
    if fp.exists():
        fp.unlink()
    meta_path.unlink()
    return True


def render_community_upload():
    st.markdown("""
    <div style='background:linear-gradient(135deg,rgba(30,20,10,0.92),rgba(16,11,7,0.97));
        border:1px solid rgba(212,175,55,0.4);border-radius:16px;padding:26px 30px;margin-bottom:24px;'>
        <h3 style='color:#f5dfa3;font-family:Cinzel,serif;margin:0 0 8px 0;'>
            📤 Share Your Book with the Community</h3>
        <p style='color:#c4b595;margin:0;font-size:0.94rem;'>
            Upload your manuscript. Our admin reviews it — approved books appear in the
            Community Library for everyone to discover and download.</p>
    </div>""", unsafe_allow_html=True)

    with st.form("community_upload_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            author_name = st.text_input("✍️ Your Name / Author Name *", placeholder="e.g. Priya Sharma")
            domain = st.selectbox("🏷️ Domain / Genre *", options=DOMAINS)
        with col2:
            description = st.text_area("📝 Short Description *", height=110,
                placeholder="Briefly describe your book — its theme, key ideas, or what makes it special…")
        uploaded = st.file_uploader("📂 Upload Your Book File *", type=SUPPORTED_TYPES,
            help="PDF, EPUB, DOCX, TXT, Markdown")
        st.markdown("<p style='color:#9a8a6a;font-size:0.82rem;'>ℹ️ By submitting, you confirm you have the rights to share this work. All submissions are reviewed before going public.</p>", unsafe_allow_html=True)
        submitted = st.form_submit_button("🚀 Submit for Review", use_container_width=True)

    if submitted:
        errors = []
        if not author_name.strip():
            errors.append("Author name is required.")
        if not description.strip():
            errors.append("Description is required.")
        if uploaded is None:
            errors.append("Please upload a book file.")
        if errors:
            for e in errors:
                st.error(f"⚠️ {e}")
        else:
            book_id = save_submission(uploaded.read(), uploaded.name, author_name, domain, description)
            st.success(f"✅ **'{uploaded.name}'** submitted for review! (ID: `{book_id[:8]}…`)")
            st.balloons()


def render_community_library():
    approved = load_submissions("approved")
    st.markdown("""
    <div style='background:linear-gradient(135deg,rgba(20,14,8,0.9),rgba(12,9,6,0.95));
        border:1px solid rgba(212,175,55,0.35);border-radius:16px;padding:22px 28px;margin-bottom:24px;'>
        <h3 style='color:#f5dfa3;font-family:Cinzel,serif;margin:0 0 6px 0;'>📚 Community Library</h3>
        <p style='color:#c4b595;margin:0;font-size:0.93rem;'>
            Books submitted and approved from our community — free to read and download.</p>
    </div>""", unsafe_allow_html=True)

    if not approved:
        st.markdown("""<div style='background:rgba(20,14,8,0.75);border:1px dashed rgba(212,175,55,0.3);
            border-radius:12px;padding:32px;text-align:center;color:#c4b595;'>
            📭 <strong>No community books yet.</strong><br>
            <span style='font-size:0.9rem;'>Be the first to share your book above!</span></div>""",
            unsafe_allow_html=True)
        return

    all_domains = sorted(set(b.get("domain","Other") for b in approved))
    filter_domain = st.selectbox("🔍 Filter by Genre", ["All Genres"] + all_domains, key="community_domain_filter")
    filtered = approved if filter_domain == "All Genres" else [b for b in approved if b.get("domain") == filter_domain]
    st.markdown(f"<p style='color:#9a8a6a;font-size:0.88rem;margin:4px 0 16px 0;'>Showing <strong>{len(filtered)}</strong> book(s)</p>", unsafe_allow_html=True)

    for i in range(0, len(filtered), 2):
        row = filtered[i:i+2]
        cols = st.columns(2)
        for col, book in zip(cols, row):
            with col:
                _render_book_card(book)


def _render_book_card(book, show_download=True):
    book_id = book.get("id","")
    approved_at = book.get("approved_at", book.get("submitted_at",""))[:10]
    domain_color = {"Fiction":"#e5a97c","Science & Technology":"#7cc8e5","History & Culture":"#c8b97c",
        "Philosophy":"#b07ce5","Poetry & Literature":"#e57ca6","Non-Fiction":"#7ce5b0"}.get(book.get("domain",""),"#c4b595")
    st.markdown(f"""<div style='background:linear-gradient(145deg,rgba(28,20,12,0.95),rgba(16,11,7,0.98));
        border:1px solid rgba(212,175,55,0.3);border-radius:14px;padding:20px 22px;margin-bottom:16px;
        box-shadow:0 6px 20px rgba(0,0,0,0.5);'>
        <div style='display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;'>
            <h4 style='color:#f5dfa3;font-family:Cinzel,serif;margin:0;font-size:0.97rem;line-height:1.3;max-width:72%;word-break:break-word;'>
                📖 {book.get("filename","Unknown")}</h4>
            <span style='background:rgba(212,175,55,0.15);border:1px solid rgba(212,175,55,0.3);
                border-radius:20px;padding:2px 10px;font-size:0.74rem;color:{domain_color};white-space:nowrap;flex-shrink:0;'>
                {book.get("domain","Other")}</span>
        </div>
        <p style='color:#e5c98b;margin:0 0 8px 0;font-size:0.88rem;'>✍️ <strong>{book.get("author","Anonymous")}</strong></p>
        <p style='color:#c4b595;font-size:0.87rem;line-height:1.55;margin:0 0 12px 0;'>{book.get("description","")}</p>
        <p style='color:#7a6a4a;font-size:0.78rem;margin:0;'>📅 Approved: {approved_at}</p>
    </div>""", unsafe_allow_html=True)

    if show_download:
        ext = book.get("ext","")
        fp = APPROVED_DIR / f"{book_id}{ext}"
        if fp.exists():
            with open(fp,"rb") as f:
                st.download_button("⬇️ Download", data=f.read(),
                    file_name=book.get("filename",f"book{ext}"),
                    mime="application/octet-stream",
                    key=f"dl_{book_id}", use_container_width=True)


def render_admin_panel():
    st.markdown("""
    <div style='background:linear-gradient(135deg,rgba(15,10,30,0.95),rgba(8,5,20,0.98));
        border:1px solid rgba(130,90,220,0.45);border-radius:16px;padding:24px 28px;margin-bottom:24px;'>
        <h3 style='color:#c9a8f5;font-family:Cinzel,serif;margin:0 0 6px 0;'>🔐 Admin Control Panel</h3>
        <p style='color:#a090c0;margin:0;font-size:0.93rem;'>
            Review, approve, or reject community book submissions.</p>
    </div>""", unsafe_allow_html=True)

    if not st.session_state.get("admin_authenticated", False):
        st.markdown("#### 🗝️ Admin Login")
        pwd_input = st.text_input("Enter Admin Password", type="password", placeholder="••••••••", key="admin_pwd_input")
        col_login, col_hint = st.columns([1,2])
        with col_login:
            if st.button("🔓 Login", use_container_width=True, key="admin_login_btn"):
                if pwd_input == _get_admin_password():
                    st.session_state.admin_authenticated = True
                    st.success("✅ Authenticated!")
                    st.rerun()
                else:
                    st.error("❌ Incorrect password.")
        with col_hint:
            env_path = Path(os.path.abspath(__file__)).parent / ".env"
            st.caption(f"💡 Set `ADMIN_PASSWORD=yourpassword` in `.env` to change the password.")
            with st.expander("🔍 Debug info", expanded=False):
                st.code(f".env path : {env_path}\n.env found: {env_path.exists()}\nActive pwd : {_get_admin_password()}", language="text")
        return

    col_title, col_logout = st.columns([4,1])
    with col_title:
        st.markdown("### 🛡️ Admin Dashboard")
    with col_logout:
        if st.button("🚪 Logout", key="admin_logout_btn", use_container_width=True):
            st.session_state.admin_authenticated = False
            st.rerun()

    pending  = load_submissions("pending")
    approved = load_submissions("approved")
    rejected = load_submissions("rejected")

    c1, c2, c3 = st.columns(3)
    c1.metric("⏳ Pending", len(pending))
    c2.metric("✅ Approved", len(approved))
    c3.metric("❌ Rejected", len(rejected))
    st.markdown("---")

    t_pend, t_appr, t_rej = st.tabs([
        f"⏳ Pending ({len(pending)})",
        f"✅ Approved ({len(approved)})",
        f"❌ Rejected ({len(rejected)})"
    ])

    with t_pend:
        if not pending:
            st.info("🎉 No pending submissions!")
        else:
            st.markdown(f"**{len(pending)} submission(s) awaiting review:**")
            for book in pending:
                _render_admin_card(book, allow_approve=True, allow_reject=True)

    with t_appr:
        if not approved:
            st.info("No approved books yet.")
        else:
            for book in approved:
                _render_admin_card(book, allow_approve=False, allow_reject=False, allow_delete=True)

    with t_rej:
        if not rejected:
            st.info("No rejected books.")
        else:
            for book in rejected:
                _render_admin_card(book)


def _render_admin_card(book, allow_approve=False, allow_reject=False, allow_delete=False):
    book_id = book.get("id","")
    submitted_at = book.get("submitted_at","")[:16].replace("T"," ")
    st.markdown(f"""<div style='background:linear-gradient(145deg,rgba(18,12,30,0.95),rgba(10,7,20,0.98));
        border:1px solid rgba(130,90,220,0.3);border-radius:13px;padding:18px 22px;margin-bottom:14px;'>
        <div style='display:flex;justify-content:space-between;align-items:flex-start;'>
            <span style='color:#c9a8f5;font-family:Cinzel,serif;font-size:1rem;font-weight:600;'>
                📖 {book.get("filename","Unknown")}</span>
            &nbsp;
            <span style='background:rgba(130,90,220,0.15);border:1px solid rgba(130,90,220,0.3);
                border-radius:20px;padding:2px 10px;font-size:0.74rem;color:#b09ae5;'>
                {book.get("domain","Other")}</span>
        </div>
        <p style='color:#d4b8f5;margin:8px 0 4px 0;font-size:0.88rem;'>
            ✍️ <strong>{book.get("author","Anonymous")}</strong> &nbsp;·&nbsp; 📅 {submitted_at}</p>
        <p style='color:#a090c0;font-size:0.87rem;line-height:1.5;margin:0;'>{book.get("description","")}</p>
    </div>""", unsafe_allow_html=True)

    for folder in [PENDING_DIR, APPROVED_DIR]:
        ext = book.get("ext","")
        fp = folder / f"{book_id}{ext}"
        if fp.exists():
            with open(fp,"rb") as f:
                st.download_button("⬇️ Preview / Download File", data=f.read(),
                    file_name=book.get("filename",f"book{ext}"),
                    mime="application/octet-stream", key=f"admin_dl_{book_id}")
            break

    action_cols = st.columns([1,1,3])
    if allow_approve:
        with action_cols[0]:
            if st.button("✅ Approve", key=f"approve_{book_id}", use_container_width=True):
                if approve_book(book_id):
                    st.success(f"✅ '{book.get('filename')}' approved!")
                    st.rerun()
    if allow_reject:
        with action_cols[1]:
            if st.button("❌ Reject", key=f"reject_{book_id}", use_container_width=True):
                if reject_book(book_id):
                    st.warning(f"❌ '{book.get('filename')}' rejected.")
                    st.rerun()
    if allow_delete:
        with action_cols[0]:
            if st.button("🗑️ Remove", key=f"delete_{book_id}", use_container_width=True,
                         help="Permanently remove from Community Library"):
                if delete_approved_book(book_id):
                    st.warning(f"🗑️ '{book.get('filename')}' removed.")
                    st.rerun()

    st.markdown("<hr style='border-color:rgba(130,90,220,0.15);margin:4px 0 16px 0;'>", unsafe_allow_html=True)
