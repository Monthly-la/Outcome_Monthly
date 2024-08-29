import streamlit as st
import pyexcel as p
import pandas as pd
from io import BytesIO


st.set_page_config(
    page_title="Monthly - App Interna",
    page_icon="💸",
    layout="wide"
)

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
                "https://monthly.la/wp-content/uploads/2024/02/Monthly-Logo.png",
                width=200, # Manually Adjust the width of the image as per requirement
            )
with header_logo_2:
    st.markdown("<h2 style='text-align: right; color: #5666FF;'>✅ Procesador de Balanzas de Comprobación</h2>", unsafe_allow_html=True)

st.divider()


processor1, paddingA, processor2, paddingB, processor3 = st.columns([5,1,5,1,5])
with processor1:
    st.markdown("<h2 style='text-align: center; color: #14E79D; font-weight: bolder;'>PASO ☝️</h2>"+"<p style='text-align: center; color: #5666FF; font-weight: bold;'>Selecciona el ERP contable y sube el archivo</p>", unsafe_allow_html=True)
    st.markdown("")
    
    option = st.selectbox(
        "ERP:",
        ("Alpha ERP","Contpaqi","Contalink", "Microsip", "SAP", "Aspel COI", "Netsuite (Oracle)"))




    uploaded_file = st.file_uploader("Inserta el Excel (.xlsx, .csv) aquí:", type=['xlsx', 'xls'])

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
            inc_statem_df["Saldo Neto"] = df["Haber"] - df["Debe"]
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

#Contpaqi
    if option == "Contpaqi":
        #Contpaqi Excel Sheets
        tabs = list(df.keys())
        tabs_dates = []

        outcome_df = pd.DataFrame(["","","",""], ["Cuenta", "Nombre", "Saldo Neto", "Sheet"]).T


        for tab in tabs:
            df = pd.read_excel(uploaded_file, sheet_name = tab)
            tabs_date = df["CONTPAQ i"].iloc[0][-8:]
            tabs_dates.append(tabs_date)
            df = df.fillna(0)
            df = df.replace(' ',0)
            
            df.columns = ["Cuenta", "Nombre"]+list(df.loc[4][2:])
            df = df.iloc[6:-7].reset_index().drop(columns = ["index"])
            
            type_of_Cuenta = []
            for i in list(df["Cuenta"]):
                type_of_Cuenta.append(type(i))
                
            df["Type"] = type_of_Cuenta
            df = df[df["Type"] == type("str")]
            df = df[:-1]
            df = df[df["Cuenta"] != "Fecha"]
            
            nombre_list = []
            for n in df["Nombre"]:
                nombre_list.append(n.strip())
            
            df["Nombre"] = nombre_list
            
            nivel_list = []
            for i in list(df["Cuenta"]):
                if (i.split("-")[2] == '000'):
                    if ((i.split("-")[1] == '00') or (i.split("-")[1] == '000')) and (i.split("-")[2] == '000'):
                        if (i.split("-")[0][-1:] == '0') and ((i.split("-")[1] == '00') or (i.split("-")[1] == '000')) and (i.split("-")[2] == '000'):
                            if (i.split("-")[0][-2:] == '00') and ((i.split("-")[1] == '00') or (i.split("-")[1] == '000')) and (i.split("-")[2] == '000'):
                                if (i.split("-")[0][-3:] == '000') and ((i.split("-")[1] == '00') or (i.split("-")[1] == '000')) and (i.split("-")[2] == '000'):
                                    nivel_list.append(1)
                                else:
                                    nivel_list.append(2)
                            else:
                                nivel_list.append(3)
                        else:
                            nivel_list.append(4)
                    else:
                        nivel_list.append(5)
                else:
                    nivel_list.append(6)
            
            
            df["Nivel"] = nivel_list
            class_of_cuenta = []
            for i in list(df["Cuenta"]):
                class_of_cuenta.append(i[0])
            
            df["Class"] = class_of_cuenta
            df["Class"] = df["Class"].astype("int")
            
            df.columns = ["Cuenta", "Nombre", "Saldo Inicial Deudor", "Saldo Inicial Acreedor", "Cargos", "Abonos", "Saldo Final Deudor", "Saldo Final Acreedor", "Tipo", "Nivel", "Clase"]
            df["Saldo Final Deudor"] = df["Saldo Final Deudor"].astype("float")
            df["Saldo Final Acreedor"] = df["Saldo Final Acreedor"].astype("float")
            
            df["Saldo Neto"] = df["Saldo Final Deudor"] - df["Saldo Final Acreedor"]
            
            activos = df[(df["Nivel"] == 1) & (df["Clase"] == 1)]["Saldo Neto"].sum()
            pasivos = df[(df["Nivel"] == 1) & (df["Clase"] == 2)]["Saldo Neto"].sum()
            capital= df[(df["Nivel"] == 1) & (df["Clase"] == 3)]["Saldo Neto"].sum()
            utilidad_acum = df[(df["Nivel"] == 1) & (df["Clase"] >= 4)]["Saldo Neto"].sum()
            
            result = round(activos+pasivos+capital+utilidad_acum,1)
            
            results_df = pd.DataFrame({"Cuentas": ["Activos", "Pasivos", "Capital", "Utilidad Acumulada", "Sumatoria Final"], 
                                    "Resultado":[activos, pasivos, capital, utilidad_acum, result]})
            
            if result == 0:
                st.caption(tabs_date + " - Check ✅")
            else:
                st.caption(tabs_date + " - No Check ❌")
            
            st.dataframe(results_df, width = 1000)
            st.divider()
            
            #Outcome Matrix

            balance_df = df[(df["Nivel"] == 2) & (df["Clase"] <= 3)][["Cuenta","Nombre","Saldo Neto"]]
            balance_df["Sheet"] = tabs_date

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
            inc_statem_df["Saldo Neto"] = df["Cargos"] - df["Abonos"]
            
            inc_statem_df = inc_statem_df[inc_statem_df["Nivel"] == inc_statem_df["Nivel Deseado"]]
            inc_statem_df = inc_statem_df[["Cuenta", "Nombre", "Saldo Neto"]]
            inc_statem_df["Sheet"] = tabs_date

            outcome_df = pd.concat([outcome_df, balance_df, inc_statem_df])
        
        outcome_df = outcome_df.pivot(index=["Cuenta", "Nombre"], columns=["Sheet"], values=["Saldo Neto"]).iloc[1:].reset_index().droplevel(0, axis = 1)
        outcome_df = outcome_df.fillna(0)

        outcome_columns = ["Cuenta", "Nombre"]

        for i in outcome_df.columns[2:]:
            outcome_columns.append(i)

        outcome_df.columns = outcome_columns
        outcome_df = outcome_df[["Cuenta", "Nombre"] + tabs_dates]

        outcome_df["Cuenta"] = outcome_df["Cuenta"].astype("str")
        
        return outcome_df

