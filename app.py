import streamlit as st
import pandas as pd
from io import BytesIO

# Custom CSS for better appearance
st.markdown("""
    <style>
        .main {
            background-color: #f9f9f9;
            font-family: 'Segoe UI', sans-serif;
        }
        .stButton > button {
            background-color: #4CAF50;
            color: white;
            border-radius: 8px;
            padding: 10px 24px;
            font-size: 16px;
        }
        .stDownloadButton > button {
            background-color: #0e76a8;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            padding: 10px 24px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='color:#0e76a8;'>📄 HTML Table to Excel Converter</h1>", unsafe_allow_html=True)
st.markdown("Upload an **HTML file** with one or more `<table>` elements. This app will convert them into an Excel workbook.")

uploaded_file = st.file_uploader("📤 Upload your HTML file", type=["html", "htm"])

if uploaded_file is not None:
    try:
        # Read all tables from HTML
        tables = pd.read_html(uploaded_file)

        if not tables:
            st.warning("⚠️ No tables found in the HTML file.")
        else:
            st.success(f"✅ Found {len(tables)} table(s) in the HTML file!")

            for idx, table in enumerate(tables):
                st.markdown(f"### 👁️ Preview of Table {idx + 1}")
                st.dataframe(table, use_container_width=True)

            def convert_tables_to_excel(tables):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    for i, table in enumerate(tables):
                        sheet_name = f"Table_{i+1}"
                        table.to_excel(writer, index=False, sheet_name=sheet_name)
                return output.getvalue()

            with st.spinner("🔄 Converting tables to Excel..."):
                excel_data = convert_tables_to_excel(tables)

            st.markdown("### 📥 Download Your Excel File")
            st.download_button(
                label="⬇️ Download Excel",
                data=excel_data,
                file_name="converted_tables.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"❌ Error processing HTML file: {e}")
