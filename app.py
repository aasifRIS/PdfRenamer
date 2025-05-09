import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd
from io import BytesIO
import re
from datetime import datetime

# Set the page configuration for a better UI
st.set_page_config(page_title="Transaction Extractor", layout="wide")

# Title and description
st.markdown("<h1 style='color:#0e76a8;'>📤 Transaction Extractor</h1>", unsafe_allow_html=True)
st.caption("Extract **Paid** and **Received** transactions from your HTML file and download them as an Excel sheet.")

# File uploader (keeps in main UI)
uploaded_file = st.file_uploader("Select your HTML file", type=["html"])

# Sidebar with filters
st.sidebar.title("🛠️ Filters & Options")

# Button for showing filters
filter_option = st.sidebar.radio("Choose Filter", ["None", "By Month", "By Date Range"], index=0, key="filter_options")

# Button to show Transaction Summary in sidebar
show_summary = st.sidebar.checkbox("Show Transaction Summary", value=True, key="show_summary")

# Function to extract transaction data from the HTML file
def extract_transaction_data(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    all_lines = [div.get_text(strip=True) for div in soup.find_all("div")]

    # Define the regex pattern for extracting relevant transaction data
    pattern = re.compile(
        r"(Paid|Received)\s+(₹[\d,]+\.\d{2}).*?(Account\s+[A-Z\dXx]+|\bUPI\b|\bCard\b|\bWallet\b).*?(\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}).*?GMT"
    )

    results = []
    seen = None

    for line in all_lines:
        matches = pattern.findall(line)

        for match in matches:
            if len(match) == 5:
                type_, amount, account, date = match[0], match[1], match[2], match[3]

                # Validate the date format (dd Mon yyyy)
                try:
                    date_obj = datetime.strptime(date.strip(), "%d %b %Y")
                    record = (type_, amount, account, date.strip())

                    # Avoid duplicates
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
                except ValueError:
                    continue

    return pd.DataFrame(results)

# Convert DataFrame to Excel format
def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df[["Type", "Amount", "Account", "Date"]].to_excel(writer, index=False, sheet_name="Transactions")
        worksheet = writer.sheets["Transactions"]

        for row_idx, value in enumerate(df["Type"], start=2):
            color = "FF0000" if value == "Paid" else "008000"
            worksheet[f"A{row_idx}"].font = worksheet[f"A{row_idx}"].font.copy(color=color)

    return output.getvalue()

# Filter by Month
def filter_by_month(df, month):
    if month != "All":
        return df[df["Date"].str.contains(month, case=False)]
    return df

# Filter by Date Range
def filter_by_date_range(df, start_date, end_date):
    mask = (df["Date"] >= start_date) & (df["Date"] <= end_date)
    return df[mask]

# UI - Display file upload status and allow filtering by month
if uploaded_file is not None:
    try:
        with st.spinner("🔍 Extracting transactions..."):
            html = uploaded_file.read()
            df = extract_transaction_data(html)

        if df.empty:
            st.warning("⚠️ No 'Paid' or 'Received' transactions found.")
        else:
            # Show Transaction Summary in sidebar if no filter is selected
            if filter_option == "None" and show_summary:
                total_paid = df[df["Type"] == "Paid"]["AmountFloat"].sum()
                total_received = df[df["Type"] == "Received"]["AmountFloat"].sum()
                net = total_received - total_paid

                st.sidebar.subheader("💰 Transaction Summary")
                st.sidebar.text(f"Total Paid: ₹{total_paid:,.2f}")
                st.sidebar.text(f"Total Received: ₹{total_received:,.2f}")
                st.sidebar.text(f"Net: ₹{net:,.2f}")

            # Filter options (month + date range)
            if filter_option == "By Month":
                month_filter = st.sidebar.selectbox("🌜 Select Month", options=["All", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
                filtered_df = filter_by_month(df, month_filter)

            # Filter by Date Range
            elif filter_option == "By Date Range":
                start_date = st.sidebar.date_input("Start Date", min_value=pd.to_datetime("2020-01-01"))
                end_date = st.sidebar.date_input("End Date", min_value=start_date)
                filtered_df = filter_by_date_range(df, start_date.strftime("%d %b %Y"), end_date.strftime("%d %b %Y"))

            else:
                filtered_df = df

            # Show filtered transactions preview
            with st.expander("🔎 Preview Transactions"):
                st.dataframe(filtered_df[["Type", "Amount", "Account", "Date"]], use_container_width=True)

            st.divider()

            # Download button
            st.download_button(
                label="⬇️ Download Excel File",
                data=convert_df_to_excel(filtered_df),
                file_name="transactions.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"❌ Error: {e}")
else:
    st.info("📁 Upload a file to begin.")
