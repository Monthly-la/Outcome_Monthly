import streamlit as st
from pptx import Presentation
from pdf2image import convert_from_bytes
from PIL import Image
import openai
import io
import os
import base64


# Configurar tu API key de OpenAI en secrets de Streamlit Cloud
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("✅ Validación de Reporte con GPT-4o")
st.markdown("Sube un archivo `.pptx`. El manual de control de calidad ya está cargado desde el sistema.")

pptx_file = st.file_uploader("📊 Reporte en PowerPoint (.pptx)", type=["pptx"])

# Convertir slides a imágenes
def pptx_to_images(file):
    prs = Presentation(file)
    images = []
    for i, slide in enumerate(prs.slides):
        img = Image.new("RGB", (1280, 720), "white")
        # Puedes renderizar texto si necesitas — opcional
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        images.append(img)
    return images

# Convertir el manual PDF a imágenes
def load_manual_images():
    with open("Monthly. Quality checks.pdf", "rb") as f:
        return convert_from_bytes(f.read(), fmt='png')

# Enviar a OpenAI
def analyze_with_openai(report_imgs, manual_imgs):
    results = []
    for idx, img in enumerate(report_imgs):
        img_byte = io.BytesIO()
        img.save(img_byte, format='PNG')
        img_byte.seek(0)
        img_base64 = base64.b64encode(img_byte.getvalue()).decode("utf-8")

        manual_parts = []
        for mimg in manual_imgs:
            m = io.BytesIO()
            mimg.save(m, format='PNG')
            m.seek(0)
            encoded = base64.b64encode(m.read()).decode("utf-8")
            manual_parts.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{encoded}"}
            })

        messages = [
            {"role": "system", "content": "Eres un experto en presentaciones y control de calidad de reportes financieros."},
            {"role": "user", "content": [
                {"type": "text", "text": "Tengo el siguiente reporte (pptx) y el manual de control de calidad (pdf). Dame tus comentarios y revisa el reporte ppt con los lineamientos mencionados en el manual."},
                {"type": "image_url", "image_url": {"url": "data:image/png;base64," + img_base64}},
                *manual_parts
            ]}
        ]

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=1000
        )

        results.append(f"**Diapositiva {idx+1}:**\n\n" + response.choices[0].message.content)
    return results

if pptx_file:
    with st.spinner("Convirtiendo archivos..."):
        pptx_images = pptx_to_images(pptx_file)
        pdf_images = load_manual_images()

    with st.spinner("Analizando con GPT-4o..."):
        feedbacks = analyze_with_openai(pptx_images, pdf_images)

    st.success("✅ Análisis completo")
    for comment in feedbacks:
        st.markdown(comment)
