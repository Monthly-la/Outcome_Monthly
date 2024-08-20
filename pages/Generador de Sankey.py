import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


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


# Function to initialize WebDriver
def init_driver():
    # Using ChromeDriverManager to handle WebDriver setup
    service = Service(ChromeDriverManager().install())
    
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Specify the correct path to the Chrome binary
    chrome_binary_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"  # Update this path if incorrect
    options.binary_location = chrome_binary_path
    
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# Streamlit app
st.title("Selenium with Streamlit and WebDriver Manager")

if st.button("Run Web Scraping"):
    st.write("Initializing WebDriver...")
    try:
        driver = init_driver()
        
        # Example of accessing a webpage
        driver.get("https://www.example.com")
        st.write("Accessed the website")
        
        # Example of finding an element
        heading = driver.find_element(By.TAG_NAME, "h1").text
        st.write("Heading found:", heading)
        
        # Close the driver
        driver.quit()
        st.write("WebDriver session closed.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

