import streamlit as st
import base64
from openai import OpenAI

# === CONFIGURACIÓN ===
st.set_page_config(
    page_title="Monthly - App Interna",
    page_icon="💸",
    layout="wide"
)

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# === ESTILO ===
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
    st.image("./Logo. Monthly Oficial.png", width=250)
with header_logo_2:
    st.markdown("<h2 style='text-align: right; color: #5666FF;'>☑️ Validación AI</h2>", unsafe_allow_html=True)

# === SUBIR ARCHIVO ===
pptx_file = st.file_uploader("📄 Sube tu reporte PowerPoint (.pptx)", type=["pptx"])

# === CARGAR MANUAL FIJO (.pdf) ===
with open("Monthly. Quality checks.pdf", "rb") as f:
    manual_pdf_bytes = f.read()
    manual_pdf_base64 = base64.b64encode(manual_pdf_bytes).decode("utf-8")

# === PROCESAR ARCHIVO DEL USUARIO ===
if pptx_file:
    pptx_bytes = pptx_file.read()
    pptx_base64 = base64.b64encode(pptx_bytes).decode("utf-8")

    st.info("Procesando el reporte con GPT-4 Vision...")

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres un experto en revisión de reportes financieros. "
                        "Evalúa un archivo PowerPoint según las buenas prácticas contenidas en un manual PDF. "
                        "Identifica errores, inconsistencias y oportunidades de mejora. "
                        "Estructura la respuesta por secciones: Resumen, Gráficos, Tablas, Notación, Métricas, Comparativos, Ciclo de Conversión. "
                        "Termina con una tabla de acciones concretas."
                    )
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
            temperature=0.4,
            max_tokens=2000
        )

        st.markdown("### ✅ Evaluación del Reporte:")
        st.write(response.choices[0].message.content)

    except Exception as e:
        st.error("❌ Ocurrió un error al llamar a OpenAI. Revisa tu clave o los archivos subidos.")
        st.exception(e)
