import streamlit as st
import streamlit.components.v1 as components

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
                "./Logo. Monthly Oficial.png",
                width=250, # Manually Adjust the width of the image as per requirement
            )
with header_logo_2:
    st.markdown("<h2 style='text-align: right; color: #5666FF;'>🔎 Lector de Información</h2>", unsafe_allow_html=True)

st.divider()


components.html(
    """<iframe class="airtable-embed" src="https://airtable.com/embed/appDnGQVYvyrjZXik/shrcbjueA1qez2Dzx?viewControls=on" frameborder="0" onmousewheel="" width="100%" height="533" style="background: transparent; border: 1px solid #ccc;"></iframe>""",
    height=600,
)
