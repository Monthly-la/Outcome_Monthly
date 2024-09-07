import streamlit as st
import pyexcel as p
import pandas as pd
from io import BytesIO


st.set_page_config(
    page_title="Monthly - App Interna",
    page_icon="💸",
    layout="wide"
)
primary_clr = st.get_option("theme.primaryColor")


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
    st.markdown("<h2 style='text-align: right; color: #5666FF;'>👨🏻‍💻 Feature Requests</h2>", unsafe_allow_html=True)

st.divider()

import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Function to send email
def send_email(subject, message, to_email):
    from_email = "checo@monthly.la"
    from_password = "Zoquete2"

    # Create message object
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    # Set up the SMTP server
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Secure the connection
        server.login(from_email, from_password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        return True
    except Exception as e:
        return False, str(e)


# Form fields
with st.form(key='contact_form'):
    name = st.text_input("Name")
    email = st.text_input("Email")
    subject = st.text_input("Subject")
    message = st.text_area("Message")

    submit_button = st.form_submit_button(label='Submit')

# After form submission
if submit_button:
    if name and email and subject and message:
        to_email = "checo@monthly.la"
        email_body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"

        # Send the email
        result = send_email(subject, email_body, to_email)

        if result == True:
            st.success("Your message has been sent successfully!")
        else:
            st.error(f"Failed to send message. Error: {result[1]}")
    else:
        st.error("Please fill in all fields.")


