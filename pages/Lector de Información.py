import streamlit as st

st.set_page_config(
    page_title="Monthly - App Interna",
    page_icon="💸",
    layout="wide"
)

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
    st.markdown("<h2 style='text-align: right; color: #5666FF;'>🔎 Lector de Información</h2>", unsafe_allow_html=True)

st.divider()
