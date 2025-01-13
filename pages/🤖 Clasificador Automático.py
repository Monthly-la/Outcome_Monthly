import streamlit as st
import pandas as pd
import os
from openai import OpenAI
import numpy as np
import re



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
    st.markdown("<h2 style='text-align: right; color: #5666FF;'>🤖 Clasificador Automático</h2>", unsafe_allow_html=True)

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
            # Ensure the CSV has the correct column name

            activos_cat = ["Efectivo y bancos", "Inventario", "Clientes", "Impuestos por cobrar", "Cuentas por cobrar", "Anticipo a proveedores",
          "Activos fijos", "Activos intangibles", "Otros activos a largo plazo", "Depreciación acumulada", "Amortización acumulada"]
            # Lista de categorías que representan los diferentes tipos de activos de una empresa, con el estándar "Monthly Way".
            
            pasivos_capital_cat = ["Proveedores", "Impuestos por pagar", "Anticipo de clientes", "Cuentas por pagar", "Deuda a corto plazo", "Deuda a largo plazo",
                     "Otros pasivos a largo plazo", "Capital de accionistas", "Dividendos pagados", "Utilidades retenidas"]
            # Lista de categorías relacionadas con pasivos y capital, con el estándar "Monthly Way".

            seccion_cat = pd.read_excel("Monthly - Catalogo.xlsx", sheet_name = "Categorización de clientes")
            # Importa únicamente la hoja llamada "Categorización de clientes" de "Monthly - Catalogo.xlsx" y la guarda en un nuevo DataFrame llamado seccion_cat.
            
            seccion_cat = seccion_cat[seccion_cat["ID-CATEGORÍA"] == "ES-MONTHLY"]
            # Filtra seccion_cat para quedarse solo con las filas donde el valor de la columna "ID-CATEGORÍA" sea "ES-MONTHLY".
            # Esto para seleccionar las categorías específicas del estándar "Monthly Way".
            
            seccion_catseccion_cat = pd.read_excel("Monthly - Catalogo.xlsx", sheet_name = "Categorización de clientes")
            # Importa únicamente la hoja llamada "Categorización de clientes" de "Monthly - Catalogo.xlsx" y la guarda en un nuevo DataFrame llamado seccion_cat.
            
            seccion_cat = seccion_cat[seccion_cat["ID-CATEGORÍA"] == "ES-MONTHLY"]
            # Filtra seccion_cat para quedarse solo con las filas donde el valor de la columna "ID-CATEGORÍA" sea "ES-MONTHLY".
            # Esto para seleccionar las categorías específicas del estándar "Monthly Way".

            seccion_cat[["SECCIÓN (MONTHLY WAY)", "SECCIÓN"]].drop_duplicates()
            # Se selecionan las columnas "SECCIÓN (MONTHLY WAY)" (nueva sección categorizada según el estándar Monthly Way), y "SECCIÓN" (sección original).
            # También se eliminan filas duplicadas en el subconjunto de columnas seleccionado para asegurar que cada combinación única de ambas columnas aparezca una sola vez.
            
            # El propósito de esta celda es obtener un listado único de pares entre la sección original ("SECCIÓN") y la sección categorizada ("SECCIÓN (MONTHLY WAY)") en el sistema Monthly Way.
            # Esto puede ser útil para identificar cómo las secciones originales han sido reclasificadas o agrupadas en el nuevo esquema.
            seccion_v_balanza_df = pd.read_excel("Monthly - Catalogo.xlsx", sheet_name = "Sección contra Balanza").fillna("").melt(id_vars=["SECCIÓN"], var_name='Clase', value_name='SECCIÓN (MONTHLY WAY)')
            # Se carga la hoja "Sección contra Balanza" de "Monthly - Catalogo.xlsx" en un DataFrame llamado seccion_v_balanza_df.
            # Se reemplazan todos los valores nulos en el DataFrame con cadenas vacías (""). Esto es para evitar problemas al manipular los datos.
            # Se convierten las columnas numéricas del DataFrame en una estructura "larga" (long format).
            # id_vars=["SECCIÓN"] conserva la columna "SECCIÓN" como identificador.
            # var_name="Clase" asigna el nombre "Clase" a la columna que contendrá los nombres de las columnas originales.
            # value_name="SECCIÓN (MONTHLY WAY)" asegura que los valores originales de las columnas numéricas se colocan en una columna llamada "SECCIÓN (MONTHLY WAY)".
            
            seccion_v_balanza_df = seccion_v_balanza_df[seccion_v_balanza_df["SECCIÓN (MONTHLY WAY)"] != ""]
            # Filtra el DataFrame para conservar solo las filas donde la columna "SECCIÓN (MONTHLY WAY)" no está vacía ("").


            monthly_cat = pd.read_excel("Monthly - Catalogo.xlsx", sheet_name = "Categorización de clientes")[["CATEGORÍA (MONTHLY WAY)","SECCIÓN (MONTHLY WAY)", "SECCIÓN", "ID-CATEGORÍA"]]
            # Se carga la hoja "Categorización de clientes" de "Monthly - Catalogo.xlsx" y se seleccionan solo las columnas relevantes.
            # El DataFrame resultante (monthly_cat) contiene datos relevantes para vincular categorías con secciones.
            
            monthly_cat_clase = monthly_cat.merge(seccion_v_balanza_df, on = ["SECCIÓN", "SECCIÓN (MONTHLY WAY)"], how = "left").drop_duplicates()
            # Combina monthly_cat con seccion_v_balanza_df usando un join en las columnas comunes: "SECCIÓN" y "SECCIÓN (MONTHLY WAY)".
            # (Left Join conserva todas las filas de monthly_cat, y añade información de seccion_v_balanza_df si las claves coinciden.)
            # drop_duplicates() elimina filas duplicadas del DataFrame resultante.
            
            monthly_cat_clase = monthly_cat_clase[monthly_cat_clase["ID-CATEGORÍA"] == "ES-MONTHLY"]
            # Se filtran solo las filas donde "ID-CATEGORÍA" es igual a "ES-MONTHLY", manteniendo datos relevantes al sistema Monthly Way.
            
            # monthly_cat_clase contiene: categorías y secciones filtradas por "ID-CATEGORÍA" == "ES-MONTHLY";
            # y la relación entre las categorías de clientes y su respectiva clasificación de secciones.
            
            # El propósito de esta celda es consolidar información de categorías y secciones, integrando datos de las hojas "Categorización de clientes" y "Sección contra Balanza" de "Monthly - Catalogo.xlsx",
            # para obtener una visión completa de cómo se categorizan y agrupan los datos en el sistema Monthly Way.

            
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
                print(i)
                cat = list(set(monthly_cat_clase[(monthly_cat_clase["Clase"] == i) & (monthly_cat_clase["ID-CATEGORÍA"] == "ES-MONTHLY")]["CATEGORÍA (MONTHLY WAY)"]))
                # Filtra el DataFrame monthly_cat_clase para obtener las categorías ("CATEGORÍA (MONTHLY WAY)") relacionadas con la clase actual (i) y el identificador "ES-MONTHLY".
                print(cat)
                # Crear words_list:
                if i <= 3:
                    words_list = list(df[(df["Nivel"] == 1) & (df["Clase"] == i)]["Nombre"])
                else:
                    if len(list(df[(df["Nivel"] == 2) & (df["Clase"] == i)]["Nombre"]) ) == 0:
                        words_list = list(df[(df["Nivel"] == 1) & (df["Clase"] == i)]["Nombre"])
                    else:
                        words_list = list(df[(df["Nivel"] <= 2) & (df["Clase"] == i)]["Nombre"])
                # Crea una lista de nombres de cuentas (words_list) basándose en el nivel y clase.
                # Para clases 1, 2, y 3, toma cuentas de nivel 1.
                # Para otras clases: Si no hay cuentas de nivel 2, usa las de nivel 1; Si hay cuentas de nivel 2, usa todas las de niveles 1 y 2.
                print(words_list)
            
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
            
            # Crear el DataFrame clasificacion_df:
            clasificacion_df = df.merge(result_df, on = "Nombre", how = "left").fillna(0).drop_duplicates(subset=['Unnamed: 0', 'Cuenta', 'Nombre', 'Saldo Inicial Deudor',
                   'Saldo Inicial Acreedor', 'Debe', 'Haber', 'Saldo Final Deudor','Saldo Final Acreedor', 'Tipo', 'Nivel', 'Clase', 'Saldo Neto'])
            # merge: Combina df con result_df usando la columna "Nombre" como clave.
            # on="Nombre": Combina las filas donde los nombres coinciden.
            # how="left": Mantiene todas las filas de df, incluso si no hay coincidencia en result_df.
            # Resultado: Se añade la columna "Categoría" de result_df a df.
            # fillna(0): Rellena los valores faltantes (NaN) con 0. Esto asegura que las filas sin coincidencia tengan un valor por defecto.
            
            # Rellenar clasificaciones vacías:
            for i in range(len(clasificacion_df)):
            # Itera sobre cada fila de clasificacion_df.
            
                if clasificacion_df["Categoría"].iloc[i] == 0 :
                   clasificacion_df["Categoría"].iloc[i] = clasificacion_df["Categoría"].iloc[i-1]
                # Si el valor en la columna "Categoría" es 0, copia el valor de la fila anterior.
                # Propósito: Asegurar que las clasificaciones vacías hereden la categoría de la fila previa, para mantener coherencia.
            
            # Crear clasificacion_seccion_df para clasificación Monthly:
            clasificacion_seccion_df = clasificacion_df.merge(
                monthly_cat_clase,
                left_on = ["Categoría", "Clase"],
                right_on = ["CATEGORÍA (MONTHLY WAY)", "Clase"],
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
                if clasificacion_seccion_df["CATEGORÍA (MONTHLY WAY)"].iloc[i] == 0 :
                    classification_full_list.append(classification_full_list[i-1])
                    section_full_list.append(section_full_list[i-1])
                    section_code_full_list.append(section_code_full_list[i-1])
                # Si "CATEGORÍA (MONTHLY WAY)" es 0, hereda los valores de la fila previa.
                else:
                    classification_full_list.append(clasificacion_seccion_df["CATEGORÍA (MONTHLY WAY)"].iloc[i])
                    section_full_list.append(clasificacion_seccion_df["SECCIÓN (MONTHLY WAY)"].iloc[i])
                    section_code_full_list.append(clasificacion_seccion_df["SECCIÓN"].iloc[i])
                # Si no es 0, toma los valores actuales de las columnas.
            
            # Agregar las listas al DataFrame:
            clasificacion_seccion_df["CATEGORÍA (MONTHLY WAY) - Full"] = classification_full_list
            clasificacion_seccion_df["SECCIÓN (MONTHLY WAY) - Full"] = section_full_list
            clasificacion_seccion_df["ID-CATEGORÍA - Full"] = "ES-MONTHLY"
            clasificacion_seccion_df["SECCIÓN - Full"] = section_code_full_list
            # Se crean nuevas columnas en clasificacion_seccion_df para almacenar las listas completas.
            
            # Agregar la columna de hoja:
            clasificacion_seccion_df["Sheet"] = "Ene/2023"
            final_df = clasificacion_seccion_df[clasificacion_seccion_df.columns[~clasificacion_seccion_df.columns.isin(list(clasificacion_seccion_df.columns[-10:-6]))]].iloc[:,1:]
            
            st.write(final_df)
