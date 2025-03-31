import requests
import streamlit as st
import tempfile

st.title("📊 Generador de Reportes PAGS")

excel_file = st.file_uploader("Sube el archivo Excel", type=["xlsx"])
logo_file = st.file_uploader("Sube el logo", type=["png", "jpg", "jpeg"])
website = st.text_input("Sitio web", "https://productorags.com.mx/")
industria = st.selectbox("Industria", ["Agricultura", "Construcción", "Tecnología"])
pais = st.selectbox("País", ["🇲🇽 México", "🇨🇱 Chile", "🇨🇴 Colombia"])
periodo = st.selectbox("Periodo", ["📆 Enero 2025", "📆 Febrero 2025", "📆 Marzo 2025"])
moneda = st.selectbox("Moneda", ["💲MXN", "💲CLP", "💲COP"])

if st.button("Generar Presentación"):
    if not all([excel_file, logo_file]):
        st.error("Sube todos los archivos requeridos")
        st.stop()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_excel, \
         tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_logo:

        tmp_excel.write(excel_file.read())
        tmp_logo.write(logo_file.read())
        tmp_excel.flush()
        tmp_logo.flush()

        files = {
            "excel": open(tmp_excel.name, "rb"),
            "image": open(tmp_logo.name, "rb")
        }
        data = {
            "website": website,
            "industria": industria,
            "pais": pais,
            "periodo": periodo,
            "moneda": moneda
        }

        with st.spinner("Procesando..."):
            response = requests.post("https://barrel-exchanges-arabian-paintings.trycloudflare.com/generate_ppt", files=files, data=data)

        if response.status_code == 200:
            st.success("✅ Presentación generada")
            st.download_button("📥 Descargar Presentación", data=response.content, file_name="Reporte_PAGS.pptx")
        else:
            st.error(f"Error: {response.text}")
