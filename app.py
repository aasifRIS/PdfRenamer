import streamlit as st
import os
import shutil
from datetime import datetime
import time

st.set_page_config(page_title="📁 PDF ReNinja", layout="centered")

def log_action(entry):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    st.session_state.logs.append(f"[{timestamp}] {entry}")

def find_pdfs(folder_path):
    pdf_paths = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".pdf"):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, folder_path)
                pdf_paths.append((full_path, rel_path))
    return pdf_paths

def safe_filename(name):
    return name.replace(os.sep, "_").replace(" ", "_")

def rename_and_copy_pdfs(src_folder):
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

st.markdown("<h2 style='text-align: center;'>📁 PDF ReNinja</h2>", unsafe_allow_html=True)
st.caption("Select a folder and automatically rename all PDFs inside subfolders based on their path.")

with st.sidebar:
    st.markdown("## ⚙️ Settings")
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

# ---- Main UI ----
folder_path = st.text_input("📂 Enter or paste the full path to your folder:", placeholder="e.g. C:/Users/John/Documents/PDFs")

if folder_path:
    if not os.path.isdir(folder_path):
        st.error("🚫 The path entered is not a valid folder.")
    else:
        if st.button("🚀 Start Renaming PDFs"):
            with st.spinner("Scanning and renaming PDFs..."):
                renamed_folder, total = rename_and_copy_pdfs(folder_path)
                time.sleep(1)
                st.success(f"✅ Renamed {total} PDF(s) and saved to: `{renamed_folder}`")

            if st.session_state.logs:
                st.markdown("### 📝 Rename Logs")
                st.markdown(f"<div class='log-box'>{'<br>'.join(st.session_state.logs)}</div>", unsafe_allow_html=True)

        if st.button("🧹 Clear Logs"):
            st.session_state.logs.clear()