#Aspel COI
    if option == "Aspel COI":
        #Contpaqi Excel Sheets
        tabs = list(df.keys())
        tabs_dates = []

        outcome_df = pd.DataFrame(["","","",""], ["Cuenta", "Nombre", "Saldo Neto", "Sheet"]).T


        for tab in tabs:
            df = pd.read_excel(uploaded_file, sheet_name = tab)
            df.columns = df.iloc[11]
            df = df.dropna(subset = df.columns[1])[2:]
            tabs_dates.append(tab)
            
            column_list = list(df.columns)
            column_list = [x for x in column_list if str(x) != 'nan']
            df = df[column_list]
            
            cuenta = []
            cuenta_len = []
            for i in list(df['No. de cuenta       Descripción']):
                cuenta.append([x for x in i.split(" ") if str(x) != ""])
                cuenta_len.append(len([x for x in i.split(" ") if str(x) != ""]))
            
            df["Cuenta"] = cuenta
            df["Validación"] = cuenta_len
            df = df[df["Validación"] > 1].drop(columns = [df.columns[0], "Validación"])
            
            codigo = []
            nombre = []
            for i in list(df["Cuenta"]):
                if len(i[0]) == 13:
                    codigo.append(i[0])
                else:
                    codigo.append(0)
                nombre.append(" ".join(str(n) for n in i[1:]))
            
            df["Cuenta"] = codigo
            df["Nombre"] = nombre
            df = df[df["Cuenta"] != 0]
            
            nivel_list = []
            
            for i in list(df["Cuenta"]):
                if (i.split("-")[1] == '0000'):
                    nivel_list.append(1)
                elif (i.split("-")[2][-2:] == '000') and (i.split("-")[1] != '0000'):
                    nivel_list.append(2)
                else:
                    nivel_list.append(3)
                        
            
            df["Nivel"] = nivel_list
            
            class_of_cuenta = []
            for i in list(df["Cuenta"]):
                class_of_cuenta.append(i[0])
            
            df["Class"] = class_of_cuenta
            df["Class"] = df["Class"].astype("int")
            
            df.columns = ["Saldo Inicial", "Debe", "Haber", "Saldo Neto", "Cuenta", "Nombre", "Nivel", "Clase"]
            #df["Saldo Final Deudor"] = df["Saldo Final Deudor"].astype("float")
            #df["Saldo Final Acreedor"] = df["Saldo Final Acreedor"].astype("float")
            df["Saldo Neto"] = df["Saldo Neto"].str.replace(',', '')
            df["Saldo Neto"] = df["Saldo Neto"].astype(float)
            
            
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

    if option == "Alpha ERP":
        ###### Alpha Excel Sheets
        tabs = list(df.keys())
        tabs_dates = []

        outcome_df = pd.DataFrame(["","","",""], ["Cuenta", "Nombre", "Saldo Neto", "Sheet"]).T
        
        #Alpha Excel Sheets
        for tab in tabs:
            df = pd.read_excel(uploaded_file, sheet_name = tab)
            tabs_date = df.iloc[1, 5][-8:]
            tabs_dates.append(tabs_date)
            
            df = df.fillna(0)[6:-4]
            
            zero_cols = df.columns[(df == 0).all()]
            df.drop(labels=zero_cols, axis=1, inplace=True)
            df.columns = ["Código", "Cuenta", "Saldo Inicial Deudor", "Saldo Inicial Acreedor", "Cargos", "Abonos", "Saldo Final Deudor", "Saldo Final Acreedor"]
            df = df[df["Código"] != 0]
            
            nivel_list = []
            def count_leading_spaces(s):
                count = 0
                for char in s:
                    if char == ' ':
                        count += 1
                    else:
                        break
                return count
            
            for i in df["Cuenta"]:
                nivel_list.append(int(1+count_leading_spaces(i)/2))
            
            df["Nivel"] = nivel_list
            
            class_of_cuenta = []
            for i in list(df["Código"]):
                class_of_cuenta.append(i[0])
            
            df["Clase"] = class_of_cuenta
            df["Clase"] = df["Clase"].astype("int")
            
            df["Saldo Neto"] = df["Saldo Final Deudor"] - df["Saldo Final Acreedor"]
            
            activos = df[(df["Nivel"] == 2) & (df["Clase"] == 1)]["Saldo Neto"].sum()
            pasivos = df[(df["Nivel"] == 2) & (df["Clase"] == 2)]["Saldo Neto"].sum()
            capital= df[(df["Nivel"] == 2) & (df["Clase"] == 3)]["Saldo Neto"].sum()
            utilidad_acum = df[(df["Nivel"] == 2) & (df["Clase"] >= 4)]["Saldo Neto"].sum()
            
            result = round(activos+pasivos+capital+utilidad_acum,1)
                
            results_df = pd.DataFrame({"Cuentas": ["Activos", "Pasivos", "Capital", "Utilidad Acumulada", "Sumatoria Final"], 
                                       "Resultado":[activos, pasivos, capital, utilidad_acum, result]})
            
            if result == 0:
                st.caption(tabs_date + " - Check ✅")
            else:
                st.caption(tabs_date + " - No Check ❌")
            
            st.dataframe(results_df, width = 1000)
            st.divider()


if uploaded_file is not None:
    st.write(uploaded_file.name)
    st.write(uploaded_file.name[-3:])
    st.write(uploaded_file.name[:4])
    
    if uploaded_file.name[-3:] == "xls":
        p.save_book_as(file_name = uploaded_file.name, dest_file_name = uploaded_file.name[:4] + '.xlsx')
    
    df = pd.read_excel(uploaded_file, sheet_name = None)
    
    if st.button('Correr 🚶‍♂️'):
        # Process the DataFrame
        with processor2:
            st.markdown("<h2 style='text-align: center; color: #14E79D; font-weight: bolder;'>PASO ✌️</h2>"+"<p style='text-align: center; color: #5666FF; font-weight: bold;'>Valida que la información cuadre</p>", unsafe_allow_html=True)
            st.markdown("")
            processed_df = process_data(df)
            
            # Convert DataFrame to Excel
            towrite = BytesIO()
            processed_df.to_excel(towrite, index=False)  # Using 'openpyxl' for .xlsx files
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
