import streamlit as st
import pyexcel as p
import pandas as pd
from io import BytesIO


st.set_page_config(
    page_title="Monthly - App Interna",
    page_icon="💸",
    layout="wide"
)
primary_clr = st.get_option("theme.primaryColor")


st.markdown("""
<style>
button {
    background-color: #14E79D;
}
</style>
""", unsafe_allow_html=True)

header_logo_1, header_logo_2 = st.columns(2)
with header_logo_1:
    st.image(
                "https://monthly.la/wp-content/uploads/2024/02/Monthly-Logo.png",
                width=200, # Manually Adjust the width of the image as per requirement
            )
with header_logo_2:
    st.markdown("<h2 style='text-align: right; color: #5666FF;'>Gestión de Efectivo</h2>", unsafe_allow_html=True)

st.divider()


data = {
    "Date": pd.to_datetime(["2024-10-01", "2024-10-05", "2024-10-10"]),
    "Description": ["Salary", "Groceries", "Electric Bill"],
    "Category": ["Income", "Expense", "Expense"],
    "Amount": [3000, -100, -150],
}

# Create a pandas DataFrame
df = pd.DataFrame(data)

# Display the editable table using st.data_editor()
edited_df = st.data_editor(df, num_rows="dynamic")

# Calculate total income, expenses, and balance
income = edited_df[edited_df["Category"] == "Income"]["Amount"].sum()
expenses = edited_df[edited_df["Category"] == "Expense"]["Amount"].sum()
balance = income + expenses

# Display summary metrics
st.write("## Summary")
col1, col2, col3 = st.columns(3)
col1.metric("Total Income", f"${income:.2f}")
col2.metric("Total Expenses", f"${-expenses:.2f}")
col3.metric("Balance", f"${balance:.2f}")

# Allow user to download the data as CSV
csv = edited_df.to_csv(index=False)
st.download_button("Download Data as CSV", csv, "cash_management.csv", "text/csv")

# Allow user to add new rows to the table
if st.button("Add Transaction"):
    new_row = pd.DataFrame({"Date": [pd.to_datetime("2024-10-20")], 
                            "Description": ["New Transaction"], 
                            "Category": ["Expense"], 
                            "Amount": [-50]})
    edited_df = pd.concat([edited_df, new_row], ignore_index=True)
    st.experimental_rerun()
