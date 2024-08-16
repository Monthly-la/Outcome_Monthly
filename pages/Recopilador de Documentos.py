import streamlit as st
from io import BytesIO
import pandas as pd


st.set_page_config(
    page_title="Monthly - App Interna",
    page_icon="💸",
    layout="wide"
)

header_logo_1, header_logo_2 = st.columns(2)
with header_logo_1:
    st.image(
                "https://monthly.la/wp-content/uploads/2024/02/Monthly-Logo.png",
                width=200, # Manually Adjust the width of the image as per requirement
            )
with header_logo_2:
    st.markdown("<h2 style='text-align: right; color: #5666FF;'>📑 Recopilador de Documentos</h2>", unsafe_allow_html=True)

st.divider()

def merge_excel_files(excel_files):
    output = BytesIO()
    
    # Create a new Excel writer object
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for uploaded_file in excel_files:
            df = pd.read_excel(uploaded_file)
            # Use the filename (without extension) as the sheet name
            sheet_name = uploaded_file.name.split('.')[0]
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    return output

excel_files  = st.file_uploader("Inserta el Excel (.xlsx, .csv) aquí:", type=['xlsx'], accept_multiple_files=True)


# Create a new Excel workbook
if excel_files:
    # When the user clicks the 'Merge' button
    if st.button("Merge Files"):
        merged_file = merge_excel_files(excel_files)
        
        st.success("Files have been merged successfully!")
        
        # Provide a download link
        st.download_button(
            label="Download Merged Excel",
            data=merged_file.getvalue(),
            file_name="merged_file.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
