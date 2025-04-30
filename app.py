import streamlit as st
import pandas as pd
import json
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

st.markdown("<h1 style='color:#0e76a8;'>📄 JSON to Excel Converter</h1>", unsafe_allow_html=True)
st.markdown("Upload your **JSON file** and download it instantly as an **Excel file**.")

uploaded_file = st.file_uploader("📤 Upload your JSON file", type=["json"])

if uploaded_file is not None:
    try:
        json_data = json.load(uploaded_file)

        # Normalize nested JSON
        df = pd.json_normalize(json_data)

        st.success("✅ JSON file successfully uploaded and processed!")

        st.markdown("### 👁️ Preview of Data")
        st.dataframe(df, use_container_width=True)

        def convert_df_to_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')
            processed_data = output.getvalue()
            return processed_data

        with st.spinner("🔄 Converting to Excel..."):
            excel_data = convert_df_to_excel(df)

        st.markdown("### 📥 Download Your Excel File")
        st.download_button(
            label="⬇️ Download Excel",
            data=excel_data,
            file_name="converted_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
