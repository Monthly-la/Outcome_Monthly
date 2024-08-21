import streamlit as st
import pandas as pd
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import requests


#https://github.com/S0NM/selenium-demo/tree/main
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
    st.markdown("<h2 style='text-align: right; color: #5666FF;'>🎋 Generador de Sankey</h2>", unsafe_allow_html=True)

st.divider()


def get_website_content(url, df):
    driver = None
    
    concepto_color_df = pd.DataFrame.from_dict({"Ingreso": "#5666FF", "Costo":"#FF585D", "Utilidad Bruta":"#14E79D", "EBITDA":"#14E79D", "Gasto":"#FFB71A", "Otras Cuentas": "#A5A5A5"}, orient='index', columns = ["Color"]).reset_index().rename(columns = {"index":"Concepto"})
    ruta_color_df = pd.DataFrame.from_dict({"#5666FF":"#B3BAFF", "#FF585D":"#FFB4B6", "#14E79D":"#C1F8E0", "#FFB71A":"#FFDF99", "#A5A5A5":"#D6D6D6"}, orient='index', columns = ["Color Ruta"]).reset_index().rename(columns = {"index":"Color Destino"})
    
    df_final = df.merge(concepto_color_df, left_on = "Destino", right_on = "Concepto", how = "left").rename(columns = {"Color":"Color Destino", "Concepto":"Concepto Destino"})
    df_final = df_final.merge(concepto_color_df, left_on = "Origen", right_on = "Concepto", how = "left").rename(columns = {"Color":"Color Origen", "Concepto":"Concepto Origen"})
    df_final = df_final.drop(columns = ["Concepto Origen", "Concepto Destino"])
    df_final['Color Origen'] = df_final['Color Origen'].fillna(df_final['Color Destino'])
    df_final['Color Destino'] = df_final['Color Destino'].fillna(df_final['Color Origen'])
    df_final = df_final.merge(ruta_color_df, on = "Color Destino", how = "left")
    df_final["Cantidad Actual"] = df_final["Cantidad Actual"].astype(int)
    df_final["Cantidad Pasada"] = df_final["Cantidad Pasada"].astype(int)
    
    df_final = df_final[["Origen", "Destino", "Cantidad Actual", "Cantidad Pasada", "Color Origen", "Color Ruta", "Color Destino"]]
    
    df_path_order_origen = df_final.groupby(by = "Origen").sum().reset_index()[["Origen", "Cantidad Actual"]].rename(columns = {"Origen":"Concepto", "Cantidad Actual":"Cantidad Origen"})
    df_path_order_destino = df_final.groupby(by = "Destino").sum().reset_index()[["Destino", "Cantidad Actual"]].rename(columns = {"Destino":"Concepto", "Cantidad Actual":"Cantidad Destino"})
    df_path_max= df_path_order_origen.merge(df_path_order_destino, on = "Concepto", how = "outer")
    df_path_max = df_path_max.fillna(0)
    df_path_max["Max"] = df_path_max[["Cantidad Origen", "Cantidad Destino"]].max(axis=1).astype(int)
    df_path_max = df_path_max[["Concepto", "Max"]]
    
    df_final["Cantidad Origen"] = df_final.merge(df_path_max, left_on = "Origen", right_on = "Concepto", how = "left")["Max"]
    df_final["Cantidad Destino"] = df_final.merge(df_path_max, left_on = "Destino", right_on = "Concepto", how = "left")["Max"]
    df_final["Min"] = df_final[["Cantidad Origen", "Cantidad Destino", "Cantidad Actual"]].min(axis=1).astype(int)
    df_final["Max"] = df_final[["Cantidad Origen", "Cantidad Destino", "Cantidad Actual"]].max(axis=1).astype(int)
    df_final = df_final.sort_values(by = ["Min", "Max", "Cantidad Origen", "Cantidad Destino", "Cantidad Actual"], ascending=[False, False, False, False, False]).reset_index().drop(columns = "index")

    #2. Generar Complementos de Tabla Original
    conceptos_origen_destino = []

    for i in range(len(df_final)):
        if df_final["Origen"][i] not in conceptos_origen_destino:
            conceptos_origen_destino.append(df_final["Origen"][i])
        
        if df_final["Destino"][i] not in conceptos_origen_destino:
            conceptos_origen_destino.append(df_final["Destino"][i])    

    #3. Tabla de Colores por Concepto de Sankey
    conceptos_origen_destino_df = pd.DataFrame(conceptos_origen_destino, columns = ["Concepto"])
    
    df_concept_origen_colors = df_final[["Origen", "Color Origen"]][df_final["Origen"].isin(conceptos_origen_destino)].drop_duplicates().rename(columns = {"Origen":"Concepto", "Color Origen":"Color"})
    df_concept_destino_colors = df_final[["Destino", "Color Destino"]][df_final["Destino"].isin(conceptos_origen_destino)].drop_duplicates().rename(columns = {"Destino":"Concepto", "Color Destino":"Color"})
    
    df_concept_colors = pd.concat([df_concept_origen_colors, df_concept_destino_colors]).drop_duplicates()
    df_concept_colors = conceptos_origen_destino_df.merge(df_concept_colors, on = "Concepto", how = "inner")

    
    try:
        # Using on Local
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1200')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                                  options=options)
        st.write(f"DEBUG:DRIVER:{driver}")
        driver.get(url)
        #time.sleep(5)
        #html_doc = driver.page_source
        #Website Zoom 67%
        fiscal_year_field = driver.find_element("xpath", "//input[@id='fiscal_year']")
        
        ActionChains(driver).click(fiscal_year_field).perform()
        ActionChains(driver).double_click(fiscal_year_field).perform()
        fiscal_year_field.send_keys("2024")
        
        #Type Values
        rows = 10
        top_rows = []
        for i in range(1,rows+1):
            top_rows.append("height: 40px; top: "+ str(i*40) +"px; width: 100%;")
        
        style_cell = ["width: 213.452px; left: 0px;", "width: 213.452px; left: 213.452px;","width: 177.876px; left: 426.903px;", "width: 177.876px; left: 604.78px;"]
        r_counter = 0
        
        r_counter = 0
        for r in top_rows:
            st.markdown("Completando: " + str(r_counter + 1) + " / " + str(len(top_rows)))
            cells = "//div[@class='dsg-row'][@style='"+ r +"']//div[@class='dsg-cell']//input[@class='dsg-input']"
            cells_fields = driver.find_elements("xpath", cells)
        
            c_counter = 0
            for c in cells_fields:
                ActionChains(driver).click(c).perform()
                ActionChains(driver).double_click(c).perform()
                #cell_field.clear()
                c.send_keys(df.iloc[r_counter,c_counter])
                c_counter += 1
                time.sleep(0.5)
            r_counter += 1
    
        
        #Fix Colors
        color_tab_field = driver.find_element("xpath", "//button[@id='tabs-:r3:--tab-1']")
        ActionChains(driver).click(color_tab_field).perform()
        
        #Color Nodes
        colors_rect =  driver.find_elements("tag name", "g")
        
        nodes = []
        for i in colors_rect:
            nodes.append(i.get_attribute('class'))
        counter = 0
        index_node = []
        for x in nodes:
            if x == "node":
                index_node.append(counter)
            counter += 1
        nodes_location = colors_rect[min(index_node):max(index_node)+1]
        order = pd.DataFrame(driver.find_element("xpath", "//div[@id = 'chart']").text.split("\n"), columns = ["Concepto"])
        df_concept_colors = order.merge(df_concept_colors, on = "Concepto", how = "left")
        df_concept_colors = df_concept_colors.dropna(axis='rows').reset_index().drop(columns = "index")
        
        for c in range(len(nodes_location)):
            element = nodes_location[c].find_element("tag name", "rect")
            driver.execute_script("arguments[0].setAttribute('fill', '" + df_concept_colors["Color"][c] + "')", element)
  

        #Color Paths
        colors_path =  driver.find_elements("tag name", "path")
        
        paths = []
        for i in colors_path:
            paths.append(i.get_attribute('stroke'))
        counter = 0
        index_paths = []
        for x in paths:
            if x is not None:
                index_paths.append(counter)
            counter += 1
        paths_location = colors_path[min(index_paths):max(index_paths)+1]
        
        for c in range(len(paths_location)):
            element = paths_location[c]
            driver.execute_script("arguments[0].setAttribute('stroke', '" + df_final["Color Ruta"][c] + "')", element)
        #Download Sankey
        file_field = driver.find_elements("xpath", "//button[@class='btn dropdown-toggle navbar-item btn-secondary']")
        #print(len(file_field))
        #print(file_field[0].text)
        ActionChains(driver).click(file_field[0]).perform()
        download_field = driver.find_element("xpath", "//a[@id='download_link_png']")
        sankey_url = download_field.get_attribute('href')

        st.markdown("Copia el URL del Sankey 👇: ")
        st.image(sankey_url, use_column_width = "always")
        Path = f'''{sankey_url}'''
        st.code(Path, language="python")
        #ActionChains(driver).click(download_field).perform()
        
        #st.markdown("Click al botón de descarga")

        driver.quit()

    #soup = BeautifulSoup(html_doc, "html.parser")
    except Exception as e:
        st.write(f"DEBUG:INIT_DRIVER:ERROR:{e}")

    finally:
        if driver is not None: 
            driver.quit()




