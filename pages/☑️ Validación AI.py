import streamlit as st
from openai import OpenAI
from pptx import Presentation
from PIL import Image, ImageDraw
import io
import base64
import tempfile

# === CONFIG ===
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Validación AI - PPTX → GPT-4o", layout="wide")

st.title("📊 Validación Automática de Reportes CFO con GPT-4o")
pptx_file = st.file_uploader("📄 Sube tu reporte PowerPoint (.pptx)", type=["pptx"])

# === FUNCIONES ===

def render_slide_as_image(slide, width=1280, height=720):
    """Genera imagen vacía y dibuja el texto de los elementos."""
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    y_offset = 40
    for shape in slide.shapes:
        if hasattr(shape, "text"):
            draw.text((50, y_offset), shape.text, fill="black")
            y_offset += 40
    return img

def pptx_to_base64_images(pptx_bytes):
    """Convierte cada slide en imagen PNG y codifica a base64."""
    prs = Presentation(io.BytesIO(pptx_bytes))
    base64_images = []

    for slide in prs.slides:
        img = render_slide_as_image(slide)
        with io.BytesIO() as output:
            img.save(output, format="PNG")
            b64 = base64.b64encode(output.getvalue()).decode("utf-8")
            base64_images.append(b64)
    return base64_images

def create_gpt4o_payload(images_b64):
    """Arma la estructura para enviar a GPT-4o con múltiples imágenes"""
    visual_inputs = []
    for b64 in images_b64[:5]:  # puedes limitar a 5 slides si quieres
        visual_inputs.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{b64}"
            }
        })
    return visual_inputs

# === PROCESAR ===
if pptx_file:
    st.info("Procesando slides del reporte...")

    pptx_bytes = pptx_file.read()
    slides_b64 = pptx_to_base64_images(pptx_bytes)
    slide_inputs = create_gpt4o_payload(slides_b64)

    st.success(f"{len(slides_b64)} slides convertidas a imágenes ✅")

    st.info("Enviando slides a GPT-4o para revisión...")

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres un experto en análisis financiero. Estás evaluando un reporte trimestral automatizado. "
                        "Analiza las siguientes diapositivas de PowerPoint buscando errores visuales, gráficos mal calibrados, inconsistencias de notación o malas prácticas. "
                        "Responde con observaciones claras, estructuradas por sección (Gráficos, Notación, Tablas, Métricas, etc)."
                    )
                },
                {
                    "role": "user",
                    "content": [
                        { "type": "text", "text": "Aquí están las slides del reporte a revisar:" },
                        *slide_inputs
                    ]
                }
            ],
            max_tokens=1800,
            temperature=0.3
        )

        st.markdown("### ✅ Evaluación del Reporte:")
        st.write(response.choices[0].message.content)

    except Exception as e:
        st.error("❌ Ocurrió un error al llamar a OpenAI.")
        st.exception(e)
