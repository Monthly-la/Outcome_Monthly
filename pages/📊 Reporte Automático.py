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
    st.markdown("<h2 style='text-align: right; color: #5666FF;'>📊 Reporte Automático</h2>", unsafe_allow_html=True)

st.divider()


fillout_embed_code = """
<div style="width:100%;height:500px;" 
     data-fillout-id="juf1xp5BPdus" 
     data-fillout-embed-type="standard" 
     data-fillout-inherit-parameters 
     data-fillout-dynamic-resize>
</div>
<script src="https://server.fillout.com/embed/v1/"></script>
"""

# Embed the form
components.html(fillout_embed_code, height=600, scrolling=True)
