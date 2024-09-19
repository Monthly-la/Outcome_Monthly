import streamlit as st

st.set_page_config(
    page_title="Monthly - App Interna",
    page_icon="💸",
    layout="wide"
)

header_logo_1, header_logo_2 = st.columns(2)
with header_logo_1:
    st.image(
                "https://monthly.la/wp-content/uploads/2024/02/Monthly-Logo.png",
                width=200, # Manually Adjust the width of the image as per requirement
            )
with header_logo_2:
    st.markdown("<h2 style='text-align: right; color: #5666FF;'>🏠 Inicio</h2>", unsafe_allow_html=True)

st.divider()
st.markdown("")

st.markdown("<h3 style='text-align: center; color: #14E79D​;'>Ⓜ️ MODELO DE SERVICIO</h3>", unsafe_allow_html=True)
st.markdown("")

cl_prospeccion, cl_venta, cl_onboarding, cl_operaciones, cl_postventa, cl_recursos = st.columns(6)

with cl_prospeccion:
    st.markdown("<h3 style='text-align: center; color: #5666FF;'> Prospección</h3>", unsafe_allow_html=True)
    st.markdown("")
    st.link_button("Substack", "https://visualcfo.substack.com/", use_container_width=True)
    st.link_button("Linktree (Monthly)", "https://linktr.ee/monthlyla", use_container_width=True)
    st.link_button("Linktree (Valora)", "https://linktr.ee/valora.la", use_container_width=True)
    st.link_button("Tidycal (Demo)", "https://tidycal.com/jona/monthly-demo-30", use_container_width=True)
    st.link_button("Website (Monthly)", "https://monthly.la/", use_container_width=True)
    st.link_button("Website (Valora)", "https://valora.la/", use_container_width=True)
    st.link_button("Instagram", "https://www.instagram.com/monthly.la/", use_container_width=True)
    st.link_button("LInkedin", "https://www.linkedin.com/company/monthlyla/", use_container_width=True)
    
    
with cl_venta:
    st.markdown("<h3 style='text-align: center; color: #5666FF;'> Venta</h3>", unsafe_allow_html=True)
    st.markdown("")
    st.link_button("Linktree (Start)", "https://linktr.ee/monthly.start", use_container_width=True)
    st.link_button("PDF Comercial - Brochure", "https://monthlyla-my.sharepoint.com/:b:/g/personal/arturo_monthly_la/EbEPyt-8V7lPk08nF75nyBABWjO2izBwqfXgkfo4VPO4rA?e=r6N2dO", use_container_width=True)
    st.link_button("PDF Comercial - Presentación", "https://monthlyla-my.sharepoint.com/:b:/g/personal/arturo_monthly_la/EXDdSWXKW9xOvu-XiZtZCeYB2wrs_aEoddLezXgsxY7W4A?e=Aan92l", use_container_width=True)
    st.link_button("Notion (Payment Links)", "https://www.notion.so/Stripe-links-4a6b8046b85d4959a458239ff184020c", use_container_width=True)
    st.link_button("CRM", "https://airtable.com/app2GD2pTpJAZ8JEq/tblmo0rAeoOju6yYu/viw0d5JhbaF9EbCcp?blocks=hide", use_container_width=True)
    st.link_button("Fillout (Subscripción de Cliente)", "https://forms.fillout.com/t/xrzArzx8guus", use_container_width=True)

with cl_onboarding:
    st.markdown("<h3 style='text-align: center; color: #5666FF;'> Onboarding</h3>", unsafe_allow_html=True)
    st.markdown("")
    st.link_button("Fillout (Cuestionario Kick-Off)", "https://forms.fillout.com/t/sxy9ZqBnFtus", use_container_width=True)
    st.link_button("Fillout (Documentos Iniciales)", "https://forms.fillout.com/t/aBDtnmSDpPus", use_container_width=True)
    st.link_button("Fillout (Evaluación Cualitativa)", "https://forms.fillout.com/t/4k6d6cQmYRus", use_container_width=True)

with cl_operaciones:
    st.markdown("<h3 style='text-align: center; color: #5666FF;'> Operaciones</h3>", unsafe_allow_html=True)
    st.markdown("")
    st.link_button("Plataforma Interna", "https://outcome-monthly.streamlit.app/", use_container_width=True)
    st.link_button("Manual de Nuevo Reporte", "", use_container_width=True)
    st.link_button("Excel (Graficación)", "https://monthlyla.sharepoint.com/:x:/s/monthly.la/EWB3hy7QuFBPp8bE4fJOhIwBb3MxBX8ZHjMPeSg6ZYmfsA?e=eJE90X", use_container_width=True)
    st.link_button("Ppt (ReporteCFO)", "https://monthlyla.sharepoint.com/:p:/s/monthly.la/ESOkjEa_ONNCmIDnjoHWQIMBBnPnc8BcT5mLChupGsBCyQ?e=x60h1j", use_container_width=True)
    st.link_button("Sankey", "https://www.sankeyart.com/", use_container_width=True)
    st.link_button("Fillout (Documentos Mensuales)", "https://forms.fillout.com/t/vzB2cu9gHDus", use_container_width=True)
    st.link_button("ChatGPT (Monthly)", "", use_container_width=True)
    st.link_button("Weekly Pulse (TGIM)", "https://forms.office.com/Pages/DesignPageV2.aspx?origin=NeoPortalPage&subpage=design&id=tk7h7DvZskO0b7FLepIvPWStz4K_-KlJj4uTVyohkktUOU9OMEM3Tk5EQ1NaTUhZQzNYMFBNQjc0VC4u&topview=Prefill", use_container_width=True)

with cl_postventa:
    st.markdown("<h3 style='text-align: center; color: #5666FF;'> Postventa</h3>", unsafe_allow_html=True)
    st.markdown("")
    st.link_button("Solicitud de Modificaciones", "https://forms.fillout.com/t/wcdh4d4kpLus", use_container_width=True)

with cl_recursos:
    st.markdown("<h3 style='text-align: center; color: #5666FF;'> Recursos</h3>", unsafe_allow_html=True)
    st.markdown("")
    st.link_button("Cursos de Excel", "", use_container_width=True)
    st.link_button("Cursos de PPT", "", use_container_width=True)
    st.link_button("Manual Financiero", "https://www.notion.so/Monthly-Way-El-iQ-del-CFO-Virtual-48e24fbc16334c109db479810d88e2b3", use_container_width=True)

st.markdown("")
st.divider()
st.markdown("")
st.image("Monthly. Arquitectura de Datos.svg")
    
