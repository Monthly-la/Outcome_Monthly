import pandas as pd

uploaded_file = st.file_uploader("Sube tu archivo .pptx", type=["pptx"])

if uploaded_file:
    st.success("Archivo cargado correctamente.")

    # Enviar archivo al webhook de Make
    files = {
        'file': (uploaded_file.name, uploaded_file, uploaded_file.type),
    }

    webhook_url = "https://hook.us1.make.com/1vdd4l5k42vrxywo21twpfaii3ociyqr"  # reemplaza con el tuyo

    response = requests.post(webhook_url, files=files)

    if response.status_code == 200:
        st.success("Enviado correctamente para revisión.")
    else:
        st.error("Error al enviar el archivo.")

