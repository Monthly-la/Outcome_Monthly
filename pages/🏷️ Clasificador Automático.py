import streamlit as st
import pandas as pd
import os
from openai import OpenAI
import numpy as np
import re
from openpyxl import load_workbook




pd.options.display.float_format = '{:,.2f}'.format


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
                "./Logo. Monthly Oficial.png",
                width=250, # Manually Adjust the width of the image as per requirement
            )
with header_logo_2:
    st.markdown("<h2 style='text-align: right; color: #5666FF;'>🏷️ Clasificador Automático</h2>", unsafe_allow_html=True)

st.divider()

#ChatGPT
# Access the OpenAI API key from the secrets
api_key = st.secrets["OPENAI_API_KEY"]

# Set up the OpenAI API client
openai = OpenAI(api_key=api_key)

uploaded_file = st.file_uploader("Inserta el Excel (.xlsx, .csv) aquí:", type=['csv'])


if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write(df)
    clicked = st.button("Generar Clasificación 🤖",type="primary")
    if clicked:

        with st.spinner("Generando Clasificaciones:"):
            catalogo_df = pd.read_excel("Categorizador 2025.xlsx")
            catalogo_df = catalogo_df.iloc[:-1]
            catalogo_df_clean = catalogo_df.fillna(0)
            catalogo_df_clean["Código"] = catalogo_df_clean["Código"].astype(float)
            catalogo_df_clean = catalogo_df_clean.sort_values(by = "Código", ascending = True)
            catalogo_df_clean["Código"] = catalogo_df_clean["Código"].astype(str)
            catalogo_df_clean["Clase"] = catalogo_df_clean["Código"].str[0].astype(int)
            catalogo_df_clean["CATEGORÍA (MONTHLY WAY)"] = catalogo_df_clean["Categoría"].astype(str).str[0:3]
            
            clases = [1,2,3,5,6,7,8]
            monthly_cat_clase = catalogo_df_clean[["Clase", "Cuenta", "CATEGORÍA (MONTHLY WAY)", "Categoría",	"Sección", "ID"]]
            monthly_cat_clase["Categoría"] = monthly_cat_clase["Categoría"].astype(str).str[4:]
            monthly_cat_clase = monthly_cat_clase.drop_duplicates()
            monthly_cat_clase = monthly_cat_clase[monthly_cat_clase["Sección"] != "-"]
            monthly_cat_clase = monthly_cat_clase[monthly_cat_clase["Clase"].isin(clases)]

            #Catálogo de Ingresos
            seccion_cat = pd.read_excel("Monthly - Catalogo.xlsx", sheet_name = "Categorización de clientes")
            seccion_cat = seccion_cat[seccion_cat["SECCIÓN (MONTHLY WAY)"] == "(a)"]
            seccion_cat = seccion_cat[seccion_cat["ID-CATEGORÍA"] != "ES-PERSONAL"]
            seccion_cat = seccion_cat.rename(columns = {"CATEGORÍA (MONTHLY WAY)": "Cuenta","SECCIÓN (MONTHLY WAY)": "CATEGORÍA (MONTHLY WAY)", "SECCIÓN":"Sección", "ID-CATEGORÍA":"ID" })
            seccion_cat["Categoría"] = "Ingreso"
            seccion_cat["Clase"] = 4
            seccion_cat = seccion_cat[["Clase", "Cuenta", "CATEGORÍA (MONTHLY WAY)", "Categoría", "Sección", "ID"]].drop_duplicates()

            catalogo = pd.concat([monthly_cat_clase, seccion_cat]).sort_values(by = ["Clase", "Cuenta"], ascending = [True, True])
            catalogo = catalogo.rename(columns = {"Cuenta": "Cuenta SAT", "Categoría": "Categoría Monthly"})


            api_key = os.getenv("OPENAI_API_KEY")
            openai.api_key = api_key
            # La clave API expuesta aquí podría ser un riesgo de seguridad. En un proyecto real, esta clave debería cargarse desde variables de entorno o un archivo protegido.
            
            classification_list = [] # NOTA: Esta lista no se había definido ya en la celda anterior? Volverla a definir no afecta el resultado?
            unfiltered_classification_list = []
            # Crea una lista vacía para almacenar los resultados de las clasificaciones realizadas con el modelo GPT.
            
            # La función classify_word clasificará palabras en categorías proporcionadas usando la API de OpenAI.
            def classify_word(word, categories):
                # Construcción del prompt que solicitará clasificar una lista de palabras en las categorías dadas, con instrucciones claras de devolver solo el formato esperado.
                prompt_for_classification = f"Clasifica las palabras {', '.join(word)} en una de las siguientes categorias: {', '.join(categories)}. No incluyas explicación, ni desarrollo, ni justificación; sólamente la categoría que más se asemeje. Si es que no hay suficiente información para clasificar, pon la clasificación 0. Entregame esta clasificación en formato lista de python de esta manera: ['Palabra 1','Categoría de Palabra 1','Palabra 2','Categoría de Palabra 2', ...'Palabra n','Categoría de Palabra n']"
                response = openai.chat.completions.create(
                    model="gpt-4", # Usa el modelo GPT-4 para procesar el prompt y generar una respuesta.
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt_for_classification}
                    ]
                )
                classification = response.choices[0].message.content.strip()
                # Devuelve la clasificación generada como un string:
            
                return classification
            
            # Clasificación por clase:
            for i in set(list(df["Clase"])):
            # Itera sobre cada valor único en la columna "Clase" de df.
                st.write(i)
                cat = list(set(catalogo[(catalogo["Clase"] == i) & (catalogo["ID"] == "ES-MONTHLY")]["Cuenta SAT"]))
                # Filtra el DataFrame monthly_cat_clase para obtener las categorías ("CATEGORÍA (MONTHLY WAY)") relacionadas con la clase actual (i) y el identificador "ES-MONTHLY".
                st.write(cat)
                # Crear words_list:
                if len(list(df[(df["Nivel"] == 2) & (df["Clase"] == i)]["Nombre"]) ) == 0:
                    words_list = list(df[(df["Nivel"] == 1) & (df["Clase"] == i)]["Nombre"])
                else:
                    words_list = list(df[(df["Nivel"] == 2) & (df["Clase"] == i)]["Nombre"])
                # Crea una lista de nombres de cuentas (words_list) basándose en el nivel y clase.
                # Para clases 1, 2, y 3, toma cuentas de nivel 1.
                # Para otras clases: Si no hay cuentas de nivel 2, usa las de nivel 1; Si hay cuentas de nivel 2, usa todas las de niveles 1 y 2.
                st.write(words_list)
            
                # Clasificación de las palabras:
                classification = classify_word(words_list, cat)
                match = re.search(r"\[.*\]", classification)
                # Usa classify_word para obtener la clasificación de las palabras en words_list usando las categorías de cat.
                # Busca el formato de una lista en la respuesta usando expresiones regulares.
            
                # Manejo de la respuesta:
                unfiltered_classification_list.append(classification)
            
                try:
                  classification = eval(classification)
                except:
                  counter = 0
                  open = 0
                  close = 0
                  for i in classification:
                    if i == "[":
                      open = counter
                    if i == "]":
                      close = counter
                    counter += 1
                  classification = eval("["+classification[open+1:close]+"]")
                #finally:
                    #pass
                #    data_cleaned = eval(classification.replace("\n", ""))
                classification_list.append(classification)
                #finally:
                #    pass
                # Convierte la respuesta de GPT en una lista válida de Python y la añade a classification_list.
                # Maneja excepciones en caso de que la conversión falle.
            
            # Consolidación de resultados:
                #classification_list
            
            #if len(classification_list[0]) == 1:
            #    classification_list = [classification_list[:2]] + classification_list[2:]
            #if len(classification_list[-1]) == 1:
            #    classification_list = classification_list[:-2] + [classification_list[-2:]]
            # Combina todas las clasificaciones en una lista única (result).
            
            
            # Ajusta classification_list si las primeras o últimas clasificaciones tienen una estructura inusual.
            
            results = sum(classification_list, [])
            nombre_result_list = results[0::2]
            categoria_result_list = results[1::2]
            
            
            result_df = pd.DataFrame()
            result_df["Nombre"] = nombre_result_list
            result_df["Categoría"] = categoria_result_list
            result_df = result_df.drop_duplicates()
            
            
            # Crear el DataFrame final:
            # Convierte result en un DataFrame con columnas "Nombre" y "Categoría".
            # Elimina duplicados para asegurar que cada combinación sea única.
            # Crear el DataFrame clasificacion_df:
            clasificacion_df = df.merge(result_df, on = "Nombre", how = "left").fillna(0).drop_duplicates(subset=['Unnamed: 0', 'Cuenta', 'Nombre', 'Saldo Inicial Deudor',
                   'Saldo Inicial Acreedor', 'Debe', 'Haber', 'Saldo Final Deudor','Saldo Final Acreedor', 'Tipo', 'Nivel', 'Clase', 'Saldo Neto'])
            
            clasificacion_df = clasificacion_df[clasificacion_df["Nivel"] != 1]

            # Rellenar clasificaciones vacías:
            for i in range(len(clasificacion_df)):
            # Itera sobre cada fila de clasificacion_df.
            
                if clasificacion_df["Categoría"].iloc[i] == 0 :
                   clasificacion_df["Categoría"].iloc[i] = clasificacion_df["Categoría"].iloc[i-1]
                # Si el valor en la columna "Categoría" es 0, copia el valor de la fila anterior.
                # Propósito: Asegurar que las clasificaciones vacías hereden la categoría de la fila previa, para mantener coherencia.
            clasificacion_seccion_df = clasificacion_df.merge(
                catalogo,
                left_on = ["Categoría", "Clase"],
                right_on = ["Cuenta SAT", "Clase"],
                how = "left")
            # merge: Combina clasificacion_df con monthly_cat_clase.
            # left_on=["Categoría", "Clase"]: Usa "Categoría" y "Clase" de clasificacion_df como claves.
            # right_on=["CATEGORÍA (MONTHLY WAY)", "Clase"]: Usa estas columnas de monthly_cat_clase como claves para emparejar.
            clasificacion_seccion_df = clasificacion_seccion_df.fillna(0)
            # fillna(0):** Rellena valores faltantes con 0
            
            # Rellenar clasificaciones completas:
            # Listas acumuladoras:
            classification_full_list = []
            # Almacena clasificaciones completas de "CATEGORÍA (MONTHLY WAY)".
            section_full_list = []
            # Almacena las secciones correspondientes.
            section_code_full_list = []
            # Almacena los códigos de sección.
            
            for i in range(len(clasificacion_seccion_df)):
                if clasificacion_seccion_df["CATEGORÍA (MONTHLY WAY)"].iloc[i] == 0:
                    classification_full_list.append(classification_full_list[i-1])
                    section_full_list.append(section_full_list[i-1])
                    section_code_full_list.append(section_code_full_list[i-1])
                # Si "CATEGORÍA (MONTHLY WAY)" es 0, hereda los valores de la fila previa.
                else:
                    classification_full_list.append(clasificacion_seccion_df["CATEGORÍA (MONTHLY WAY)"].iloc[i])
                    section_full_list.append(clasificacion_seccion_df["Sección"].iloc[i])
                    section_code_full_list.append(clasificacion_seccion_df["Sección"].iloc[i])
                # Si no es 0, toma los valores actuales de las columnas.
            
            # Agregar las listas al DataFrame:
            clasificacion_seccion_df["CATEGORÍA (MONTHLY WAY) - Full"] = classification_full_list
            clasificacion_seccion_df["SECCIÓN (MONTHLY WAY) - Full"] = section_full_list
            clasificacion_seccion_df["ID-CATEGORÍA - Full"] = "ES-MONTHLY"
            clasificacion_seccion_df["SECCIÓN - Full"] = section_code_full_list
            
            final_df = clasificacion_seccion_df[ ~( ((clasificacion_seccion_df["SECCIÓN - Full"] == "Costo") & (clasificacion_seccion_df["Clase"] >= 6)) | ((clasificacion_seccion_df["SECCIÓN - Full"] == "Gasto") & (clasificacion_seccion_df["Clase"] < 6)) ) ]


            
            st.write(final_df)
