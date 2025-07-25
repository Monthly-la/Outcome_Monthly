import streamlit as st
import openai
from pdf2image import convert_from_bytes
import tempfile
import base64
import io
import os
import subprocess

st.set_page_config(page_title="Validación de Reporte GPT-4o", layout="centered")

openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("✅ Validación de Reporte con GPT-4o")
st.markdown("Sube un archivo `.pptx`. El manual de control de calidad ya está cargado desde el sistema.")

pptx_file = st.file_uploader("📊 Reporte en PowerPoint (.pptx)", type=["pptx"])

# Convertir PPTX a PDF usando libreoffice y luego a imágenes
def pptx_to_images(file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pptx") as tmp_pptx:
        tmp_pptx.write(file.read())
        tmp_pptx.flush()
        output_pdf = tmp_pptx.name.replace(".pptx", ".pdf")
        subprocess.run(["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", os.path.dirname(output_pdf), tmp_pptx.name])
        with open(output_pdf, "rb") as f:
            images = convert_from_bytes(f.read(), fmt="png")
    return images

# Convertir manual PDF a imágenes
def load_manual_images():
    with open("Monthly. Quality checks.pdf", "rb") as f:
        return convert_from_bytes(f.read(), fmt='png')

# Enviar a OpenAI
def analyze_with_openai(report_imgs, manual_imgs):
    results = []

    # Convertir manual a base64 solo una vez
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
                {"type": "text", "text": "Tengo el siguiente reporte (pptx) y el manual de control de calidad (pdf). Dame tus comentarios y revisa el reporte ppt con los lineamientos mencionados en el manual."},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{slide_b64}"}},
                *manual_parts
            ]}
        ]

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=1000
        )

        results.append(f"### 🖼 Diapositiva {idx+1}:\n\n{response.choices[0].message.content}")

    return results

if pptx_file:
    with st.spinner("Convirtiendo archivos..."):
        pptx_images = pptx_to_images(pptx_file)
        pdf_images = load_manual_images()

    with st.spinner("Analizando con GPT-4o..."):
        feedbacks = analyze_with_openai(pptx_images, pdf_images)

    st.success("✅ Análisis completo")
    for comment in feedbacks:
        st.markdown(comment, unsafe_allow_html=True)
