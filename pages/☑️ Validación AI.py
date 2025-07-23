import pandas as pd
import streamlit as st
import pyexcel as p
import pandas as pd
from io import BytesIO
import numpy as np
import re
from openpyxl import load_workbook


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
                "./Logo. Monthly Oficial.png",
                width=250, # Manually Adjust the width of the image as per requirement
            )
with header_logo_2:
    st.markdown("<h2 style='text-align: right; color: #5666FF;'>✅ Procesador de Balanzas de Comprobación</h2>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Sube tu archivo .pptx", type=["pptx"])

if uploaded_file:
    st.success("Archivo cargado correctamente.")

    # Enviar archivo al webhook de Make
    files = {
        'file': (uploaded_file.name, uploaded_file, uploaded_file.type),
    }

    webhook_url = "https://hook.us1.make.com/1vdd4l5k42vrxywo21twpfaii3ociyqr"  # reemplaza con el tuyo

    response = requests.post(webhook_url, files=files)

    if response.status_code == 200:
        st.success("Enviado correctamente para revisión.")
    else:
        st.error("Error al enviar el archivo.")

