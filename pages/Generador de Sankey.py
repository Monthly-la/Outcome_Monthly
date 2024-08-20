import streamlit as st
import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
from bs4 import BeautifulSoup

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


def get_website_content(url, df, df_final, df_concept_colors):
    driver = None
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
        top_rows
        
        style_cell = ["width: 213.452px; left: 0px;", "width: 213.452px; left: 213.452px;","width: 177.876px; left: 426.903px;", "width: 177.876px; left: 604.78px;"]
        c_counter = -1
        for c in style_cell:
            c_counter += 1
            r_counter = 0
            for r in top_rows:
                cell = "//div[@class='dsg-row'][@style='"+ r +"']//div[@class='dsg-cell'][@style='"+ c +"']//input[@class='dsg-input']"
                cell_field = driver.find_elements("xpath", cell)[0]
                #cell_field = WebDriverWait(driver, 2).until(ec.element_to_be_clickable((By.CSS_SELECTOR, cell))).click()
                ActionChains(driver).click(cell_field).perform()
                ActionChains(driver).double_click(cell_field).perform()
                #cell_field.clear()
                cell_field.send_keys(df.iloc[r_counter,c_counter])
                r_counter += 1
                time.sleep(0.5)
        
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
        ActionChains(driver).click(download_field).perform()

        driver.quit()
        #soup = BeautifulSoup(html_doc, "html.parser")
        #return soup.get_text()
    except Exception as e:
        st.write(f"DEBUG:INIT_DRIVER:ERROR:{e}")
    finally:
        if driver is not None: driver.quit()
    return None




# ---------------- Page & UI/UX Components ------------------------
def main_sidebar():
    # 1.Vertical Menu
    st.header("Running Selenium on Streamlit Cloud")
    site_extraction_page()


def site_extraction_page():

    #1. Lectura de Archivo
    uploaded_file = st.file_uploader("Inserta el Excel (.xlsx, .csv) aquí:", type=['csv'])
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write(df)
        df["Cantidad Actual"] = df["Cantidad Actual"].astype("string")
        df["Cantidad Pasada"] = df["Cantidad Pasada"].astype("string")
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
    
        
        url = "https://www.sankeyart.com/sankeys/1426/"
        clicked = st.button("Load Page Content",type="primary")
        if clicked:
            with st.container(border=True):
                with st.spinner("Loading page website..."):
                    content = get_website_content(url, df, df_final, df_concept_colors)
                    #st.write(content)


if __name__ == "__main__":
    main_sidebar()
