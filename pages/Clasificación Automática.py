import streamlit as st

st.set_page_config(
    page_title="Monthly - App Interna",
    page_icon="💸",
    layout="wide"
)

st.button("")

header_logo_1, header_logo_2 = st.columns(2)
with header_logo_1:
    st.image(
                "https://monthly.la/wp-content/uploads/2024/02/Monthly-Logo.png",
                width=200, # Manually Adjust the width of the image as per requirement
            )
with header_logo_2:
    st.markdown("<h2 style='text-align: right; color: #5666FF;'>🤖 Secciones Automáticas</h2>", unsafe_allow_html=True)

st.divider()

#ChatGPT
# Ensure the CSV has the correct column name
openai.api_key = st.secrets['OPENAI_API_KEY']


classification_list = []
for i in list(set(df["Clase"])):
    words_list = df[df["Clase"] == i]["Nombre"].tolist()
    
    # Step 2: Use GPT to Suggest 5 Categories
    prompt_for_categories = f"Basado en las siguientes palabras: {', '.join(words_list)}, sugiere 5 distintas categorías en las cual clasificarlas. No redactes nada más que una lista de 5 conceptos (no descripciones, no preámbulo de la respuesta, no conclusión; sólo la lista separada por comas)"
    response = openai.chat.completions.create(
        model="gpt-4",  # Use the desired model
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt_for_categories}
        ]
    )
    categories = response.choices[0].message.content.strip().split('\n')
    
# Step 3: Classify Each Word
def classify_word(word, categories):
    prompt_for_classification = f"Clasifica las palabras {', '.join(words_list)} en una de las siguientes categorias: {', '.join(categories)}. No incluyas explicación, ni desarrollo, ni justificación; sólamente la categoría que más se asemeje. Si es que no hay suficiente información para clasificar, pon la clasificación previa. Entregame esta clasificación en formato lista de tuples de python de esta manera: [('Palabra 1','Categoría'), ('Palabra 2': 'Categoría'), ('Palabra 3': 'Categoría')...]"
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt_for_classification}
        ]
        
    )
    classification = response.choices[0].message.content.strip()
    return classification
    
classification = classify_word(words_list, categories)
classification_list.append(classification)

categoria_df = pd.DataFrame(["",""], ["Nombre", "Categoría"]).T

for c in classification_list:
    categoria_df = pd.concat([categoria_df,pd.DataFrame(eval(c), columns = ["Nombre", "Categoría"])])
    categoria_df = categoria_df.iloc[1:]

nombre_list = []
for n in categoria_df["Nombre"]:
    nombre_list.append(n.strip())

categoria_df["Nombre"] = nombre_list

df_categorizado = df.merge(categoria_df, on = "Nombre", how = "left")

st.write(df_categorizado)
