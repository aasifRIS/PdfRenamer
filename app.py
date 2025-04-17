import streamlit as st
import os
import shutil
from datetime import datetime
import time
from io import BytesIO
import zipfile

st.set_page_config(page_title="📁 PDF ReNinja", layout="centered")

def log_action(entry):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    st.session_state.logs.append(f"[{timestamp}] {entry}")

def safe_filename(name):
    return name.replace(os.sep, "_").replace(" ", "_")

def find_pdfs(folder_path):
    pdf_paths = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".pdf"):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, folder_path)
                pdf_paths.append((full_path, rel_path))
    return pdf_paths

def rename_and_copy_pdfs_local(src_folder):
    parent_dir = os.path.dirname(src_folder)
    folder_name = os.path.basename(src_folder)
    renamed_folder = os.path.join(parent_dir, folder_name + "_renamed")

    if os.path.exists(renamed_folder):
        shutil.rmtree(renamed_folder)
    os.makedirs(renamed_folder, exist_ok=True)

    pdfs = find_pdfs(src_folder)

    for full_path, rel_path in pdfs:
        new_name = safe_filename(os.path.splitext(rel_path)[0]) + ".pdf"
        new_path = os.path.join(renamed_folder, new_name)
        shutil.copy2(full_path, new_path)
        log_action(f"Renamed '{os.path.basename(full_path)}' → '{new_name}'")

    return renamed_folder, len(pdfs)

def rename_uploaded_pdfs(files):
    if not files:
        return None, 0

    output_dir = "renamed_uploaded_pdfs"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    for file in files:
        original_name = os.path.splitext(file.name)[0]
        new_name = safe_filename(original_name) + ".pdf"
        save_path = os.path.join(output_dir, new_name)

        with open(save_path, "wb") as f:
            f.write(file.read())

        log_action(f"Renamed '{file.name}' → '{new_name}'")

    return output_dir, len(files)

def create_zip_of_folder(folder_path):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                filepath = os.path.join(root, file)
                zipf.write(filepath, arcname=file)
    zip_buffer.seek(0)
    return zip_buffer

def apply_ui_styles():
    st.markdown("""
    <style>
        html, body, [class*="st-"] {
            font-family: 'Segoe UI', sans-serif;
        }
        .stTextInput input {
            padding: 10px;
            font-size: 16px;
        }
        .stButton>button {
            border-radius: 8px;
            padding: 10px;
            font-size: 16px;
        }
        .log-box {
            background-color: #1e1e1e;
            color: #ccc;
            border-radius: 10px;
            border: 1px solid #333;
            padding: 12px;
            font-size: 13px;
            max-height: 300px;
            overflow-y: auto;
        }
    </style>
    """, unsafe_allow_html=True)

apply_ui_styles()

if 'logs' not in st.session_state:
    st.session_state.logs = []

# --- Sidebar Settings ---
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    mode = st.radio("Select mode:", ["Local", "Deploy"], index=0)
    dark_mode = st.toggle("🌙 Enable Dark Mode", value=False)
    if dark_mode:
        st.markdown("""
        <style>
            html, body, [class*="st-"] {
                background-color: #0f0f0f !important;
                color: #ddd !important;
            }
            .stTextInput input, .stFileUploader, .stButton>button {
                background-color: #1f1f1f !important;
                color: white !important;
                border: 1px solid #444 !important;
            }
        </style>
        """, unsafe_allow_html=True)

# --- Main UI ---
st.markdown("<h2 style='text-align: center;'>📁 PDF ReNinja</h2>", unsafe_allow_html=True)
st.caption("Rename your PDFs automatically based on their path or filename.")

if mode == "Local":
    folder_path = st.text_input("📂 Enter folder path:", placeholder="e.g. C:/Users/You/Documents/PDFs")

    if folder_path:
        if not os.path.isdir(folder_path):
            st.error("🚫 Invalid folder path.")
        else:
            if st.button("🚀 Start Renaming (Local)"):
                with st.spinner("Renaming PDFs..."):
                    renamed_folder, total = rename_and_copy_pdfs_local(folder_path)
                    time.sleep(1)
                    st.success(f"✅ Renamed {total} PDF(s). Saved to: `{renamed_folder}`")

                if st.session_state.logs:
                    st.markdown("### 📝 Rename Logs")
                    st.markdown(f"<div class='log-box'>{'<br>'.join(st.session_state.logs)}</div>", unsafe_allow_html=True)

elif mode == "Deploy":
    uploaded_files = st.file_uploader("📤 Upload multiple PDF files", type="pdf", accept_multiple_files=True)

    if uploaded_files and st.button("🚀 Start Renaming (Deploy)"):
        with st.spinner("Processing uploaded PDFs..."):
            renamed_folder, total = rename_uploaded_pdfs(uploaded_files)
            zip_file = create_zip_of_folder(renamed_folder)
            time.sleep(1)
            st.success(f"✅ Renamed {total} uploaded PDF(s).")

            st.download_button(
                label="⬇️ Download Renamed PDFs as ZIP",
                data=zip_file,
                file_name="renamed_pdfs.zip",
                mime="application/zip"
            )

        if st.session_state.logs:
            st.markdown("### 📝 Rename Logs")
            st.markdown(f"<div class='log-box'>{'<br>'.join(st.session_state.logs)}</div>", unsafe_allow_html=True)

if st.button("🧹 Clear Logs"):
    st.session_state.logs.clear()
