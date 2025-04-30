import streamlit as st
import pandas as pd
import json
from io import BytesIO

st.title("JSON to Excel Converter")

uploaded_file = st.file_uploader("Upload your JSON file", type=["json"])

if uploaded_file is not None:
    try:
        json_data = json.load(uploaded_file)
        
        df = pd.json_normalize(json_data)

        st.subheader("Preview of JSON Data")
        st.dataframe(df)

        def convert_df_to_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')
            processed_data = output.getvalue()
            return processed_data

        excel_data = convert_df_to_excel(df)
        st.download_button(
            label="📥 Download Excel file",
            data=excel_data,
            file_name="converted_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Error reading JSON: {e}")
