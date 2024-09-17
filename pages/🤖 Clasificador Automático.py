import streamlit as st
import pandas as pd
import os
from openai import OpenAI


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
            classification_list = []
                
            # Step 3: Classify Each Word
            def classify_word(word, categories):
                prompt_for_classification = f"Clasifica las palabras {', '.join(word)} en una de las siguientes categorias: {', '.join(categories)}. No incluyas explicación, ni desarrollo, ni justificación; sólamente la categoría que más se asemeje. Si es que no hay suficiente información para clasificar, pon la clasificación 0. Entregame esta clasificación en formato lista de listas de python de esta manera: [['Palabra 1','Categoría'], ['Palabra 2': 'Categoría'], ['Palabra 3': 'Categoría']...]"
                response = openai.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt_for_classification}
                    ]
                    
                )
                classification = response.choices[0].message.content.strip()
                return classification
            
            for i in set(list(df["Clase"])):
                print(i)
                cat = list(set(monthly_cat_clase[(monthly_cat_clase["Clase"] == i) & (monthly_cat_clase["ID-CATEGORÍA"] == "ES-MONTHLY")]["CATEGORÍA (MONTHLY WAY)"]))
                print(cat)
                if i <= 3:
                    words_list = list(df[(df["Nivel"] == 1) & (df["Clase"] == i)]["Nombre"])
                else:
                    if len(list(df[(df["Nivel"] == 2) & (df["Clase"] == i)]["Nombre"]) ) == 0:
                        words_list = list(df[(df["Nivel"] == 1) & (df["Clase"] == i)]["Nombre"])
                    else:
                        words_list = list(df[(df["Nivel"] <= 2) & (df["Clase"] == i)]["Nombre"])
                print(words_list)
                classification = classify_word(words_list, cat)
                match = re.search(r"\[.*\]", classification)
            
                try:
                    if match:
                        classification = eval(match.group())
                        classification_list.append(classification)
                except:
                    data_cleaned = eval(classification.replace("\n", ""))
                    classification_list.append(data_cleaned)
                finally:
                    pass
                    
            result = sum(classification_list, [])
            
            if len(classification_list[0]) == 1:
                classification_list = [classification_list[:2]] + classification_list[2:]
            if len(classification_list[-1]) == 1:
                classification_list = classification_list[:-2] + [classification_list[-2:]]
            
            try:
                result = result.replace("\n", "")
            except:
                pass
                
            result_df = pd.DataFrame(result, columns=['Nombre', 'Categoría']).drop_duplicates()
            
            #Clasificación Chat GPT con Insumo original
            clasificacion_df = df.merge(result_df, on = "Nombre", how = "left").fillna(0)
            
            #Llenado de Ramificaciones vacías
            for i in range(len(clasificacion_df)):
                if clasificacion_df["Categoría"].iloc[i] == 0 :
                   clasificacion_df["Categoría"].iloc[i] = clasificacion_df["Categoría"].iloc[i-1]
            
            #Clasificación Monthly
            clasificacion_seccion_df = clasificacion_df.merge(monthly_cat_clase, left_on = ["Categoría", "Clase"], right_on = ["CATEGORÍA (MONTHLY WAY)", "Clase"], how = "left").fillna(0)
            clasificacion_seccion_df
            
            #Llenado final de clasificaciones vacías
            classification_full_list = []
            section_full_list = []
            section_code_full_list = []
            
            for i in range(len(clasificacion_seccion_df)):
                if clasificacion_seccion_df["CATEGORÍA (MONTHLY WAY)"].iloc[i] == 0 :
                    classification_full_list.append(classification_full_list[i-1])
                    section_full_list.append(section_full_list[i-1])
                    section_code_full_list.append(section_code_full_list[i-1])
                else:
                    classification_full_list.append(clasificacion_seccion_df["CATEGORÍA (MONTHLY WAY)"].iloc[i])
                    section_full_list.append(clasificacion_seccion_df["SECCIÓN (MONTHLY WAY)"].iloc[i])
                    section_code_full_list.append(clasificacion_seccion_df["SECCIÓN"].iloc[i])
            
            clasificacion_seccion_df["CATEGORÍA (MONTHLY WAY) - Full"] = classification_full_list
            clasificacion_seccion_df["SECCIÓN (MONTHLY WAY) - Full"] = section_full_list
            clasificacion_seccion_df["ID-CATEGORÍA - Full"] = "ES-MONTHLY"
            clasificacion_seccion_df["SECCIÓN - Full"] = section_code_full_list
            
            clasificacion_seccion_df["Sheet"] = "Ene/2023"
            
            st.write(clasificacion_seccion_df)
