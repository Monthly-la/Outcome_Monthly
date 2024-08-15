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
    st.markdown("<h2 style='text-align: right; color: #5666FF;'>✅ Procesador de Balanzas de Comprobación</h2>", unsafe_allow_html=True)

st.divider()
import streamlit as st
import pandas as pd
from io import BytesIO

processor1, paddingA, processor2, paddingB, processor3 = st.columns([5,1,5,1,5])
with processor1:
    st.markdown("<h2 style='text-align: center; color: #14E79D; font-weight: bolder;'>PASO ☝️</h2>"+"<p style='text-align: center; color: #5666FF; font-weight: bold;'>Selecciona el ERP contable y sube el archivo</p>", unsafe_allow_html=True)
    st.markdown("")
    
    option = st.selectbox(
        "ERP:",
        ("Alpha ERP","Contpaqi","Contalink", "Microsip", "SAP", "Netsuite (Oracle)"))




    uploaded_file = st.file_uploader("Inserta el Excel (.xlsx, .csv) aquí:", type=['xlsx'])

def process_data(df, option = option):
    tabs = list(df.keys())

#Microsip
    if option == "Microsip":
        outcome_df = pd.DataFrame(["","","",""], ["Cuenta", "Nombre", "Saldo Neto", "Sheet"]).T

        for tab in tabs:
            #Microsip Dataframe
            df = pd.read_excel(uploaded_file, sheet_name = tab)
            df = df.fillna(0)
            
            df.columns = df.loc[4]
            df = df.loc[5:].reset_index().drop(columns = {"index",0})
            
            type_of_Cuenta = []
            for i in list(df["Cuenta"]):
                type_of_Cuenta.append(type(i))
            
            df["Type"] = type_of_Cuenta
            df = df[df["Type"] == type("str")]
            df = df[:-1]
            df = df[df["Cuenta"] != "Fecha"]
            
            nivel_list = []
            for i in list(df["Cuenta"]):
                nivel_list.append(len(i.split(".")))
            
            df["Nivel"] = nivel_list
            class_of_cuenta = []
            for i in list(df["Cuenta"]):
                class_of_cuenta.append(i[0])
            
            df["Class"] = class_of_cuenta
            df["Class"] = df["Class"].astype("int")
            
            df.columns = ["Cuenta", "Nombre", "Saldo Inicial Deudor", "Saldo Inicial Acreedor", "Debe", "Haber", "Saldo Final Deudor", "Saldo Final Acreedor", "Tipo", "Nivel", "Clase"]
            df["Saldo Neto"] = df["Saldo Final Deudor"] - df["Saldo Final Acreedor"]
            
            #Microsip Validación
            activos = df[(df["Nivel"] == 1) & (df["Clase"] == 1)]["Saldo Neto"].sum()
            pasivos = df[(df["Nivel"] == 1) & (df["Clase"] == 2)]["Saldo Neto"].sum()
            capital= df[(df["Nivel"] == 1) & (df["Clase"] == 3)]["Saldo Neto"].sum()
            utilidad_acum = df[(df["Nivel"] == 1) & (df["Clase"] >= 4)]["Saldo Neto"].sum()
            
            result = round(activos+pasivos+capital+utilidad_acum,1)

            results_df = pd.DataFrame({"Cuentas": ["Activos", "Pasivos", "Capital", "Utilidad Acumulada", "Sumatoria Final"], 
                                    "Resultado":[activos, pasivos, capital, utilidad_acum, result]})
            
            if result == 0:
                st.caption(tab + " - Check ✅")
            else:
                st.caption(tab + " - No Check ❌")
            
            st.dataframe(results_df, width = 1000)
            st.divider()


            #Outcome Matrix

            balance_df = df[(df["Nivel"] == 1) & (df["Clase"] <= 3)][["Cuenta","Nombre","Saldo Neto"]]
            balance_df["Sheet"] = tab

            inc_statem_df = df[(df["Clase"] > 3)]
            inc_statem_df = inc_statem_df.drop(columns = ["Saldo Neto"])
            general = []
            for i in inc_statem_df["Cuenta"]:
                general.append(i[:4])
            inc_statem_df["Cuenta General"] = general
            
            detalle_df = inc_statem_df.groupby(by = ["Cuenta General", "Nivel"])["Cuenta",].count().reset_index()
            
            nivel_deseado = []
            for c in list(set(detalle_df["Cuenta General"])):
                detalle_nivel_df = detalle_df[detalle_df["Cuenta General"] == c]
                
                if len(detalle_nivel_df[detalle_nivel_df["Cuenta"] >= 2]) > 0:
                    nivel_deseado.append([c, max(detalle_nivel_df[detalle_nivel_df["Cuenta"] >= 2]["Nivel"])])
                else:
                    nivel_deseado.append([c, 1])   
            nivel_deseado_df = pd.DataFrame(nivel_deseado, columns = ["Cuenta General", "Nivel Deseado"])
            
            detalle_deseado_df = detalle_df.merge(nivel_deseado_df, on = "Cuenta General", how = "left")[["Cuenta General", "Nivel Deseado"]].drop_duplicates()
            
            inc_statem_df = inc_statem_df.merge(detalle_deseado_df, on = "Cuenta General", how = "left")
            inc_statem_df["Saldo Neto"] = df["Debe"] - df["Haber"]
            
            inc_statem_df = inc_statem_df[inc_statem_df["Nivel"] == inc_statem_df["Nivel Deseado"]]
            inc_statem_df = inc_statem_df[["Cuenta", "Nombre", "Saldo Neto"]]
            inc_statem_df["Sheet"] = tab

            outcome_df = pd.concat([outcome_df, balance_df, inc_statem_df])

        outcome_df = outcome_df.pivot(index=["Cuenta", "Nombre"], columns=["Sheet"], values=["Saldo Neto"]).iloc[1:].reset_index().droplevel(0, axis = 1)
        outcome_df = outcome_df.fillna(0)

        outcome_columns = ["Cuenta", "Nombre", "Espaciador"]

        for i in outcome_df.columns[3:]:
            outcome_columns.append(i)

        outcome_df.columns = outcome_columns
        outcome_df = outcome_df.drop(columns = ["Espaciador"])[["Cuenta", "Nombre"] + tabs]
        outcome_df["Cuenta"] = outcome_df["Cuenta"].astype("str")

        return outcome_df


if uploaded_file is not None:
    df = pd.read_excel(uploaded_file, sheet_name = None)
    
    if st.button('Correr 🚶‍♂️'):
        # Process the DataFrame
        with processor2:
            st.markdown("<h2 style='text-align: center; color: #14E79D; font-weight: bolder;'>PASO ✌️</h2>"+"<p style='text-align: center; color: #5666FF; font-weight: bold;'>Valida que la información cuadre</p>", unsafe_allow_html=True)
            st.markdown("")
            processed_df = process_data(df)
            
            # Convert DataFrame to Excel
            towrite = BytesIO()
            processed_df.to_excel(towrite, index=False, engine='openpyxl')  # Using 'openpyxl' for .xlsx files
            towrite.seek(0)

        with processor3:
            st.markdown("<h2 style='text-align: center; color: #14E79D; font-weight: bolder;'>PASO 👌</h2>"+"<p style='text-align: center; color: #5666FF; font-weight: bold;'>Descarga el archivo procesado</p>", unsafe_allow_html=True)
            st.markdown("")
            # Optionally display the processed DataFrame (comment out if not needed)
            st.dataframe(processed_df)

            # Create a link for downloading
            st.download_button(label='Descarga Archivo 📃',
                            data=towrite,
                            file_name='processed_output.xlsx',
                            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
