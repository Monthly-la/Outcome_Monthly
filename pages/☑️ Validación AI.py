import pandas as pd
import streamlit as st
import pyexcel as p
import pandas as pd
from io import BytesIO
import numpy as np
import re
from openpyxl import load_workbook
import openai
import requests
import openai
import base64

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
    st.markdown("<h2 style='text-align: right; color: #5666FF;'>☑️ Validación AI</h2>", unsafe_allow_html=True)

api_key = st.secrets["OPENAI_API_KEY"]
openai.api_key = st.secrets["OPENAI_API_KEY"]


# Subir archivo del usuario
pptx_file = st.file_uploader("📄 Sube tu reporte PowerPoint (.pptx)", type=["pptx"])

# Cargar manual fijo (PDF)
with open("Monthly. Quality checks.pdf", "rb") as f:
    manual_pdf_bytes = f.read()
    manual_pdf_base64 = base64.b64encode(manual_pdf_bytes).decode("utf-8")

# Procesar
if pptx_file:
    pptx_bytes = pptx_file.read()
    pptx_base64 = base64.b64encode(pptx_bytes).decode("utf-8")

    # Armar payload
    response = openai.ChatCompletion.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "system",
                "content": "Eres un experto en revisión de reportes financieros. Evalúa un archivo PowerPoint según las buenas prácticas contenidas en un manual PDF. Identifica errores, inconsistencias y oportunidades de mejora. Estructura la respuesta por secciones: Resumen, Gráficos, Tablas, Notación, Métricas, Comparativos, Ciclo de Conversión. Termina con una tabla de acciones concretas."
            },
            {
                "role": "user",
                "content": [
                    { "type": "text", "text": "Este es el reporte a revisar (.pptx):" },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:application/vnd.openxmlformats-officedocument.presentationml.presentation;base64,{pptx_base64}"
                        }
                    },
                    { "type": "text", "text": "Este es el manual de revisión (.pdf):" },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:application/pdf;base64,{manual_pdf_base64}"
                        }
                    }
                ]
            }
        ],
        max_tokens=2000,
        temperature=0.4
    )

    # Mostrar respuesta
    st.markdown("### ✅ Evaluación del Reporte:")
