import streamlit as st
import os
import tempfile
import datetime
import requests

# === STREAMLIT UI ===
st.set_page_config(page_title="PAGS PPT Generator", layout="centered")
st.title("📊 PAGS Report Automation")

excel_file = st.file_uploader("Upload Excel Model", type=["xlsx"])
logo_file = st.file_uploader("Upload Logo Image", type=["png", "jpg", "jpeg"])

industria = st.selectbox("Selecciona la industria:", ["Agricultura", "Construcción", "Manufactura", "Tecnología"])
pais = st.selectbox("Selecciona el país:", ["🇲🇽 México", "🇨🇱 Chile", "🇨🇴 Colombia", "🇵🇪 Perú"])
periodo = st.selectbox("Selecciona el periodo:", ["📆 Enero 2025", "📆 Febrero 2025", "📆 Marzo 2025"])
moneda = st.selectbox("Selecciona la moneda:", ["💲MXN", "💲CLP", "💲COP", "💲PEN"])

website = st.text_input("Website para semblanza (opcional):", value="https://productorags.com.mx/")
cloudflare_url = st.text_input("Cloudflare Tunnel URL:", value="https://<tu-túnel>.trycloudflare.com")



def generate_ppt_report():
    if not all([excel_file, logo_file]):
        st.error("🚫 Por favor, sube todos los archivos requeridos.")
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        excel_path = os.path.join(tmpdir, "model.xlsx")
        logo_path = os.path.join(tmpdir, "logo.png")

        with open(excel_path, "wb") as f: f.write(excel_file.read())
        with open(logo_path, "wb") as f: f.write(logo_file.read())

        # Prepare request payload
        files = {
            "excel": open(excel_path, "rb"),
            "logo": open(logo_path, "rb")
        }
        data = {
            "website": website,
            "industria": industria,
            "pais": pais,
            "periodo": periodo,
            "moneda": moneda
        }

        # Call Flask server
        try:
            response = requests.post(
                f"{cloudflare_url}/generate_ppt",
                files=files,
                data=data
            )
            if response.status_code == 200:
                output_filename = f"PAGS_Reporte_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx"
                st.success("✅ Presentación generada correctamente.")
                st.download_button("📥 Descargar Presentación PPT", response.content, file_name=output_filename)
            else:
                st.error(f"❌ Error en el servidor: {response.status_code}\n{response.text}")
        except Exception as e:
            st.error(f"❌ No se pudo contactar con el servidor: {e}")


if st.button("🛠️ Generar Presentación"):
    generate_ppt_report()
