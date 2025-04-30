import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd
from io import BytesIO
import re

st.set_page_config(page_title="Transaction Extractor", layout="wide")

# Header Section
st.markdown("<h1 style='color:#0e76a8;'>📤 Transaction Extractor</h1>", unsafe_allow_html=True)
st.caption("Extract **Paid** and **Received** transactions from your HTML file and download them as an Excel sheet.")

uploaded_file = st.file_uploader("Select your HTML file", type=["html"], label_visibility="visible")

def extract_transaction_data(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    data = []

    for div in soup.find_all("div"):
        text = div.get_text(strip=True)

        if 'Paid' in text or 'Received' in text:
            match = re.search(r"(Paid|Received)\s+(₹[\d,\.]+)\s+.*?(Account\s+\w+|\bUPI\b|\bCard\b|\bWallet\b)[^J]*?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).*", text)
            if match:
                trans_type = match.group(1)
                amount = match.group(2)
                account = match.group(3)
                date_search = re.search(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).*", text)
                date = date_search.group(0) if date_search else ''
                data.append({
                    "Type": trans_type,
                    "Amount": amount,
                    "Account": account,
                    "Date": date
                })
    return pd.DataFrame(data)

def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Transactions")
        workbook = writer.book
        worksheet = writer.sheets["Transactions"]

        # Color coding: Paid = red, Received = green
        for row_idx, value in enumerate(df["Type"], start=2):
            color = "FF0000" if value == "Paid" else "008000"
            worksheet[f"A{row_idx}"].font = worksheet[f"A{row_idx}"].font.copy(color=color)

    return output.getvalue()

if uploaded_file is not None:
    try:
        with st.spinner("🔍 Extracting transactions from file..."):
            html = uploaded_file.read()
            df = extract_transaction_data(html)

        if df.empty:
            st.warning("⚠️ No 'Paid' or 'Received' transactions found in the file.")
        else:
            st.success(f"✅ Successfully extracted {len(df)} transactions.")

            with st.expander("🔎 Preview Extracted Transactions"):
                st.dataframe(df, use_container_width=True)

            st.divider()
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown("### 📥 Download")
            with col2:
                excel_data = convert_df_to_excel(df)
                st.download_button(
                    label="⬇️ Download Excel File",
                    data=excel_data,
                    file_name="transactions.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    except Exception as e:
        st.error(f"❌ Error: {e}")

else:
    st.info("📁 Upload a Activity HTML file to begin.")
