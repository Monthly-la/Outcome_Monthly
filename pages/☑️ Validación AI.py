import streamlit as st
from pptx import Presentation
from pdf2image import convert_from_bytes
from PIL import Image
import openai
import io
import os

# API Key
openai.api_key = st.secrets["OPENAI_API_KEY"]  # Defínelo en Secrets de Streamlit Cloud

st.title("✅ Validación de Reporte con GPT-4o")
st.markdown("Sube un archivo `.pptx` y el manual en `.pdf`. Analizaremos el reporte basado en los lineamientos del manual.")

pptx_file = st.file_uploader("📊 Reporte en PowerPoint (.pptx)", type=["pptx"])
pdf_file = st.file_uploader("📄 Manual de control de calidad (.pdf)", type=["pdf"])

def pptx_to_images(file):
    prs = Presentation(file)
    images = []
    for i, slide in enumerate(prs.slides):
        img = Image.new("RGB", (1280, 720), "white")
        for shape in slide.shapes:
            if shape.has_text_frame:
                text = shape.text
                # Dibujar texto sobre imagen (mock)
                Image.Image.paste(img, Image.new("RGB", (0, 0)), (0, 0))
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        images.append(img)
    return images

def pdf_to_images(file):
    return convert_from_bytes(file.read(), fmt='png')

def analyze_with_openai(report_imgs, manual_imgs):
    results = []
    for idx, img in enumerate(report_imgs):
        img_byte = io.BytesIO()
        img.save(img_byte, format='PNG')
        img_byte.seek(0)

        manual_bytes = []
        for mimg in manual_imgs:
            m = io.BytesIO()
            mimg.save(m, format='PNG')
            m.seek(0)
            manual_bytes.append({"image": m.read(), "mime_type": "image/png"})

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Eres un experto en presentación de informes financieros."},
                {"role": "user", "content": [
                    {"type": "text", "text": "Tengo el siguiente reporte (pptx) y el manual de control de calidad (pdf). Dame tus comentarios y revisa el reporte ppt con los lineamientos mencionados en el manual."},
                    {"type": "image_url", "image_url": {"url": "data:image/png;base64," + img_byte.getvalue().hex()}},
                    *[
                        {"type": "image_url", "image_url": {"url": "data:image/png;base64," + m.read().hex()}}
                        for m in manual_bytes
                    ]
                ]}
            ],
            max_tokens=1000
        )
        results.append(f"**Diapositiva {idx+1}:**\n\n" + response.choices[0].message.content)
    return results

if pptx_file and pdf_file:
    with st.spinner("Convirtiendo archivos..."):
        pptx_images = pptx_to_images(pptx_file)
        pdf_images = pdf_to_images(pdf_file)

    with st.spinner("Analizando con GPT-4o..."):
        feedbacks = analyze_with_openai(pptx_images, pdf_images)

    st.success("✅ Análisis completo")
    for comment in feedbacks:
        st.markdown(comment)