# ---------------- Page & UI/UX Components ------------------------
def main_sidebar():
    # 1.Vertical Menu
    site_extraction_page()


def site_extraction_page():

    input_1, padding_A, input_2, padding_B, input_3 = st.columns([4,1,4,1,4])

    with input_1:
        #1. Lectura de Archivo
        st.markdown("<h2 style='text-align: left; color: #14E79D; font-weight: bolder;'>PASO ☝️</h2>"+"<p style='text-align: left; color: #5666FF; font-weight: bold;'>Descarga el archivo template en el que registrarás las cuentas del Sankey: </p>", unsafe_allow_html=True)
        #template_sankey_df = pd.DataFrame({'Origen': [""], 'Destino': [""], 'Cantidad Actual': [""], 'Cantidad Pasada': [""]})
        
        st.download_button(
            label = "Descargar template 📥",
            data = "Origen, Destino, Cantidad Actual, Cantidad Pasada",
            file_name = "Template_Sankey.csv",
            mime = "text/csv",
        )
        st.markdown("")
        
    with input_2:
        st.markdown("<h2 style='text-align: left; color: #14E79D; font-weight: bolder;'>PASO ✌</h2>"+"<p style='text-align: left; color: #5666FF; font-weight: bold;'>Sube el archivo con las cuentas: </p>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Inserta el Excel (.xlsx, .csv) aquí:", type=['csv'])
    
        if uploaded_file is not None:
                df = pd.read_csv(uploaded_file)
                df["Cantidad Actual"] = df["Cantidad Actual"].astype("string")
                df["Cantidad Pasada"] = df["Cantidad Pasada"].astype("string")
                st.write(df)

    with input_3:
            url = "https://www.sankeyart.com/sankeys/1426/"
            st.markdown("<h2 style='text-align: left; color: #14E79D; font-weight: bolder;'>PASO 👌</h2>"+"<p style='text-align: left; color: #5666FF; font-weight: bold;'>Genera el diagrama Sankey: </p>", unsafe_allow_html=True)

            clicked = st.button("Generar 🎋",type="primary")
            if clicked:
                with st.container(border=True):
                    with st.spinner("Loading page website..."):
                        content = get_website_content(url, df)




if __name__ == "__main__":
    main_sidebar()
