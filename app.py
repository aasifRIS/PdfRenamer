import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd
from io import BytesIO
import re

st.set_page_config(page_title="Transaction Extractor", layout="wide")

st.markdown("<h1 style='color:#0e76a8;'>📤 Transaction Extractor</h1>", unsafe_allow_html=True)
st.caption("Extract **Paid** and **Received** transactions from your HTML file and download them as an Excel sheet.")

uploaded_file = st.file_uploader("Select your HTML file", type=["html"])

def extract_transaction_data(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    all_lines = [div.get_text(strip=True) for div in soup.find_all("div")]

    pattern = re.compile(
        r"(Paid|Received)\s+(₹[\d,]+\.\d{2}).*?(Account\s+[A-Z\dXx]+|\bUPI\b|\bCard\b|\bWallet\b).*?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec.*?)GMT"
    )

    results = []
    seen = None

    for line in all_lines:
        matches = pattern.findall(line)
        for match in matches:
            type_, amount, account, date = match
            record = (type_, amount, account, date)

            # Only add if it's not the same as the last one (consecutive duplicate)
            if record != seen:
                seen = record
                amount_float = float(amount.replace("₹", "").replace(",", ""))
                results.append({
                    "Type": type_,
                    "Amount": amount,
                    "Account": account,
                    "Date": date.strip(),
                    "AmountFloat": amount_float
                })

    df = pd.DataFrame(results)
    return df

def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df[["Type", "Amount", "Account", "Date"]].to_excel(writer, index=False, sheet_name="Transactions")
        worksheet = writer.sheets["Transactions"]

        for row_idx, value in enumerate(df["Type"], start=2):
            color = "FF0000" if value == "Paid" else "008000"
            worksheet[f"A{row_idx}"].font = worksheet[f"A{row_idx}"].font.copy(color=color)

    return output.getvalue()

if uploaded_file is not None:
    try:
        with st.spinner("🔍 Extracting transactions..."):
            html = uploaded_file.read()
            df = extract_transaction_data(html)

        if df.empty:
            st.warning("⚠️ No 'Paid' or 'Received' transactions found.")
        else:
            total_paid = df[df["Type"] == "Paid"]["AmountFloat"].sum()
            total_received = df[df["Type"] == "Received"]["AmountFloat"].sum()
            net = total_received - total_paid

            st.subheader("💰 Transaction Summary")
            st.metric("Total Paid", f"₹{total_paid:,.2f}")
            st.metric("Total Received", f"₹{total_received:,.2f}")
            st.metric("Net", f"₹{net:,.2f}")

            with st.expander("🔎 Preview Transactions"):
                st.dataframe(df[["Type", "Amount", "Account", "Date"]], use_container_width=True)

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
    st.info("📁 Upload a file to begin.")
