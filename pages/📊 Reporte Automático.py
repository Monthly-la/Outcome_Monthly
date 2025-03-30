import streamlit as st
import pyexcel as p
import pandas as pd
from io import BytesIO
import re
from openpyxl import load_workbook
import os
import tempfile
import datetime
from PIL import Image
from win32com.client import Dispatch
import time
import win32com.client
import openai


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

st.divider()

# === STREAMLIT UI ===
st.title("📊 PAGS Report Automation")

excel_file = st.file_uploader("Upload Excel Model", type=["xlsx"])
ppt_file = st.file_uploader("Upload PowerPoint Template", type=["pptx"])
logo_file = st.file_uploader("Upload Logo Image", type=["png", "jpg", "jpeg"])

industria = st.selectbox("Selecciona la industria:", ["Agricultura", "Construcción", "Manufactura", "Tecnología"])
pais = st.selectbox("Selecciona el país:", ["🇲🇽 México", "🇨🇱 Chile", "🇨🇴 Colombia", "🇵🇪 Perú"])
periodo = st.selectbox("Selecciona el periodo:", ["📆 Enero 2025", "📆 Febrero 2025", "📆 Marzo 2025"])
moneda = st.selectbox("Selecciona la moneda:", ["💲MXN", "💲CLP", "💲COP", "💲PEN"])

website = st.text_input("Website para semblanza (opcional):", value="https://productorags.com.mx/")

if st.button("🛠️ Generar Presentación"):
    if not all([excel_file, ppt_file, logo_file]):
        st.error("🚫 Por favor, sube todos los archivos requeridos.")
        st.stop()

    with tempfile.TemporaryDirectory() as tmpdir:
        excel_path = os.path.join(tmpdir, "model.xlsx")
        ppt_path = os.path.join(tmpdir, "template.pptx")
        logo_path = os.path.join(tmpdir, "logo.png")

        with open(excel_path, "wb") as f: f.write(excel_file.read())
        with open(ppt_path, "wb") as f: f.write(ppt_file.read())
        with open(logo_path, "wb") as f: f.write(logo_file.read())

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_ppt_path = os.path.join(tmpdir, f"PAGS_Reporte_{timestamp}.pptx")

        # === LAUNCH PowerPoint ===
        ppt = Dispatch("PowerPoint.Application")
        ppt.Visible = True
        presentation = ppt.Presentations.Open(ppt_path)

        # === LAUNCH Excel ===
        try:
            excel = win32com.client.Dispatch("Excel.Application")
            time.sleep(1)
            try:
                excel.Visible = False
            except Exception as ve:
                print(f"⚠️ Excel.Visible issue: {ve}")
        except Exception as e:
            st.error("❌ Error al iniciar Excel.")
            st.stop()

        try:
            wb = excel.Workbooks.Open(excel_path, ReadOnly=True)
        except Exception as e:
            st.error("❌ Error al abrir el archivo Excel.")
            st.stop()

        # === INSERT LOGO ON FIRST SLIDE ===
        slide = presentation.Slides(1)
        slide_width = presentation.PageSetup.SlideWidth
        top_position = 640
        max_height = 1020 - top_position

        im = Image.open(logo_path)
        orig_w, orig_h = im.size
        aspect_ratio = orig_w / orig_h

        target_height = max_height
        target_width = target_height * aspect_ratio
        left_position = (slide_width - target_width) / 2

        slide.Shapes.AddPicture(FileName=logo_path, LinkToFile=False, SaveWithDocument=True,
                                Left=left_position, Top=top_position,
                                Width=target_width, Height=target_height)

        # === SEMBLANZA VIA OPENAI (Optional) ===
        try:
            if website.strip():
              # Access the OpenAI API key from the secrets
                api_key = st.secrets["OPENAI_API_KEY"]
                
                openai = OpenAI(api_key=api_key)
                response = openai.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": f"Genera una semblanza de no más de 80 palabras sobre la empresa de este sitio web: {website}"}
                    ]
                )
                semblanza = response.choices[0].message.content.strip()
            else:
                semblanza = ""
        except Exception as e:
            semblanza = ""

        # === REPLACEMENT LABELS ===
        replacements = {
            "Industria": industria,
            "País": pais,
            "Período": periodo,
            "Moneda": moneda,
            "Semblanza": semblanza
        }

        for slide in presentation.Slides:
            for shape in slide.Shapes:
                if shape.HasTextFrame and shape.TextFrame.HasText:
                    original_text = shape.TextFrame.TextRange.Text
                    new_text = original_text
                    for old, new in replacements.items():
                        new_text = new_text.replace(old, new)
                    if new_text != original_text:
                        shape.TextFrame.TextRange.Text = new_text

        try:
            presentation.SaveAs(output_ppt_path)
            st.success("✅ Presentación generada correctamente.")

            with open(output_ppt_path, "rb") as f:
                st.download_button("📥 Descargar Presentación PPT", f, file_name=f"PAGS_Reporte_{timestamp}.pptx")
        except Exception as e:
            st.error(f"❌ Error al guardar la presentación: {e}")

        wb.Close(False)
        excel.Quit()
        #ppt.Quit()
