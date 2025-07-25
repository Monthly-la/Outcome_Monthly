import streamlit as st
import openai
from pdf2image import convert_from_bytes
import base64
import io

st.set_page_config(page_title="Validación de Reporte GPT-4o", layout="centered")
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("✅ Validación de Reporte con GPT-4o")
st.markdown("Sube tu reporte ya convertido a `.pdf`. El manual de control de calidad ya está cargado desde el sistema.")

pdf_file = st.file_uploader("📄 Reporte en PDF (convertido desde PowerPoint)", type=["pdf"])

# Convertir el manual PDF a imágenes
def load_manual_images():
    with open("Monthly. Quality checks.pdf", "rb") as f:
        return convert_from_bytes(f.read(), fmt='png')

# Enviar a GPT-4o
def analyze_with_openai(report_imgs, manual_imgs):
    results = []

    manual_parts = []
    for mimg in manual_imgs:
        buf = io.BytesIO()
        mimg.save(buf, format='PNG')
        encoded = base64.b64encode(buf.getvalue()).decode("utf-8")
        manual_parts.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{encoded}"}
        })

    for idx, slide_img in enumerate(report_imgs):
        buf = io.BytesIO()
        slide_img.save(buf, format='PNG')
        slide_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        messages = [
            {"role": "system", "content": "Eres un experto en presentaciones y control de calidad de reportes financieros."},
            {"role": "user", "content": [
                {"type": "text", "text": "Tengo el siguiente reporte (pdf convertido desde pptx) y el manual de control de calidad (pdf). Dame tus comentarios y revisa el reporte con los lineamientos del manual."},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{slide_b64}"}},
                *manual_parts
            ]}
        ]

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=1000
        )

        results.append(f"### 🖼 Página {idx+1}:\n\n{response.choices[0].message.content}")
    return results

if pdf_file:
    with st.spinner("Convirtiendo PDF a imágenes..."):
        pptx_images = convert_from_bytes(pdf_file.read(), fmt="png")
        manual_images = load_manual_images()

    with st.spinner("Analizando con GPT-4o..."):
        feedbacks = analyze_with_openai(pptx_images, manual_images)

    st.success("✅ Análisis completo")
    for comment in feedbacks:
        st.markdown(comment, unsafe_allow_html=True)
